# -*- coding: utf-8 -*-
"""
app.py - 主應用程式 (維持純英文變數，解耦 UI 標籤與資料庫邏輯)
"""

import datetime
import streamlit as st
import constants as c
import database as db

# 設定頁面配置
st.set_page_config(page_title=c.APP_TITLE, page_icon="⛪", layout="wide")

st.title(c.APP_TITLE)
st.caption(c.APP_SUBTITLE)

# ── 行數 21-35：共用時段與日期選擇區塊 ──
st.subheader(c.LABELS["date_section"])
col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input(c.LABELS["select_date"], value=datetime.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

with col_time:
    selected_time_option = st.selectbox(c.LABELS["select_time"], c.TIME_SLOT_OPTIONS)
    if selected_time_option == c.TIME_SLOT_OPTIONS[-1]:
        selected_time = st.text_input(c.LABELS["custom_time"], value="")
    else:
        selected_time = selected_time_option

# ── 行數 37-45：主選單 Tabs 宣告 ──
tab_grace, tab_venue, tab_roster, tab_search = st.tabs([
    c.LABELS["tab_grace"],
    c.LABELS["tab_venue"],
    c.LABELS["tab_roster"],
    c.LABELS["tab_search"]
])

# ── 行數 47-75：模組 A (📖 恩典與體會紀錄) ──
with tab_grace:
    st.header(c.LABELS["grace_header"])
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        worker_name = st.text_input(c.LABELS["worker_name"], key="grace_worker_name")
        gift_option = st.selectbox(c.LABELS["gifts_select"], c.GRACE_GIFTS_OPTIONS)
        gift_val = st.text_input(c.LABELS["custom_gift"]) if gift_option == c.GRACE_GIFTS_OPTIONS[-1] else gift_option
    
    with col_a2:
        reflection = st.text_area(c.LABELS["reflection"], height=100)
        prayer = st.text_area(c.LABELS["prayer"], height=80)
        
    if st.button(c.LABELS["btn_save_grace"], type="primary"):
        if not worker_name.strip():
            st.warning("請填寫同工姓名！")
        else:
            success = db.save_grace_record(date_str, selected_time, worker_name, gift_val, reflection, prayer)
            if success:
                st.success("恩典紀錄儲存成功！")

# ── 行數 77-110：模組 B (🏠 場地借用與防撞檢查) ──
with tab_venue:
    st.header(c.LABELS["venue_header"])
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        venue_option = st.selectbox(c.LABELS["venue_select"], c.VENUE_OPTIONS)
        venue_val = st.text_input(c.LABELS["custom_venue"]) if venue_option == c.VENUE_OPTIONS[-1] else venue_option
        applicant = st.text_input(c.LABELS["applicant"])
    
    with col_b2:
        purpose = st.text_area(c.LABELS["purpose"], height=100)
        force_save_venue = st.checkbox(c.LABELS["force_save_venue"])
        
    if st.button(c.LABELS["btn_save_venue"], type="primary"):
        if not venue_val.strip() or not applicant.strip():
            st.warning("請填寫完整的場地與申請人資訊！")
        else:
            has_conflict, conflicts = db.check_venue_conflict(date_str, selected_time, venue_val)
            if has_conflict and not force_save_venue:
                st.error(f"⚠️ 場地衝突！【{venue_val}】於 {date_str} {selected_time} 已被【{conflicts[0].get('applicant')}】預約。")
                st.info("如確定要聯合使用場地，請勾選「強制儲存 (Force Save)」後再點擊提交。")
            else:
                success = db.save_venue_booking(date_str, selected_time, venue_val, applicant, purpose)
                if success:
                    st.success("場地預約申請提交成功！")

# ── 行數 112-160：模組 C (📅 事奉排班時間表與智慧防錯) ──
with tab_roster:
    st.header(c.LABELS["roster_header"])
    st.caption(c.LABELS["roster_hint"])
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        worship_lead = st.text_input(c.LABELS["worship_lead"])
        speaker = st.text_input(c.LABELS["speaker"])
        av_team = st.text_input(c.LABELS["av_team"])
    with col_c2:
        usher_team = st.text_input(c.LABELS["usher_team"])
        sunday_school = st.text_input(c.LABELS["sunday_school"])
        other_roles = st.text_input(c.LABELS["other_roles"])
        
    force_save_roster = st.checkbox(c.LABELS["force_save_roster"])
    
    roles_data = {
        c.LABELS["worship_lead"]: worship_lead,
        c.LABELS["speaker"]: speaker,
        c.LABELS["av_team"]: av_team,
        c.LABELS["usher_team"]: usher_team,
        c.LABELS["sunday_school"]: sunday_school,
        c.LABELS["other_roles"]: other_roles
    }
    
    if st.button(c.LABELS["btn_save_roster"], type="primary"):
        has_conflict, warnings = db.check_roster_conflict(date_str, selected_time, roles_data)
        
        if has_conflict and not force_save_roster:
            st.warning("⚠️ 偵測到重複排班預警：")
            for w in warnings:
                st.write(f"- {w}")
            st.info("如為一人兼任多職或聯合聚會，請勾選「強制儲存 (Force Save)」後再點擊發布。")
        else:
            success = db.save_roster_record(date_str, selected_time, roles_data)
            if success:
                st.success("事奉時間表已成功發布！")

# ── 行數 162-200：模組 D (🔍 查詢與管理版面) ──
with tab_search:
    st.header(c.LABELS["search_header"])
    
    subtab_query, subtab_worker = st.tabs([
        c.LABELS["subtab_query"],
        c.LABELS["subtab_worker_mgmt"]
    ])
    
    with subtab_query:
        col_q1, col_q2, col_q3 = st.columns([2, 3, 3])
        with col_q1:
            module_choice = st.selectbox(c.LABELS["select_module"], ["恩典紀錄", "場地借用", "事奉排班"])
        with col_q2:
            search_kw = st.text_input(c.LABELS["search_keyword"])
        with col_q3:
            date_range = st.date_input(c.LABELS["date_range"], value=(datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()))
            
        if st.button(c.LABELS["btn_search"]):
            table_map = {
                "恩典紀錄": "grace_records",
                "場地借用": "venue_bookings",
                "事奉排班": "roster_records"
            }
            start_d = date_range[0].strftime("%Y-%m-%d") if len(date_range) > 0 else None
            end_d = date_range[1].strftime("%Y-%m-%d") if len(date_range) > 1 else None
            
            df_result = db.query_records(table_map[module_choice], keyword=search_kw, start_date=start_d, end_date=end_d)
            
            if df_result.empty:
                st.info(c.LABELS["no_data_found"])
            else:
                st.dataframe(df_result, use_container_width=True)
                csv = df_result.to_csv(index=False).encode('utf-8-sig')
                st.download_button(c.LABELS["export_csv"], data=csv, file_name=f"{module_choice}_export.csv", mime="text/csv")

    with subtab_worker:
        st.subheader(c.LABELS["worker_mgmt_header"])
        st.info("同工名單維護模組運行中...")
