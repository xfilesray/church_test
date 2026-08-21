# ==============================================================================
# File: constants.py
# Description: Centralized I18n labels, options, and multi-language mappings.
# ==============================================================================

# ── UI 標籤與提示文字 (LABELS) ──
LABELS = {
    # 系統標題
    "app_title": "⛪ 教會事奉管理與恩典紀錄系統",
    "app_caption": "整合恩典分享、場地預約防撞、事奉排班與跨欄位查詢管理",

    # 主選單 Tabs
    "tab_grace": "📖 恩典與體會紀錄",
    "tab_venue": "🏠 場地借用",
    "tab_roster": "📅 事奉排班時間表",
    "tab_search": "🔍 查詢紀錄與管理",

    # 模組 A: 恩典與體會
    "grace_header": "📖 恩典與體會紀錄",
    "grace_worker_name": "👤 同工姓名",
    "grace_ministry_item": "🎯 服侍恩賜 / 項目",
    "grace_reflection": "💡 恩典與心得分享",
    "grace_prayer_request": "🙏 代禱事項 (選填)",
    "btn_save_grace": "💾 儲存恩典紀錄",
    "grace_save_success": "✨ 恩典紀錄已成功儲存！",

    # 模組 B: 場地借用
    "venue_header": "🏠 場地預約與借用登記",
    "venue_name": "🏛️ 借用場地",
    "venue_applicant": "👤 申請人 / 事工單位",
    "venue_purpose": "🎯 事工用途",
    "venue_booking_date": "📅 借用日期",
    "venue_start_time": "⏰ 開始時間",
    "venue_end_time": "⏰ 結束時間",
    "venue_notes": "📝 備註事項 (選填)",
    "force_save_venue": "⚠️ 強制儲存預約 (忽視時間重疊衝突警示)",
    "btn_save_venue": "💾 提交場地預約",
    "venue_conflict_warning": "⚠️ 場地預約衝突：該場地在指定時段已有其他預約紀錄！",
    "venue_time_error": "❌ 錯誤：結束時間必須晚於開始時間！",
    "venue_save_success": "✅ 場地預約成功！",

    # 模組 C: 事奉排班
    "roster_header": "📅 事奉排班時間表",
    "roster_service_date": "📅 主日 / 聚會日期",
    "roster_service_type": "⛪ 聚會類型",
    "roster_worship_leader": "🎤 敬拜主領 / 樂手",
    "roster_speaker": "📖 證道 / 講員",
    "roster_sound_av": "🎧 音控 / 直播同工",
    "roster_usher": "🤝 招待 / 迎賓同工",
    "roster_sunday_school": "🎨 主日學老師",
    "roster_other_roles": "⛪ 其他事奉同工",
    "custom_worker_input": "➕ 新增自訂同工 (多位請用中英文逗號分隔)",
    "roster_notes": "📝 排班備註 (選填)",
    "force_save_roster": "⚠️ 強制儲存排班 (許可同工重複排班 / 聯合聚會)",
    "btn_save_roster": "💾 儲存排班紀錄",
    "roster_self_conflict": "⚠️ 表單內重複：同工 [{workers}] 在同一天被指派了多個重複崗位！",
    "roster_db_conflict": "⚠️ 雲端資料庫衝突：同工 [{workers}] 在 {date} 已有其他事奉排班！",
    "roster_save_success": "✅ 排班時間表已成功儲存！",

    # 模組 D: 查詢與管理
    "search_header": "🔍 紀錄查詢與系統管理",
    "subtab_query": "🔍 綜合紀錄查詢",
    "subtab_worker_mgmt": "👥 同工名單維護",
    "search_query_label": "輸入關鍵字 (支援跨欄位、不限大小寫模糊查詢)",
    "search_module_filter": "選擇查詢範圍",
    "search_no_results": "ℹ️ 未找到符合條件的紀錄。",
    "worker_add_header": "➕ 新增教會同工",
    "worker_name_input": "同工姓名",
    "worker_role_input": "主要服侍角色 / 恩賜",
    "btn_add_worker": "➕ 新增同工",
    "worker_add_success": "✅ 同工 [{name}] 已成功加入名單！",
    "worker_list_header": "📋 目前在籍同工名單"
}

# ── 下拉選單與預設選項 (OPTIONS) ──
OPTIONS = {
    "venues": ["大堂", "201 副堂", "202 團契室", "301 主日學教室", "302 練琴室", "舞蹈教室", "教會廚房"],
    "service_types": ["主日崇拜", "青年崇拜", "兒童主日學", "週三禱告會", "特會 / 講座", "團契聚會"],
    "search_modules": ["全部模組", "恩典紀錄", "場地預約", "事奉排班"]
}
