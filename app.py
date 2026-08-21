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
# 1. 共用時段選擇器 (Shared Date & Time)
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
# 2. 四大模組分頁
# ==========================================
tab_grace, tab_venue, tab_roster, tab_viewer = st.tabs([
    c.LABELS["tab_grace"], 
    c.LABELS["tab_venue"], 
    c.LABELS["tab_roster"],
    "🔍 查詢紀錄"
])

# ------------------------------------------
# Module A: 恩典與體會紀錄
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
                final_gifts = [g for g in selected_gifts if g != "其他 / 請自行於下方輸入"]
                if custom_gift_val.strip():
                    final_gifts.append(custom_gift_val.strip())
                
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
# Module B: 場地借用
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
                has_conflict = db.check_venue_conflict(
                    event_date=selected_date, 
                    time_slot=selected_time_slot, 
                    venue_name=final_venue
                )
                
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
# Module C: Ministry Roster (動態 Supabase 同工選單版)
# ------------------------------------------
with tab_roster:
    st.header(c.LABELS["roster_header"])
    st.info(f"📍 當前排班時間：{selected_date} | {selected_time_slot}")
    
    # 動態從 Supabase 取得最新同工名單
    try:
        db_workers = db.fetch_church_workers()
    except Exception as e:
        db_workers = []
        st.error(f"⚠️ 無法載入同工名單：{e}")
        
    with st.form("roster_form"):
        st.subheader("👥 指派事奉崗位與同工")
        
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            worship_lead = st.multiselect("🎤 敬拜主領 / 樂手", options=db_workers)
            speaker = st.multiselect("📖 證道 / 講員", options=db_workers)
            av_team = st.multiselect("🎧 音控 / 直播同工", options=db_workers)

        with col_r2:
            usher_team = st.multiselect("🤝 招待 / 迎賓同工", options=db_workers)
            sunday_school = st.multiselect("🎨 主日學老師", options=db_workers)
            other_roles = st.multiselect("⛪ 其他事奉同工", options=db_workers)
        
        # 自訂/新同工輸入欄位
        custom_worker = st.text_input("➕ 若有新同工，請在此輸入（提交後將自動新增至資料庫，多人請用逗號分隔）：")
        
        force_save_roster = st.checkbox(c.LABELS["force_save_roster"])
        submit_roster = st.form_submit_button(c.LABELS["btn_save_roster"])
        
        if submit_roster:
            # 1. 解析自訂輸入的同工名單，並同步寫入 Supabase 資料庫
            custom_workers_list = []
            if custom_worker.strip():
                raw_list = [w.strip() for w in custom_worker.replace("，", ",").split(",") if w.strip()]
                for new_w in raw_list:
                    try:
                        db.add_church_worker(new_w)  # 自動寫入 church_workers 表
                        custom_workers_list.append(new_w)
                    except Exception as e:
                        st.warning(f"無法同步新增同工 {new_w}：{e}")

            # 2. 彙整所有被指派的同工名單
            all_assigned_workers = (
                worship_lead + speaker + av_team + 
                usher_team + sunday_school + other_roles + 
                custom_workers_list
            )
            
            # 3. 檢查單次排班內的重複指派
            seen = set()
            self_duplicates = [w for w in all_assigned_workers if w in seen or seen.add(w)]
            
            # 4. 檢查 Supabase 資料庫跨紀錄重複排班
            db_conflicts = db.check_roster_conflict(
                event_date=selected_date, 
                time_slot=selected_time_slot, 
                worker_list=all_assigned_workers
            )
            
            all_conflicts = list(set(self_duplicates + db_conflicts))
            
            # 5. 判斷阻擋或進行寫入
            if all_conflicts and not force_save_roster:
                st.warning(f"⚠️ 重複排班提醒：同工 [{', '.join(all_conflicts)}] 在此時段被重複指派！若確認無誤請勾選強制儲存。")
            else:
                try:
                    roles_data = {
                        "worship_lead": ", ".join(worship_lead),
                        "speaker": ", ".join(speaker),
                        "av_team": ", ".join(av_team),
                        "usher_team": ", ".join(usher_team),
                        "sunday_school": ", ".join(sunday_school),
                        "other_roles": ", ".join(other_roles + custom_workers_list)
                    }
                    
                    db.save_ministry_roster(
                        event_date=selected_date,
                        time_slot=selected_time_slot,
                        roles_dict=roles_data,
                        all_workers=all_assigned_workers,
                        is_forced=force_save_roster
                    )
                    st.success("✅ 事奉時間表已成功發布並寫入資料庫！")
                    st.rerun()  # 重新載入頁面以即時刷新下拉選單
                except Exception as e:
                    st.error(f"❌ 發布失敗：{e}")
# ------------------------------------------
# Module D: 🔍 查詢紀錄版面 (支援大小寫不限與多欄位搜尋)
# ------------------------------------------
with tab_viewer:
    st.header("🔍 教會事奉數據與紀錄查詢")
    
    if st.button("🔄 重新整理資料"):
        st.rerun()
        
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "📖 恩典日記紀錄", 
        "🏠 場地預約紀錄", 
        "📅 事奉排班時間表"
    ])
    
    # 1. 恩典日記紀錄
    with sub_tab1:
        st.subheader("📖 恩典與體會歷史紀錄")
        try:
            grace_data = db.fetch_grace_logs()
            if grace_data:
                df_grace = pd.DataFrame(grace_data)
                
                # 關鍵字搜尋 (不限大小寫 case=False)
                search_term = st.text_input("🔍 搜尋關鍵字（支援中英文、大細階）：", key="search_grace")
                if search_term.strip():
                    term = search_term.strip()
                    df_grace = df_grace[
                        df_grace["worker_name"].astype(str).str.contains(term, case=False, na=False) |
                        df_grace["spiritual_gifts"].astype(str).str.contains(term, case=False, na=False) |
                        df_grace["reflection"].astype(str).str.contains(term, case=False, na=False) |
                        df_grace["prayer_requests"].astype(str).str.contains(term, case=False, na=False)
                    ]
                
                df_grace_display = df_grace.rename(columns={
                    "event_date": "日期",
                    "time_slot": "時段",
                    "worker_name": "同工姓名",
                    "spiritual_gifts": "服侍恩賜/項目",
                    "reflection": "恩典體會與心得",
                    "prayer_requests": "代禱事項",
                    "created_at": "建立時間"
                })
                
                st.dataframe(df_grace_display, use_container_width=True)
            else:
                st.info("尚無任何恩典日記紀錄。")
        except Exception as e:
            st.error(f"資料讀取失敗：{e}")

    # 2. 場地預約紀錄
    with sub_tab2:
        st.subheader("🏠 場地借用歷史紀錄")
        try:
            venue_data = db.fetch_venue_bookings()
            if venue_data:
                df_venue = pd.DataFrame(venue_data)
                
                # 關鍵字搜尋 (不限大小寫 case=False)
                search_venue = st.text_input("🔍 搜尋關鍵字（支援中英文、大細階）：", key="search_venue")
                if search_venue.strip():
                    term = search_venue.strip()
                    df_venue = df_venue[
                        df_venue["venue_name"].astype(str).str.contains(term, case=False, na=False) |
                        df_venue["applicant_name"].astype(str).str.contains(term, case=False, na=False) |
                        df_venue["event_purpose"].astype(str).str.contains(term, case=False, na=False)
                    ]
                
                df_venue_display = df_venue.rename(columns={
                    "event_date": "日期",
                    "time_slot": "時段",
                    "venue_name": "借用場地",
                    "applicant_name": "申請人/單位",
                    "event_purpose": "聚會用途",
                    "is_forced": "強制儲存",
                    "created_at": "申請時間"
                })
                
                st.dataframe(df_venue_display, use_container_width=True)
            else:
                st.info("尚無任何場地預約紀錄。")
        except Exception as e:
            st.error(f"資料讀取失敗：{e}")

    # 3. 事奉排班時間表
    with sub_tab3:
        st.subheader("📅 事奉時間表歷史紀錄")
        try:
            roster_data = db.fetch_ministry_rosters()
            if roster_data:
                df_roster = pd.DataFrame(roster_data)
                
                # 關鍵字搜尋 (不限大小寫 case=False，可搜尋英文名如 John 或 中文名)
                search_roster = st.text_input("🔍 搜尋同工姓名或崗位（支援大細階）：", key="search_roster")
                if search_roster.strip():
                    term = search_roster.strip()
                    df_roster = df_roster[
                        df_roster["all_workers"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["worship_lead"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["speaker"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["av_team"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["usher_team"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["sunday_school"].astype(str).str.contains(term, case=False, na=False) |
                        df_roster["other_roles"].astype(str).str.contains(term, case=False, na=False)
                    ]
                
                df_roster_display = df_roster.rename(columns={
                    "event_date": "日期",
                    "time_slot": "時段",
                    "worship_lead": "敬拜主領",
                    "speaker": "講員/證道",
                    "av_team": "音控/直播",
                    "usher_team": "招待/迎賓",
                    "sunday_school": "主日學老師",
                    "other_roles": "其他崗位",
                    "created_at": "發布時間"
                })
                
                st.dataframe(df_roster_display, use_container_width=True)
            else:
                st.info("尚無任何排班紀錄。")
        except Exception as e:
            st.error(f"資料讀取失敗：{e}")
