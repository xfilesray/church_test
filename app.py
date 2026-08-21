import streamlit as st
import pandas as pd
import constants as c
import database as db

# 設定頁面資訊
st.set_page_config(page_title="Church Ministry Management System", layout="wide")

st.title(c.APP_TITLE)
st.caption(c.APP_SUBTITLE)
st.divider()

# ==========================================
# 1. Shared Section: Date & Time
# ==========================================
st.subheader(c.LABELS["date_section"])
col_date, col_time = st.columns(2)

with col_date:
    selected_date = st.date_input(c.LABELS["select_date"])

with col_time:
    selected_time_slot = st.selectbox(
        c.LABELS["select_time"],
        options=c.TIME_SLOT_OPTIONS
    )
    if selected_time_slot == "其他 / 請自行於下方輸入":
        selected_time_slot = st.text_input(c.LABELS["custom_time"], value="")

st.divider()

# ==========================================
# 2. Main Module Tabs
# ==========================================
tab_grace, tab_venue, tab_roster = st.tabs([
    c.LABELS["tab_grace"], 
    c.LABELS["tab_venue"], 
    c.LABELS["tab_roster"]
])

# ------------------------------------------
# Module A: Grace & Experience Log
# ------------------------------------------
with tab_grace:
    st.header(c.LABELS["grace_header"])
    st.info(f"📍 當前套用時間：{selected_date} | {selected_time_slot}")
    
    with st.form("grace_log_form"):
        worker_name = st.text_input(c.LABELS["worker_name"])
        selected_gifts = st.multiselect(
            c.LABELS["gifts_select"],
            options=c.GRACE_GIFTS_OPTIONS
        )
        
        custom_gift_val = ""
        if "其他 / 請自行於下方輸入" in selected_gifts:
            custom_gift_val = st.text_input(c.LABELS["custom_gift"])
            
        grace_reflection = st.text_area(c.LABELS["reflection"])
        prayer_requests = st.text_area(c.LABELS["prayer"])
        
        submit_grace = st.form_submit_button(c.LABELS["btn_save_grace"])
        
        if submit_grace:
            if not worker_name.strip():
                st.error("❌ 請輸入同工姓名！")
            else:
                # 1. 處理自訂選項整合
                final_gifts = [g for g in selected_gifts if g != "其他 / 請自行於下方輸入"]
                if custom_gift_val.strip():
                    final_gifts.append(custom_gift_val.strip())
                
                # 2. 呼叫 database.py 寫入 Supabase
                try:
                    db.save_grace_log(
                        event_date=selected_date,
                        time_slot=selected_time_slot,
                        worker_name=worker_name,
                        gifts=final_gifts,
                        reflection=grace_reflection,
                        prayer=prayer_requests
                    )
                    st.success(f"✅ 已成功儲存 [{worker_name}] 的恩賜與體會紀錄！")
                except Exception as e:
                    st.error(f"❌ 儲存失敗：{e}")

# ------------------------------------------
# Module B: Venue Reservation
# ------------------------------------------
with tab_venue:
    st.header(c.LABELS["venue_header"])
    st.info(f"📍 當前預約時間：{selected_date} | {selected_time_slot}")
    
    with st.form("venue_booking_form"):
        venue_choice = st.selectbox(
            c.LABELS["venue_select"],
            options=c.VENUE_OPTIONS
        )
        
        final_venue = venue_choice
        if venue_choice == "其他 / 請自行於下方輸入":
            final_venue = st.text_input(c.LABELS["custom_venue"])
            
        applicant_name = st.text_input(c.LABELS["applicant"])
        event_purpose = st.text_input(c.LABELS["purpose"])
        
        force_save_venue = st.checkbox(c.LABELS["force_save_venue"])
        
        submit_venue = st.form_submit_button(c.LABELS["btn_save_venue"])
        
         if submit_venue:
            if not final_venue.strip() or not applicant_name.strip():
                st.error("❌ 請填寫完整的場地名稱與申請人資訊！")
            else:
                # 1. 查詢資料庫確認是否場地撞期
                has_conflict = db.check_venue_conflict(
                    event_date=selected_date, 
                    time_slot=selected_time_slot, 
                    venue_name=final_venue
                )
                
                # 2. 若撞期且未勾選強制儲存，發出警示；否則寫入資料庫
                if has_conflict and not force_save_venue:
                    st.error(f"⚠️ 衝突警示：[{final_venue}] 在此時段已被預約！若需覆蓋請勾選強制儲存。")
                else:
                    try:
                        db.save_venue_booking(
                            event_date=selected_date,
                            time_slot=selected_time_slot,
                            venue_name=final_venue,
                            applicant=applicant_name,
                            purpose=event_purpose,
                            is_forced=force_save_venue
                        )
                        st.success(f"✅ 已成功提交 [{final_venue}] 的借用申請！")
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

# ------------------------------------------
# Module C: Ministry Roster
# ------------------------------------------
with tab_roster:
    st.header(c.LABELS["roster_header"])
    st.info(f"📍 當前排班時間：{selected_date} | {selected_time_slot}")
    st.caption(c.LABELS["roster_hint"])
    
    with st.form("roster_form"):
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            worship_lead = st.text_input(c.LABELS["worship_lead"])
            speaker = st.text_input(c.LABELS["speaker"])
            av_team = st.text_input(c.LABELS["av_team"])
            
        with col_r2:
            usher_team = st.text_input(c.LABELS["usher_team"])
            sunday_school = st.text_input(c.LABELS["sunday_school"])
            other_roles = st.text_input(c.LABELS["other_roles"])
            
        force_save_roster = st.checkbox(c.LABELS["force_save_roster"])
        
        submit_roster = st.form_submit_button(c.LABELS["btn_save_roster"])
        
        if submit_roster:
            # 1. 解析同工姓名（相容中英文逗號）
            def parse_names(input_str):
                if not input_str:
                    return []
                return [name.strip() for name in input_str.replace("，", ",").split(",") if name.strip()]
            
            all_assigned_workers = (
                parse_names(worship_lead) + 
                parse_names(speaker) + 
                parse_names(av_team) + 
                parse_names(usher_team) + 
                parse_names(sunday_school) + 
                parse_names(other_roles)
            )
            
            # 2. 檢測單表單內重複排班
            seen = set()
            self_duplicates = [w for w in all_assigned_workers if w in seen or seen.add(w)]
            
            # 3. 檢測資料庫內跨紀錄重複排班
            db_conflicts = db.check_roster_conflict(
                event_date=selected_date, 
                time_slot=selected_time_slot, 
                worker_list=all_assigned_workers
            )
            
            all_conflicts = list(set(self_duplicates + db_conflicts))
            
            # 4. 判斷是否阻擋或寫入
            if all_conflicts and not force_save_roster:
                st.warning(f"⚠️ 重複排班提醒：同工 [{', '.join(all_conflicts)}] 在此時段被指派了多個崗位！若確認無誤請勾選強制儲存。")
            else:
                try:
                    roles_data = {
                        "worship_lead": worship_lead,
                        "speaker": speaker,
                        "av_team": av_team,
                        "usher_team": usher_team,
                        "sunday_school": sunday_school,
                        "other_roles": other_roles
                    }
                    db.save_ministry_roster(
                        event_date=selected_date,
                        time_slot=selected_time_slot,
                        roles_dict=roles_data,
                        all_workers=all_assigned_workers,
                        is_forced=force_save_roster
                    )
                    st.success("✅ 事奉時間表已成功發布並存入資料庫！")
                except Exception as e:
                    st.error(f"❌ 發布失敗：{e}")
