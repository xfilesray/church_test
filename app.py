import streamlit as st
import pandas as pd
from datetime import datetime, time
from supabase import create_client, Client

def ts(codes):
    return bytes(codes).decode('utf-8')

# Titles & Config
st.set_page_config(
    page_title=ts([233, 153, 131, 230, 156, 131, 228, 186, 139, 229, 139, 153, 231, 174, 161, 231, 173, 134]),
    page_icon="⛪",
    layout="wide"
)

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

st.title("⛪ " + ts([233, 153, 131, 230, 156, 131, 228, 186, 139, 229, 139, 153, 231, 174, 161, 231, 173, 134]))
st.markdown("---")

# Safe Lists
roles_list = [ts([230, 149, 172, 229, 160, 156, 233, 155, 133]), ts([228, 184, 187, 230, 151, 165, 229, 173, 184]), ts([233, 159, 179, 230, 142, 167]), ts([230, 142, 165, 229, 1f3, 133]), ts([229, 133, 182, 228, 187, 150])]
groups_list = [ts([229, 164, 167, 232, 161, 155, 229, 176, 143, 231, 173, 134]), ts([230, 156, 131, 228, 187, 150])]
rooms_list = ["101", "201", "301", ts([229, 164, 167, 229, 133, 130]), ts([229, 133, 175, 229, 133, 130])]

st.sidebar.header("Form Input")
record_type = st.sidebar.radio("Select Type:", ["DIARY", "SCHEDULE", "ROOMS"])

with st.sidebar.form(key="f_main", clear_on_submit=False):
    s_date = st.date_input("Date", datetime.now())
    t_in = st.time_input("Time", time(9, 30))
    time_str = t_in.strftime("%H:%M")
    
    if record_type == "ROOMS":
        final_room = st.selectbox("Select Room", rooms_list)
        role = "ROOM_BORROW"
        final_group = st.selectbox("Select Group", groups_list)
        content = st.text_input("Usage Summary", placeholder="Meeting...")
        people = st.text_input("Contact Person", placeholder="Name")
        grace_notes = st.text_area("Notes", placeholder="Equipments...", height=100)
    else:
        final_room = ""
        role = st.selectbox("Select Role", roles_list)
        content = st.text_input("Content Summary", placeholder="Worship...")
        final_group = st.selectbox("Select Group", groups_list)
        people = st.text_input("Staff Name(s)", placeholder="John, Mary")
        grace_notes = st.text_area("Grace Notes / Memo", placeholder="Write here...", height=150)
        
    submit_button = st.form_submit_button(label="Save to Cloud")

try:
    response = supabase.table("service_records").select("service_date, service_time, role, content, group_name, people, grace_notes, record_type, room_name").order("service_date", desc=False).execute()
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"Read Error: {e}")
    df_raw = pd.DataFrame()

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

def save_to_supabase(d_str, t_str, r_str, c_str, g_str, p_str, n_str, type_str, rm_str):
    insert_data = {
        "service_date": d_str, "service_time": t_str, "role": r_str, "content": c_str,
        "group_name": g_str, "people": p_str, "grace_notes": n_str, "record_type": type_str, "room_name": rm_str
    }
    try:
        supabase.table("service_records").insert(insert_data).execute()
        st.success("🎉 Data successfully saved!")
        st.session_state.clear()
        import time as t_mod
        t_mod.sleep(1.0)
        st.rerun()
    except Exception as save_err:
        st.error(f"Save failed: {save_err}")

if submit_button:
    date_str = s_date.strftime("%Y-%m-%d")
    conflict_detected = False
    conflict_msg = []
    
    if not df_raw.empty:
        if record_type == "SCHEDULE":
            same_time_role = df_raw[(df_raw["service_date"] == date_str) & (df_raw["service_time"] == time_str) & (df_raw["role"] == role) & (df_raw["record_type"] == "SCHEDULE")]
            if not same_time_role.empty:
                conflict_detected = True
                conflict_msg.append(f"Conflict: Role repeating on {date_str} {time_str}")
            
            if people.strip():
                input_names = [n.strip() for n in people.replace(",", ",").split(",") if n.strip()]
                day_time_records = df_raw[(df_raw["service_date"] == date_str) & (df_raw["service_time"] == time_str) & (df_raw["record_type"] == "SCHEDULE")]
                for name in input_names:
                    for idx, row in day_time_records.iterrows():
                        if name in row["people"]:
                            conflict_detected = True
                            conflict_msg.append(f"Conflict: Staff [{name}] is busy on {date_str} {time_str}")
        
        elif record_type == "ROOMS":
            same_room_time = df_raw[(df_raw["service_date"] == date_str) & (df_raw["service_time"] == time_str) & (df_raw["room_name"] == final_room) & (df_raw["record_type"] == "ROOMS")]
            if not same_room_time.empty:
                conflict_detected = True
                conflict_msg.append(f"Conflict: Room [{final_room}] already booked on {date_str} {time_str}")

    if conflict_detected:
        st.session_state["c_m"] = conflict_msg
        st.session_state["p_d"] = (date_str, time_str, role, content, final_group, people, grace_notes, record_type, final_room)
    else:
        save_to_supabase(date_str, time_str, role, content, final_group, people, grace_notes, record_type, final_room)

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
            st.session_state.clear()
            st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["📅 SCHEDULE TIME", "🏠 ROOM STATUS", "📜 GRACE NOTES"])

today_str = datetime.now().strftime("%Y-%m-%d")

with tab1:
    st.subheader("🗓️ Service Schedule")
    if df_raw.empty:
        st.info("No data.")
    else:
        df_s = df_raw[(df_raw["record_type"] == "SCHEDULE") & (df_raw["service_date"] >= today_str)].copy().sort_values(by=["service_date", "service_time"])
        q_s = st.text_input("Search Schedule:", placeholder="Type keywords...")
        if q_s:
            df_s = df_s[df_s["service_date"].str.contains(q_s, case=False) | df_s["role"].str.contains(q_s, case=False) | df_s["people"].str.contains(q_s, case=False)]
        
        df_s_disp = df_s.rename(columns={"service_date": "Date", "service_time": "Time", "role": "Role", "group_name": "Group", "content": "Session", "people": "Staff", "grace_notes": "Memo"})
        st.dataframe(df_s_disp[["Date", "Time", "Role", "Group", "Session", "Staff", "Memo"]], use_container_width=True)

with tab2:
    st.subheader("📋 Church Room Reservations")
    if df_raw.empty:
        st.info("No data.")
    else:
        df_r = df_raw[(df_raw["record_type"] == "ROOMS") & (df_raw["service_date"] >= today_str)].copy().sort_values(by=["service_date", "service_time"])
        q_r = st.text_input("Search Rooms:", placeholder="Type keywords...")
        if q_r:
            df_r = df_r[df_r["service_date"].str.contains(q_r, case=False) | df_r["room_name"].str.contains(q_r, case=False) | df_r["group_name"].str.contains(q_r, case=False)]
        
        df_r_disp = df_r.rename(columns={"service_date": "Date", "service_time": "Time", "room_name": "Room", "group_name": "Group", "content": "Purpose", "people": "Contact", "grace_notes": "Memo"})
        st.dataframe(df_r_disp[["Date", "Time", "Room", "Group", "Purpose", "Contact", "Memo"]], use_container_width=True)

with tab3:
    st.subheader("🔍 Search Grace Diary")
    if df_raw.empty:
        st.info("No data.")
    else:
        df_g = df_raw[df_raw["record_type"] == "DIARY"].copy().sort_values(by="service_date", ascending=False)
        q_g = st.text_input("Universal Search Diary:", placeholder="Type keywords...")
        if q_g:
            df_g = df_g[df_g["service_date"].str.contains(q_g, case=False) | df_g["grace_notes"].str.contains(q_g, case=False) | df_g["people"].str.contains(q_g, case=False)]
        
        df_g_disp = df_g.rename(columns={"service_date": "Date", "service_time": "Time", "role": "Role", "group_name": "Group", "content": "Summary", "people": "Companion", "grace_notes": "Notes"})
        st.dataframe(df_g_disp[["Date", "Time", "Role", "Group", "Summary", "Companion", "Notes"]], use_container_width=True)
        st.markdown("---")
        
        selected_key = st.selectbox("Select row to view diary:", df_g_disp.index, format_func=lambda x: f"{df_g_disp.loc[x, 'Date']} - {df_g_disp.loc[x, 'Role']}")
        if selected_key is not None:
            f_row = df_g_disp.loc[selected_key]
            st.info(f"INFO: {f_row['Date']} {f_row['Time']} | {f_row['Role']} | {f_row['Group']}")
            st.write(f"People: {f_row['Companion']}")
            st.write(f"Summary: {f_row['Summary']}")
            st.success(str(f_row['Notes']))
