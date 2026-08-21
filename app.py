# app.py
"""
Church Ministry Management & Grace Journal System
Main Application Entry Point (Pure UI Logic & Workflow Control)
"""

import datetime
import streamlit as st

# Local Module Imports
import constants as const
from database import get_supabase_client, check_conflicts, save_record, load_records

# --- Page & Theme Configuration ---
st.set_page_config(
    page_title=const.PAGE_TITLE,
    page_icon=const.PAGE_ICON,
    layout="wide"
)

st.title(f"{const.PAGE_ICON} {const.PAGE_TITLE}")

# --- Initialize Supabase Client ---
try:
    supabase = get_supabase_client()
except Exception as err:
    st.error(f"❌ Failed to connect to Supabase: {err}")
    st.stop()

# --- Main Interface Tabs ---
tab_form, tab_data = st.tabs([
    "📝 新增事奉與恩典紀錄", 
    "🔍 查詢與檢視紀錄"
])

# ==========================================
# TAB 1: THREE-IN-ONE FORM INPUT
# ==========================================
with tab_form:
    st.subheader("三合一紀錄表單 (Form Input)")
    
    with st.form("church_record_form", clear_on_submit=False):
        col_left, col_right = st.columns(2)
        
        # Left Column: Date, Time Slot, Ministry & Personnel
        with col_left:
            input_date = st.date_input(const.TEXT_DATE_SELECT, datetime.date.today())
            input_slot = st.selectbox(const.TEXT_TIME_SLOT, const.TIME_SLOTS)
            
            # Ministry Role Dynamic Input
            role_sel = st.selectbox("事奉崗位", const.ROLES)
            if role_sel == const.OPTION_OTHER:
                input_role = st.text_input("請輸入自訂崗位名稱", placeholder="例：特會攝影 / 兒幼帶領")
            else:
                input_role = role_sel
                
            input_personnel = st.text_area(
                "排班人員（多位同工請用逗點、頓點或換行隔開）", 
                placeholder="例如：張小明, 李大華, 王五"
            )

        # Right Column: Room Reservation & Grace Journal
        with col_right:
            # Room Name Dynamic Input
            room_sel = st.selectbox("借用場地/房間", const.ROOMS)
            if room_sel == const.OPTION_OTHER:
                input_room = st.text_input("請輸入自訂場地名稱", placeholder="例：副堂 B 區")
            else:
                input_room = room_sel
                
            input_contact = st.text_input("借用聯絡人", placeholder="例：張長老")
            
            input_diary = st.text_area(
                "恩典與體會日記（數算恩典/心得/禱告事項）", 
                height=120,
                placeholder="在此紀錄今日服侍心得或感恩事項..."
            )

        # Form Submit Button
        submitted = st.form_submit_button("送出紀錄", type="primary")

    # Submission & Conflict Detection Logic
    if submitted:
        date_str = str(input_date)
        
        # Check for Room Collisions & Personnel Overlaps
        conflicts = check_conflicts(
            supabase=supabase,
            date_str=date_str,
            time_slot=input_slot,
            room=input_room,
            personnel_text=input_personnel
        )
        
        has_conflict = conflicts["has_room_conflict"] or len(conflicts["conflicting_people"]) > 0
        
        # Prepare Data Payload
        record_payload = {
            "event_date": date_str,
            "time_slot": input_slot,
            "grace_diary": input_diary,
            "ministry_role": input_role,
            "personnel": input_personnel,
            "room_name": input_room,
            "contact_person": input_contact
        }

        if not has_conflict:
            # Safe Insert
            try:
                save_record(supabase, record_payload)
                st.success(const.TEXT_SUBMIT_SUCCESS)
                st.rerun()
            except Exception as err:
                st.error(f"❌ 儲存失敗: {err}")
        else:
            # Warning Banner for Detected Conflicts
            st.warning(const.TEXT_FORCE_SAVE)
            
            if conflicts["has_room_conflict"]:
                st.error(f"🚨 場地衝突：【{input_room}】在 {date_str} ({input_slot}) 已被預約！")
                
            if conflicts["conflicting_people"]:
                names = ", ".join(conflicts["conflicting_people"])
                st.error(f"🚨 同工重複排班：同工【{names}】在該時段已有事奉安排！")
            
            # Force Save Override Option
            if st.button("🔓 仍要強制寫入 (Force Save)"):
                try:
                    save_record(supabase, record_payload)
                    st.success("⚠️ 已強制將紀錄寫入資料庫！")
                    st.rerun()
                except Exception as err:
                    st.error(f"❌ 強制寫入失敗: {err}")

# ==========================================
# TAB 2: DATA SEARCH & VIEW
# ==========================================
with tab_data:
    st.subheader("歷史資料檢視與關鍵字搜尋")
    
    try:
        df = load_records(supabase)
    except Exception as err:
        st.error(f"❌ 無法載入歷史紀錄: {err}")
        df = None

    if df is not None and not df.empty:
        # Search Box
        search_kw = st.text_input("🔍 關鍵字搜尋（可搜尋同工姓名、崗位、場地或日記內容）", "")
        
        # Dynamic Pandas Search Filter
        if search_kw.strip():
            mask = df.apply(
                lambda row: row.astype(str).str.contains(search_kw.strip(), case=False).any(), 
                axis=1
            )
            filtered_df = df[mask]
        else:
            filtered_df = df

        # Rename Columns using Configuration Map
        display_cols = [c for c in const.COLUMN_MAPPINGS.keys() if c in filtered_df.columns]
        df_display = filtered_df[display_cols].rename(columns=const.COLUMN_MAPPINGS)
        
        st.dataframe(
            df_display, 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("目前尚無資料紀錄。")
