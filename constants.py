# constants.py
"""
Church Ministry Management & Grace Journal System
Global Constants, UI Labels, Options, and Column Mappings (Traditional Chinese)
"""

# --- Page Setup ---
PAGE_TITLE = "教會事奉管理與恩典紀錄系統"
PAGE_ICON = "⛪"

# --- Common UI Form Labels ---
TEXT_DATE_SELECT = "事奉 / 借用日期"
TEXT_TIME_SLOT = "事奉 / 借用時段"
TEXT_SUBMIT_SUCCESS = "✅ 紀錄已成功儲存！"
TEXT_FORCE_SAVE = "⚠️ 系統偵測到潛在衝突！若確定要繼續，請點擊下方「強制寫入」按鈕。"

# --- Selectbox Option Constants ---
OPTION_OTHER = "其他 / 請自行於下方輸入"

TIME_SLOTS = [
    "早禱會 (07:30 - 08:30)",
    "主日早堂 (09:00 - 10:30)",
    "主日午堂 (11:00 - 12:30)",
    "下午小組/培訓 (14:00 - 16:00)",
    "晚堂/晚會 (19:00 - 21:00)",
    OPTION_OTHER
]

ROLES = [
    "主領 / 傳道",
    "敬拜讚美隊",
    "音控 / 直播 / PPT",
    "司琴 / 伴奏",
    "主日學老師 / 助教",
    "接待 / 新親友關懷",
    "餐飲 / 招待組",
    "清潔 / 場地復原",
    OPTION_OTHER
]

ROOMS = [
    "大堂 (Main Sanctuary)",
    "副堂 (Secondary Hall)",
    "小組教室 A (Room A)",
    "小組教室 B (Room B)",
    "副堂副室 / 兒幼房",
    "禱告室 (Prayer Room)",
    "會議室 (Conference Room)",
    OPTION_OTHER
]

# --- Pandas DataFrame Column Display Mapping ---
# Format: "database_column_name": "UI Header Name (Traditional Chinese)"
COLUMN_MAPPINGS = {
    "event_date": "日期",
    "time_slot": "時段",
    "ministry_role": "事奉崗位",
    "personnel": "排班同工",
    "room_name": "借用場地",
    "contact_person": "借用聯絡人",
    "grace_diary": "恩典與體會日記",
    "created_at": "建立時間"
}
