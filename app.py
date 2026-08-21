# app.py
# ==========================================
# Church Service Management & Grace Journal
# Main Application (With Date & Time Support)
# ==========================================

import os
from datetime import time
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import constants as c

# ------------------------------------------
# 1. Page & DB Initialization
# ------------------------------------------
st.set_page_config(
    page_title=c.PAGE_TITLE,
    page_icon=c.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client using Streamlit secrets or environment variables."""
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ 找不到 SUPABASE_URL 或 SUPABASE_KEY。請檢查 secrets.toml 或環境變數設定。")
        st.stop()
        
    return create_client(url, key)

supabase = init_supabase()
TABLE_NAME = "church_records"

# ------------------------------------------
# 2. Helper & Conflict Detection Logic
# ------------------------------------------
def parse_worker_names(worker_string: str) -> set:
    """Parse comma-separated worker names into a normalized clean set."""
    if not worker_string:
        return set()
    normalized = worker_string.replace("，", ",")
    return {name.strip().lower() for name in normalized.split(",") if name.strip()}

def check_conflicts(event_date: str, record_type: str, service_workers: str, venue_name: str, time_slot: str):
    """Checks database for potential roster or venue booking conflicts."""
    worker_conflicts = []
    venue_conflicts = False

    response = supabase.table(TABLE_NAME).select("*").eq("event_date", event_date).execute()
    existing_records = response.data

    if not existing_records:
        return worker_conflicts, venue_conflicts

    new_workers = parse_worker_names(service_workers)

    for rec in existing_records:
        # Check Worker Conflict
        if record_type == c.TYPE_SERVICE and rec.get("record_type") == c.TYPE_SERVICE:
            exist_workers = parse_worker_names(rec.get("service_workers", ""))
            overlap = new_workers.intersection(exist_workers)
            if overlap:
                for worker in overlap:
                    worker_conflicts.append({
                        "worker": worker,
                        "existing_role": rec.get("service_role")
                    })

        # Check Venue Conflict
        if record_type == c.TYPE_VENUE and rec.get("record_type") == c.TYPE_VENUE:
            if rec.get("venue_name") == venue_name and rec.get("time_slot") == time_slot:
                venue_conflicts = True

    return worker_conflicts, venue_conflicts

def insert_record(data: dict) -> bool:
    """Inserts a record dictionary into Supabase database."""
    try:
        supabase.table(TABLE_NAME).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"{c.MSG_DB_ERROR} {str(e)}")
        return False

# ------------------------------------------
# 3. Sidebar Navigation
# ------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/church.png", width=80)
    st.title(c.NAV_HEADER)
    st.markdown("---")
    
    menu_choice = st.radio(
        label="功能頁面切換",
        options=[c.NAV_LABEL_FORM, c.NAV_LABEL_DATA],
        index=0,
        key="navigation_menu"
    )
    
    st.markdown("---")
    st.caption("⛪ 教會事奉管理系統 v2.0")

# ------------------------------------------
# 4. View 1: Form Input (新增資料表單)
# ------------------------------------------
if menu_choice == c.NAV_LABEL_FORM:
    st.title(f"{c.PAGE_ICON} {c.PAGE_TITLE}")
    st.subheader(c.FORM_TITLE)

    with st.form(key="church_record_form", clear_on_submit=False):
        st.markdown(f"### {c.SECTION_BASIC}")
        col1, col2 = st.columns(2)
        with col1:
            # 日期選擇器
            event_date = st.date_input(c.LABEL_DATE)
        with col2:
            submitted_by = st.text_input(c.LABEL_USER)

        st.markdown(f"### {c.SECTION_CATEGORY}")
        record_type = st.selectbox(c.LABEL_RECORD_TYPE, c.RECORD_TYPES)

        # Dynamic Variables
        service_role = ""
        service_workers = ""
        venue_name = ""
        time_slot = ""
        start_time_str = ""
        end_time_str = ""
        contact_person = ""

        # Dynamic Section: Service Roster (事奉排班)
        if record_type == c.TYPE_SERVICE:
            selected_role = st.selectbox(c.LABEL_SERVICE_ROLE, c.SERVICE_ROSTER_OPTIONS)
            if "其他" in selected_role:
                service_role = st.text_input(c.LABEL_CUSTOM_ROLE)
            else:
                service_role = selected_role
            
            service_workers = st.text_input(c.LABEL_SERVICE_WORKERS, help=c.HELP_SERVICE_WORKERS)

        # Dynamic Section: Venue Booking (場地借用 - 包含時間選擇)
        elif record_type == c.TYPE_VENUE:
            selected_venue = st.selectbox(c.LABEL_VENUE_NAME, c.VENUE_OPTIONS)
            if "其他" in selected_venue:
                venue_name = st.text_input(c.LABEL_CUSTOM_VENUE)
            else:
                venue_name = selected_venue

            # 提供「預設時段」與「自訂時間」雙模式
            time_option = st.radio(
                c.LABEL_TIME_OPTION, 
                [c.TIME_OPTION_SLOT, c.TIME_OPTION_CUSTOM],
                horizontal=True
            )

            if time_option == c.TIME_OPTION_SLOT:
                time_slot = st.selectbox(c.LABEL_TIME_SLOT, c.TIME_SLOT_OPTIONS)
            else:
                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    start_t = st.time_input(c.LABEL_START_TIME, time(9, 0))
                with t_col2:
                    end_t = st.time_input(c.LABEL_END_TIME, time(11, 0))
                start_time_str = start_t.strftime("%H:%M")
                end_time_str = end_t.strftime("%H:%M")
                time_slot = f"{start_time_str} - {end_time_str}"

            contact_person = st.text_input(c.LABEL_CONTACT_PERSON)

        # Common Content Field
        content = st.text_area(c.LABEL_CONTENT, height=120)

        submit_button = st.form_submit_button(label=c.BTN_SUBMIT, use_container_width=True)

    # Submission & Conflict Validation
    if submit_button:
        if not submitted_by or not content:
            st.error(c.MSG_MISSING_FIELDS)
        else:
            str_date = str(event_date)
            
            worker_conflicts, venue_conflicts = check_conflicts(
                str_date, record_type, service_workers, venue_name, time_slot
            )

            record_payload = {
                "event_date": str_date,
                "submitted_by": submitted_by,
                "record_type": record_type,
                "content": content,
                "service_role": service_role,
                "service_workers": service_workers,
                "venue_name": venue_name,
                "time_slot": time_slot,
                "start_time": start_time_str if start_time_str else None,
                "end_time": end_time_str if end_time_str else None,
                "contact_person": contact_person
            }

            has_conflict = False

            if worker_conflicts:
                has_conflict = True
                st.warning(c.WARN_WORKER_CONFLICT)
                for item in worker_conflicts:
                    st.write(f"- 同工 **{item['worker'].title()}** 在同日已有崗位：`{item['existing_role']}`")

            if venue_conflicts:
                has_conflict = True
                st.error(f"{c.WARN_VENUE_CONFLICT} **{venue_name}** 在 `{str_date}` 的 `{time_slot}` 時段已被預約！")

            if has_conflict:
                st.session_state["pending_record"] = record_payload
            else:
                if insert_record(record_payload):
                    st.success(c.MSG_SUCCESS)

    # Force Save Button
    if "pending_record" in st.session_state and st.session_state["pending_record"]:
        st.divider()
        st.info("若此為特殊聯合聚會或已知特例，您可以選擇強制儲存：")
        if st.button(c.BTN_FORCE_SAVE, use_container_width=True):
            if insert_record(st.session_state["pending_record"]):
                st.success(c.MSG_FORCE_SUCCESS)
                st.session_state["pending_record"] = None

# ------------------------------------------
# 5. View 2: Data Query & Dashboard (資料查詢)
# ------------------------------------------
elif menu_choice == c.NAV_LABEL_DATA:
    st.title(f"{c.PAGE_ICON} {c.NAV_LABEL_DATA}")

    try:
        response = supabase.table(TABLE_NAME).select("*").order("event_date", desc=True).execute()
        records = response.data

        if not records:
            st.info(c.MSG_NO_DATA)
        else:
            df = pd.DataFrame(records)

            # Filtering & Search
            col_filter1, col_filter2 = st.columns([1, 2])
            with col_filter1:
                filter_type = st.multiselect("篩選紀錄類型", c.RECORD_TYPES, default=c.RECORD_TYPES)
            with col_filter2:
                search_query = st.text_input("🔍 全文搜尋關鍵字 (日期/同工/場地/內容)", "")

            if filter_type:
                df = df[df["record_type"].isin(filter_type)]

            if search_query:
                search_mask = df.astype(str).apply(
                    lambda row: row.str.contains(search_query, case=False, na=False)
                ).any(axis=1)
                df = df[search_mask]

            # Reorder Columns
            columns_order = [
                "event_date", "time_slot", "submitted_by", "record_type", "service_role", 
                "service_workers", "venue_name", "contact_person", "content"
            ]
            existing_cols = [col for col in columns_order if col in df.columns]
            df = df[existing_cols]

            # Rename Headers
            df_display = df.rename(columns=c.COLUMN_MAP)

            st.dataframe(df_display, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"{c.MSG_DB_ERROR} {str(e)}")
