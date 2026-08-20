import streamlit as st
import pandas as pd
from datetime import datetime, time
from supabase import create_client, Client
import base64

def dec(b_str):
    return base64.b64decode(b_str.encode('utf-8')).decode('utf-8')

st.set_page_config(
    page_title=dec("5pWZ5pyD5LqL5aWp44CB6ZW35Zyw6IiH5oGp5YW4566h55CG57O757Wx"),
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
    st.error("⚠️ SUPABASE_URL / SUPABASE_KEY missing in Secrets!")
    st.stop()

st.title("⛪ " + dec("5pWZ5pyD5LqL5aWp44CB6ZW35Zyw6IiH5oGp5YW4566h55CG57O757Wx"))
st.markdown("---")

roles_list = [dec("5pWs5p6w6ZqKL+WPuCDjgpQ="), dec("5Li75pel5a24L+WKqeWZgA=="), dec("6Z+z5o6nL+ebtOaSreL+WKleW9seWniw=="), dec("5o6l5b6FL+WPuOS6iy/lu3 some things"), dec("5bI+6ZW3L+eJp+WKnS/lsI7mpaM="), dec("6Zec6fCAL+aOoueovS/mlrDmnIvlj4vigoU="), dec("5Li75pBRL+領omg="), dec("5p6j5pWZL+WkluaVlg=="), dec("5YW25LuW")]
roles_list[3] = dec("5o6l5b6FL+WPuOS6iy/lu30w")
roles_list_real = [dec("5pWs5p6w6ZqKL+WPu琴"), dec("5Li75pel5a24L+WKqeWZgA=="), dec("6Z+z5o6nL+ebtOaSreL+WKleW9seWniw=="), dec("5o6l5b6FL+WPuOS6iy/lu30="), dec("5bI+6ZW3L+eJp+WKnS/lsI7mpaM="), dec("6Zec6fCAL+aOoueovS/mlrDmnIvlj4vigoU="), dec("5Li75pBRL+m領omg="), dec("5p6j5pWZL+WkluaVlg=="), dec("5YW25LuW")]
groups_list = [dec("5aSn6KGb5bI+"), dec("57SE5pu45Lqe6Z2S5bm05ZyY"), dec("6迦5bI+6ZW36Z2S"), dec("5Zac5qiC5a625b庭"), dec("5p6p5b6X6fCFLbI="), dec("5YW25LuWIC8g6KuL6Ieq6KGM5re75Yqg")]

try:
    res = supabase.table("service_records").select("service_date, service_time, role, content, group_name, people, grace_notes, record_type, room_name").order("service_date", desc=False).execute()
    df_raw = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Database error: {e}")
    df_raw = pd.DataFrame()

if not df_raw.empty:
    df_raw["record_type"] = df_raw["record_type"].fillna("恩典日記").astype(str)
    df_raw["service_date"] = df_raw["service_date"].fillna("").astype(str)
    df_raw["service_time"] = df_raw["service_time"].fillna("00:00").astype(str)
    df_raw["role"] = df_raw["role"].fillna("").astype(str)
    df_raw["group_name"] = df_raw["group_name"].fillna("").astype(str)
    df_raw["people"] = df_raw["people"].fillna("").astype(str)
    df_raw["content"] = df_raw["content"].fillna("").astype(str)
    df_raw["grace_notes"] = df_raw["grace_notes"].fillna("").astype(str)
    df_raw["room_name"] = df_raw["room_name"].fillna("").astype(str)

today_str = datetime.now().strftime("%Y-%m-%d")

st.sidebar.header(dec("4pyoIOiom記録5paw6LOH5paZ"))
r_type_sel = st.sidebar.radio(dec("6KuL6YG45p9Y6Ly45YWl6aGe5Z6LDQo="), ["G_DIARY", "S_PLAN", "R_BORROW"])

with st.sidebar.form(key="f_main", clear_on_submit=False):
    s_date = st.date_input(dec("5L9Y55So5pel5pyf"), datetime.now())
    t_in = st.time_input(dec("6ZaL5aeL5pmC6ZaT"), time(9, 30))
    t_str = t_in.strftime("%H:%M")
    
    if r_type_sel == "R_BORROW":
        f_room = st.text_input(dec("6Yg45p6p6IiH6Ly45YWl5oi/6ZaT5ZCN56ix"), "101")
        role_val = "場地借用"
        f_group = st.text_input(dec("5Y借55So5bI+6Z2S"), "David")
        f_content = st.text_input(dec("5Y借55So55So6YCU5p6p6KaB"), "Meeting")
        f_people = st.text_input(dec("6ZOf6LOg6Y借55So5ZCM5bel"), "User")
        f_notes = st.text_area(dec("6Y借55So6備6Ki7"), "", height=100)
    else:
        f_room = ""
        role_val = st.selectbox(dec("5LqL5aWp5b岗5L9Y"), roles_list_real)
        f_content = st.text_input(dec("5pyN5L9Y5pmC6Z615oi05YWn5a655p6p6KaB"), "")
        f_group = st.text_input(dec("6YG45p6p5bI+6Z2S56ix56ix"), "David")
        f_people = st.text_input(dec("5LqL5aWp5Lq65ZOhIC8g5ZCM6KGM5ZCM5bel"), "")
        f_notes = st.text_area(dec("5oSf5YuV6IiH6auU5pyD6Ki76YCB"), "", height=150)
        
    sub_b = st.form_submit_button(dec("5YS儲5a2Y6Iez6Zuy6duv"))

def save_data(d, t, r, c, g, p, n, ty, rm):
    try:
        supabase.table("service_records").insert({"service_date":d,"service_time":t,"role":r,"content":c,"group_name":g,"people":p,"grace_notes":n,"record_type":ty,"room_name":rm}).execute()
        st.success("SAVED SUCCESS!")
        st.session_state.clear()
        import time as tm
        tm.sleep(1.0)
        st.rerun()
    except Exception as err:
        st.error(f"Save failed: {err}")

if sub_b:
    d_str = s_date.strftime("%Y-%m-%d")
    db_ty = "恩典日記" if r_type_sel == "G_DIARY" else ("事奉排班" if r_type_sel == "S_PLAN" else "場地借用")
    
    warn_flag = False
    w_msg = []
    
    if not df_raw.empty:
        if db_ty == "事奉排班":
            chk1 = df_raw[(df_raw["service_date"]==d_str) & (df_raw["service_time"]==t_str) & (df_raw["role"]==role_val) & (df_raw["record_type"]=="事奉排班")]
            if not chk1.empty:
                warn_flag = True
                w_msg.append(f"CONFLICT: ROLE TAKEN AT {d_str} {t_str}")
            if f_people.strip():
                p_arr = [x.strip() for x in f_people.replace("，",",").split(",") if x.strip()]
                chk2 = df_raw[(df_raw["service_date"]==d_str) & (df_raw["service_time"]==t_str) & (df_raw["record_type"]=="事奉排班")]
                for nm in p_arr:
                    for idx, row in chk2.iterrows():
                        if nm in row["people"]:
                            warn_flag = True
                            w_msg.append(f"CONFLICT: USER {nm} BUSY AT {d_str} {t_str}")
        elif db_ty == "場地借用":
            chk3 = df_raw[(df_raw["service_date"]==d_str) & (df_raw["service_time"]==t_str) & (df_raw["room_name"]==f_room) & (df_raw["record_type"]=="場地借用")]
            if not chk3.empty:
                warn_flag = True
                w_msg.append(f"CONFLICT: ROOM {f_room} OCCUPIED AT {d_str} {t_str}")

    if warn_flag:
        st.session_state["w"] = w_msg
        st.session_state["p"] = (d_str, t_str, role_val, f_content, f_group, f_people, f_notes, db_ty, f_room)
    else:
        save_data(d_str, t_str, role_val, f_content, f_group, f_people, f_notes, db_ty, f_room)

if "w" in st.session_state:
    st.error("🚨 DUPLICATE DETECTED:")
    for m in st.session_state["w"]:
        st.warning(m)
    c_ok, c_no = st.columns(2)
    with c_ok:
        if st.button("FORCE SAVE", type="primary"):
            pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8, pd9 = st.session_state["p"]
            save_data(pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8, pd9)
    with c_no:
        if st.button("CANCEL"):
            st.session_state.clear()
            st.rerun()

t_a, t_b, t_c = st.tabs(["S_SCHEDULE", "R_STATUS", "G_NOTES"])

with t_a:
    st.subheader(dec("7p6m5pyf5Y+K5pyf5L6G5LqL5aWp5o6S54re"))
    if df_raw.empty:
        st.info("No data.")
    else:
        df_s = df_raw[(df_raw["record_type"] == "事奉排班") & (df_raw["service_date"] >= today_str)].copy().sort_values(by=["service_date", "service_time"])
        q_s = st.text_input("Search Schedule:", placeholder="Type to filter...")
        if q_s:
            df_s = df_s[df_s["service_date"].str.contains(q_s,case=False)|df_s["service_time"].str.contains(q_s,case=False)|df_s["role"].str.contains(q_s,case=False)|df_s["people"].str.contains(q_s,case=False)]
        st.dataframe(df_s, use_container_width=True)

with t_b:
    st.subheader(dec("6Yg45p6p6IiH6Ly45YWl5oi/6ZaT5ZCN56ix"))
    if df_raw.empty:
        st.info("No data.")
    else:
        df_r = df_raw[(df_raw["record_type"] == "場地借用") & (df_raw["service_date"] >= today_str)].copy().sort_values(by=["service_date", "service_time"])
        q_r = st.text_input("Search Rooms:", placeholder="Type to filter...")
        if q_r:
            df_r = df_r[df_r["service_date"].str.contains(q_r,case=False)|df_r["room_name"].str.contains(q_r,case=False)|df_r["group_name"].str.contains(q_r,case=False)]
        st.dataframe(df_r, use_container_width=True)

with t_c:
    st.subheader(dec("6Zyy566X6IiH6bOl6ecv5byP5oGp5YW46Ki76YCB"))
    if df_raw.empty:
        st.info("No data.")
    else:
        df_g = df_raw[df_raw["record_type"] == "恩典日記"].copy().sort_values(by=["service_date", "service_time"], ascending=False)
        q_g = st.text_input("Search Grace Notes:", placeholder="Type to filter...")
        if q_g:
            df_g = df_g[df_g["service_date"].str.contains(q_g,case=False)|df_g["grace_notes"].str.contains(q_g,case=False)|df_g["people"].str.contains(q_g,case=False)]
        st.dataframe(df_g, use_container_width=True)
        st.markdown("---")
        idx_sel = st.selectbox("Select row to view detail:", df_g.index)
        if idx_sel is not None:
            f_r = df_g.loc[idx_sel]
            st.info(f"DATE: {f_r['service_date']} {f_r['service_time']} | ROLE: {f_r['role']} | GROUP: {f_r['group_name']}")
            st.write(f"PEOPLE: {f_r['people']}")
            st.write(f"SUMMARY: {f_r['content']}")
            st.info(str(f_r['grace_notes']))
