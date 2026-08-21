# -*- coding: utf-8 -*-
"""
constants.py - 集中管理繁體中文 UI 標籤、對照表與預設選項
"""

# App 系統設定
APP_TITLE = "⛪ 教會事奉管理與恩典紀錄系統"
APP_SUBTITLE = "專為教會同工與團隊設計的一站式事奉排班、場地借用與恩典紀錄平台"

# 共用時段選項
TIME_SLOT_OPTIONS = [
    "早堂 (08:00 - 10:00)",
    "主日堂 (10:00 - 12:00)",
    "午堂 (14:00 - 16:00)",
    "晚堂 (19:00 - 21:00)",
    "其他 / 請自行於下方輸入"
]

# 模組 A：事奉恩賜與體會
GRACE_GIFTS_OPTIONS = [
    "講道 / 分享",
    "敬拜讚美 / 樂手",
    "關懷代禱",
    "影音 / 音控 / 直播",
    "行政協調 / 總務",
    "兒童主日學 / 青少年",
    "招待 / 迎賓",
    "其他 / 請自行於下方輸入"
]

# 模組 B：場地借用
VENUE_OPTIONS = [
    "大堂 (Main Sanctuary)",
    "副堂 (Side Chapel)",
    "101 教室",
    "102 教室",
    "舞蹈 / 小組室",
    "其他 / 請自行於下方輸入"
]

# UI 文字標籤 (UI Labels)
LABELS = {
    "date_section": "📅 請選擇活動 / 事奉時間 (Shared Date & Time)",
    "select_date": "選擇日期",
    "select_time": "選擇時段",
    "custom_time": "請輸入自訂時段",
    
    # Tab 1: 恩賜與體會
    "tab_grace": "📖 紀錄事奉恩賜",
    "grace_header": "📖 紀錄事奉恩賜與心得日記",
    "worker_name": "同工姓名",
    "gifts_select": "事奉恩賜 / 服侍項目",
    "custom_gift": "請輸入自訂恩賜/項目",
    "reflection": "恩典體會與心得紀錄",
    "prayer": "代禱事項",
    "btn_save_grace": "儲存恩賜紀錄",
    
    # Tab 2: 場地借用
    "tab_venue": "🏠 借用場地",
    "venue_header": "🏠 教會房間 / 場地借用申請",
    "venue_select": "選擇借用場地 / 房間",
    "custom_venue": "請輸入自訂場地名稱",
    "applicant": "申請人 / 單位聯絡人",
    "purpose": "事工 / 聚會用途",
    "force_save_venue": "⚠️ 若有場地撞期，仍強制儲存 (Force Save)",
    "btn_save_venue": "提交場地借用申請",
    
    # Tab 3: 排班時間表
    "tab_roster": "📅 事奉時間表",
    "roster_header": "📅 未來事奉時間表 (團隊排班)",
    "worship_lead": "敬拜主領",
    "speaker": "講員 / 證道",
    "av_team": "音控 / 直播同工",
    "usher_team": "招待 / 迎賓同工",
    "sunday_school": "主日學老師",
    "other_roles": "其他事奉同工",
    "roster_hint": "💡 多位同工請用逗號（中英文皆可）分隔，例如：張弟兄, 李姊妹",
    "force_save_roster": "⚠️ 若有重複排班警示，仍強制儲存 (Force Save)",
    "btn_save_roster": "發布事奉時間表",

    "tab_worker_mgmt": "👥 同工名單管理",
    "worker_mgmt_header": "👥 同工名單與狀態維護",
    "btn_update_status": "更新狀態",
    "btn_delete_worker": "刪除同工",
    "msg_worker_updated": "已更新同工狀態！",
    "msg_worker_deleted": "已成功刪除同工！",
    "confirm_delete_worker": "確定要永久刪除此同工嗎？"
}
