# ==============================================================================
# File: app.py
# Description: Streamlit Frontend Interface. All UI strings are loaded from constants.py.
# ==============================================================================
import datetime
import pandas as pd
import streamlit as st

import constants as c
import database as db

# 設定頁面配置
st.set_page_config(
    page_title=c.LABELS["app_title"],
    page_icon="⛪",
    layout="wide"
)

st.title(c.LABELS["app_title"])
st.caption(c.LABELS["app_caption"])

# 建立四大核心模組 Tabs (變數名稱維持純英文)
tab_grace, tab_venue, tab_roster, tab_search = st.tabs([
    c.LABELS["tab_grace"],
    c.LABELS["tab_venue"],
    c.LABELS["tab_roster"],
    c.LABELS["tab_search"]
])

# ------------------------------------------------------------------------------
# Module A: Grace Logs
# ------------------------------------------------------------------------------
with tab_grace:
    st.header(c.LABELS["grace_header"])
    
    # 動態取得同工選單
    active_workers = db.fetch_church_workers()
    
    with st.form("form_grace_record"):
        col1, col2 = st.columns(2)
        with col1:
            worker_name = st.selectbox(c.LABELS["grace_worker_name"], options=active_workers if active_workers else ["無資料"])
        with col2:
            ministry_item = st.text_input(c.LABELS["grace_ministry_item"], placeholder="例如: 敬拜讚美 / 主日學")
            
        reflection = st.text_area(c.LABELS["grace_reflection"], height=120)
        prayer_request = st.text_area(c.LABELS["grace_prayer_request"], height=80)
        
        submit_grace = st.form_submit_button(c.LABELS["btn_save_grace"])
        
        if submit_grace:
            if not reflection.strip():
                st.error("請填寫恩典與心得分享！")
            else:
                success = db.insert_grace_record(worker_name, ministry_item, reflection, prayer_request)
                if success:
                    st.success(c.LABELS["grace_save_success"])
                else:
                    st.error("儲存失敗，請檢查資料庫連線。")


# ------------------------------------------------------------------------------
# Module B: Venue Booking
# ------------------------------------------------------------------------------
with tab_venue:
    st.header(c.LABELS["venue_header"])
    
    with st.form("form_venue_booking"):
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            venue_name = st.selectbox(c.LABELS["venue_name"], options=c.OPTIONS["venues"])
        with col_b2:
            applicant_name = st.text_input(c.LABELS["venue_applicant"], placeholder="例如: 青年團契 / 張同工")
        with col_b3:
            purpose = st.text_input(c.LABELS["venue_purpose"], placeholder="例如: 團契彩排 / 敬拜預備")
            
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            booking_date = st.date_input(c.LABELS["venue_booking_date"], value=datetime.date.today())
        with col_t2:
            start_time = st.time_input(c.LABELS["venue_start_time"], value=datetime.time(14, 0))
        with col_t3:
            end_time = st.time_input(c.LABELS["venue_end_time"], value=datetime.time(16, 0))
            
        notes = st.text_input(c.LABELS["venue_notes"])
        force_save_venue = st.checkbox(c.LABELS["force_save_venue"])
        
        submit_venue = st.form_submit_button(c.LABELS["btn_save_venue"])
        
        if submit_venue:
            if start_time >= end_time:
                st.error(c.LABELS["venue_time_error"])
            else:
                # 衝突檢查
                has_conflict = db.check_venue_conflict(venue_name, booking_date, start_time, end_time)
                
                if has_conflict and not force_save_venue:
                    st.warning(c.LABELS["venue_conflict_warning"])
                else:
                    success = db.insert_venue_booking(venue_name, applicant_name, purpose, booking_date, start_time, end_time, notes)
                    if success:
                        st.success(c.LABELS["venue_save_success"])
                    else:
                        st.error("儲存場地預約失敗。")


# ------------------------------------------------------------------------------
# Module C: Ministry Roster
# ------------------------------------------------------------------------------
with tab_roster:
    st.header(c.LABELS["roster_header"])
    
    active_workers = db.fetch_church_workers()
    
    with st.form("form_ministry_roster"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            service_date = st.date_input(c.LABELS["roster_service_date"], value=datetime.date.today())
        with col_r2:
            service_type = st.selectbox(c.LABELS["roster_service_type"], options=c.OPTIONS["service_types"])
            
        st.subheader("👥 指派事奉崗位")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            worship_leaders = st.multiselect(c.LABELS["roster_worship_leader"], options=active_workers)
            speakers = st.multiselect(c.LABELS["roster_speaker"], options=active_workers)
            sound_avs = st.multiselect(c.LABELS["roster_sound_av"], options=active_workers)
        with col_g2:
            ushers = st.multiselect(c.LABELS["roster_usher"], options=active_workers)
            sunday_schools = st.multiselect(c.LABELS["roster_sunday_school"], options=active_workers)
            other_roles = st.multiselect(c.LABELS["roster_other_roles"], options=active_workers)
            
        custom_workers_raw = st.text_input(c.LABELS["custom_worker_input"])
        notes = st.text_input(c.LABELS["roster_notes"])
        force_save_roster = st.checkbox(c.LABELS["force_save_roster"])
        
        submit_roster = st.form_submit_button(c.LABELS["btn_save_roster"])
        
        if submit_roster:
            # 1. 解析並寫入自訂新同工
            new_workers = db.parse_workers_string(custom_workers_raw)
            for nw in new_workers:
                db.add_church_worker(nw)
                
            # 2. 彙整崗位資料
            roles_map = {
                "worship_leader": worship_leaders,
                "speaker": speakers,
                "sound_av": sound_avs,
                "usher": ushers,
                "sunday_school": sunday_schools,
                "other_roles": other_roles + new_workers
            }
            
            # 3. 執行智慧衝突檢測
            self_conflicts, db_conflicts = db.check_roster_conflicts(service_date, roles_map)
            
            # 4. 判斷是否阻擋儲存
            if (self_conflicts or db_conflicts) and not force_save_roster:
                if self_conflicts:
                    st.warning(c.LABELS["roster_self_conflict"].format(workers=", ".join(self_conflicts)))
                if db_conflicts:
                    st.warning(c.LABELS["roster_db_conflict"].format(workers=", ".join(db_conflicts), date=service_date.isoformat()))
            else:
                # 轉換 List 為逗號字串寫入資料庫
                db_roles_payload = {k: ", ".join(v) for k, v in roles_map.items()}
                success = db.insert_roster_schedule(service_date, service_type, db_roles_payload, notes, force_save_roster)
                if success:
                    st.success(c.LABELS["roster_save_success"])
                else:
                    st.error("儲存排班失敗。")


# ------------------------------------------------------------------------------
# Module D: Search & Management
# ------------------------------------------------------------------------------
with tab_search:
    st.header(c.LABELS["search_header"])
    
    subtab_query, subtab_worker_mgmt = st.tabs([
        c.LABELS["subtab_query"],
        c.LABELS["subtab_worker_mgmt"]
    ])
    
    # ── 子頁籤 1: 紀錄查詢 ──
    with subtab_query:
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_keyword = st.text_input(c.LABELS["search_query_label"], placeholder="輸入同工姓名、場地名稱或關鍵字...")
        with col_s2:
            module_filter = st.selectbox(c.LABELS["search_module_filter"], options=c.OPTIONS["search_modules"])
            
        if search_keyword:
            results = db.search_all_records(search_keyword, module_filter)
            has_data = False
            
            if results.get("grace_records"):
                has_data = True
                st.subheader("📖 恩典與體會紀錄")
                st.dataframe(pd.DataFrame(results["grace_records"]), use_container_width=True)
                
            if results.get("venue_bookings"):
                has_data = True
                st.subheader("🏠 場地借用紀錄")
                st.dataframe(pd.DataFrame(results["venue_bookings"]), use_container_width=True)
                
            if results.get("roster_schedules"):
                has_data = True
                st.subheader("📅 事奉排班紀錄")
                st.dataframe(pd.DataFrame(results["roster_schedules"]), use_container_width=True)
                
            if not has_data:
                st.info(c.LABELS["search_no_results"])

    # ── 子頁籤 2: 同工名單維護 ──
    with subtab_worker_mgmt:
        st.subheader(c.LABELS["worker_add_header"])
        with st.form("form_add_worker"):
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                new_w_name = st.text_input(c.LABELS["worker_name_input"])
            with col_w2:
                new_w_role = st.text_input(c.LABELS["worker_role_input"], value="一般同工")
                
            submit_add_worker = st.form_submit_button(c.LABELS["btn_add_worker"])
            if submit_add_worker:
                if new_w_name.strip():
                    if db.add_church_worker(new_w_name, new_w_role):
                        st.success(c.LABELS["worker_add_success"].format(name=new_w_name))
                        st.rerun()
                else:
                    st.error("請輸入同工姓名！")
                    
        st.divider()
        st.subheader(c.LABELS["worker_list_header"])
        workers_list = db.fetch_all_workers_details()
        if workers_list:
            st.dataframe(pd.DataFrame(workers_list), use_container_width=True)
