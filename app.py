import constants as c
from datetime import datetime, time
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# Page Config
st.set_page_config(page_title=c.PAGE_TITLE, page_icon="⛪", layout="wide")

# Supabase Initialization
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    @st.cache_resource
    def get_supabase_client() -> Client:
        return create_client(SUPABASE_URL, SUPABASE_KEY)

    supabase = get_supabase_client()
else:
    st.error("Missing Secrets keys.")
    st.stop()

# Initialize Active Tab State
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = c.TABS[0]

st.title(c.MAIN_TITLE)
st.markdown("---")

# Sidebar - Form Setup
st.sidebar.header("Form Input")

selected_type_key = st.sidebar.radio(
    "Select Type:",
    c.RECORD_TYPE_KEYS,
    format_func=lambda x: c.RECORD_TYPE_MAP[x],
)

with st.sidebar.form(key="f_main", clear_on_submit=False):
    s_date = st.date_input("Date", datetime.now())
    t_in = st.time_input("Time", time(9, 30))
    time_str = t_in.strftime("%H:%M")

    # Common Field: Group Selection
    sel_group = st.selectbox("Select Group", c.GROUPS)
    if sel_group == c.OTHER_CUSTOM_TRIGGER:
        final_group = st.text_input(
            "Custom Group Name", placeholder="Enter group name..."
        )
    else:
        final_group = sel_group

    if selected_type_key == "ROOMS":
        sel_room = st.selectbox("Select Room", c.ROOMS)
        if sel_room == c.OTHER_CUSTOM_TRIGGER:
            final_room = st.text_input(
                "Custom Room Name", placeholder="Enter room name..."
            )
        else:
            final_room = sel_room

        role = "場地借用"
        content = st.text_input(
            "Usage Summary", placeholder="e.g. Youth Choir Practice"
        )
        people = st.text_input("Contact Person", placeholder="e.g. John Doe")
        grace_notes = st.text_area(
            "Notes", placeholder="Equipments / Memos...", height=100
        )

    else:
        final_room = ""
        sel_role = st.selectbox("Select Role", c.ROLES)
        if sel_role == c.OTHER_CUSTOM_TRIGGER:
            role = st.text_input(
                "Custom Role Name", placeholder="Enter role name..."
            )
        else:
            role = sel_role

        content = st.text_input(
            "Content Summary", placeholder="e.g. Sunday Worship"
        )
        people = st.text_input(
            "Staff Name(s)", placeholder="e.g. Mary, Peter (Comma separated)"
        )
        grace_notes = st.text_area(
            "Grace Notes / Memo", placeholder="Write here...", height=150
        )

    submit_button = st.form_submit_button(label="Save to Cloud")

# Fetch Cloud Data
try:
    response = (
        supabase.table("service_records")
        .select(
            "service_date, service_time, role, content, group_name, people, grace_notes, record_type, room_name"
        )
        .order("service_date", desc=False)
        .execute()
    )
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"Read Error: {e}")
    df_raw = pd.DataFrame()

# Clean Dataframe
if not df_raw.empty:
    df_raw["record_type"] = df_raw["record_type"].fillna("DIARY").astype(str)
    df_raw["service_date"] = df_raw["service_date"].fillna("").astype(str)
    df_raw["service_time"] = df_raw["service_time"].fillna("00:00").astype(str)
    df_raw["role"] = df_raw["role"].fillna("").astype(str)
    df_raw["group_name"] = df_raw["group_name"].fillna("").astype(str)
    df_raw["people"] = df_raw["people"].fillna("").astype(str)
    df_raw["content"] = df_raw["content"].fillna("").astype(str)
    df_raw["grace_notes"] = df_raw["grace_notes"].fillna("").astype(str)
    df_raw["room_name"] = df_raw["room_name"].fillna("").astype(str)


def save_to_supabase(
    d_str, t_str, r_str, c_str, g_str, p_str, n_str, type_str, rm_str
):
    insert_data = {
        "service_date": d_str,
        "service_time": t_str,
        "role": r_str,
        "content": c_str,
        "group_name": g_str,
        "people": p_str,
        "grace_notes": n_str,
        "record_type": type_str,
        "room_name": rm_str,
    }
    try:
        supabase.table("service_records").insert(insert_data).execute()
        st.success("🎉 Data successfully saved!")

        # Dynamic Tab Switching based on saved type
        if type_str == "SCHEDULE":
            st.session_state["active_tab"] = c.TABS[0]
        elif type_str == "ROOMS":
            st.session_state["active_tab"] = c.TABS[1]
        else:
            st.session_state["active_tab"] = c.TABS[2]

        st.session_state.pop("c_m", None)
        st.session_state.pop("p_d", None)

        import time as t_mod

        t_mod.sleep(0.8)
        st.rerun()
    except Exception as save_err:
        st.error(f"Save failed: {save_err}")


# Strict Duplicate & Conflict Checking Logic
if submit_button:
    date_str = s_date.strftime("%Y-%m-%d")
    conflict_detected = False
    conflict_msg = []

    if not df_raw.empty:
        # 1. Room Conflict Check
        if final_room.strip():
            same_room_time = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
                & (df_raw["room_name"] == final_room.strip())
            ]
            if not same_room_time.empty:
                conflict_detected = True
                conflict_msg.append(
                    f"Conflict: Room [{final_room.strip()}] is already booked on {date_str} {time_str}"
                )

        # 2. Staff Conflict Check
        if people.strip():
            input_names = [
                n.strip()
                for n in people.replace("，", ",").split(",")
                if n.strip()
            ]
            day_time_records = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
            ]
            for name in input_names:
                for idx, row in day_time_records.iterrows():
                    existing_people = [
                        p.strip()
                        for p in str(row["people"]).replace("，", ",").split(",")
                        if p.strip()
                    ]
                    if name in existing_people:
                        conflict_detected = True
                        conflict_msg.append(
                            f"Conflict: Staff [{name}] is already assigned/booked on {date_str} {time_str}"
                        )

        # 3. Role Conflict Check
        if selected_type_key == "SCHEDULE" and role.strip():
            same_time_role = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
                & (df_raw["role"] == role.strip())
                & (df_raw["record_type"] == "SCHEDULE")
            ]
            if not same_time_role.empty:
                conflict_detected = True
                conflict_msg.append(
                    f"Conflict: Role [{role.strip()}] is already assigned on {date_str} {time_str}"
                )

    if conflict_detected:
        st.session_state["c_m"] = conflict_msg
        st.session_state["p_d"] = (
            date_str,
            time_str,
            role,
            content,
            final_group,
            people,
            grace_notes,
            selected_type_key,
            final_room,
        )
    else:
        save_to_supabase(
            date_str,
            time_str,
            role,
            content,
            final_group,
            people,
            grace_notes,
            selected_type_key,
            final_room,
        )

# Handle Conflict Modal / Alert Prompt
if "c_m" in st.session_state:
    st.error("🚨 Booking Conflict Detected:")
    for msg in st.session_state["c_m"]:
        st.warning(msg)
    col_ok, col_no = st.columns(2)
    with col_ok:
        if st.button("Force Save", type="primary"):
            p1, p2, p3, p4, p5, p6, p7, p8, p9 = st.session_state["p_d"]
            save_to_supabase(p1, p2, p3, p4, p5, p6, p7, p8, p9)
    with col_no:
        if st.button("Cancel"):
            st.session_state.pop("c_m", None)
            st.session_state.pop("p_d", None)
            st.rerun()

# Main Display Controlled Tabs
selected_tab = st.radio(
    "",
    options=c.TABS,
    index=c.TABS.index(st.session_state.get("active_tab", c.TABS[0])),
    key="tab_selector",
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state["active_tab"] = selected_tab
st.markdown("---")

today_str = datetime.now().strftime("%Y-%m-%d")

# TAB 1: SCHEDULE
if selected_tab == c.TABS[0]:
    st.subheader(c.TABS[0])
    if df_raw.empty:
        st.info("No data available.")
    else:
        df_s = (
            df_raw[
                (df_raw["record_type"] == "SCHEDULE")
                & (df_raw["service_date"] >= today_str)
            ]
            .copy()
            .sort_values(by=["service_date", "service_time"])
        )
        q_s = st.text_input("Search Schedule:", placeholder="Type keywords...")
        if q_s:
            df_s = df_s[
                df_s["service_date"].str.contains(q_s, case=False)
                | df_s["role"].str.contains(q_s, case=False)
                | df_s["people"].str.contains(q_s, case=False)
            ]

        df_s_disp = df_s.rename(columns=c.DF_COL_MAP_SCHEDULE)
        st.dataframe(
            df_s_disp[list(c.DF_COL_MAP_SCHEDULE.values())],
            use_container_width=True,
        )

# TAB 2: ROOMS
elif selected_tab == c.TABS[1]:
    st.subheader(c.TABS[1])
    if df_raw.empty:
        st.info("No data available.")
    else:
        df_r = (
            df_raw[
                (df_raw["record_type"] == "ROOMS")
                & (df_raw["service_date"] >= today_str)
            ]
            .copy()
            .sort_values(by=["service_date", "service_time"])
        )
        q_r = st.text_input("Search Rooms:", placeholder="Type keywords...")
        if q_r:
            df_r = df_r[
                df_r["service_date"].str.contains(q_r, case=False)
                | df_r["room_name"].str.contains(q_r, case=False)
                | df_r["group_name"].str.contains(q_r, case=False)
            ]

        df_r_disp = df_r.rename(columns=c.DF_COL_MAP_ROOMS)
        st.dataframe(
            df_r_disp[list(c.DF_COL_MAP_ROOMS.values())],
            use_container_width=True,
        )

# TAB 3: DIARY
elif selected_tab == c.TABS[2]:
    st.subheader(c.TABS[2])
    if df_raw.empty:
        st.info("No data available.")
    else:
        df_g = (
            df_raw[df_raw["record_type"] == "DIARY"]
            .copy()
            .sort_values(by="service_date", ascending=False)
        )
        q_g = st.text_input(
            "Universal Search Diary:", placeholder="Type keywords..."
        )
        if q_g:
            df_g = df_g[
                df_g["service_date"].str.contains(q_g, case=False)
                | df_g["grace_notes"].str.contains(q_g, case=False)
                | df_g["people"].str.contains(q_g, case=False)
            ]

        df_g_disp = df_g.rename(columns=c.DF_COL_MAP_DIARY)
        st.dataframe(
            df_g_disp[list(c.DF_COL_MAP_DIARY.values())],
            use_container_width=True,
        )
        st.markdown("---")

        if not df_g_disp.empty:
            selected_key = st.selectbox(
                "Select record to view detail:",
                df_g_disp.index,
                format_func=lambda x: f"{df_g_disp.loc[x, '日期']} - {df_g_disp.loc[x, '崗位']}",
            )
            if selected_key is not None:
                f_row = df_g_disp.loc[selected_key]
                st.info(
                    f"Details: {f_row['日期']} {f_row['時間']} | {f_row['崗位']} | {f_row['所屬小組']}"
                )
                st.write(f"Companions: {f_row['同行同工']}")
                st.write(f"Summary: {f_row['摘要']}")
                st.success(str(f_row["恩典體會"]))
