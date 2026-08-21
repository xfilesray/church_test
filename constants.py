# constants.py
# ==========================================
# Church Service Management & Grace Journal
# Language & Configuration Management
# ==========================================

# Page Config
PAGE_TITLE = "教會事奉管理與恩典紀錄系統"
PAGE_ICON = "⛪"

# Sidebar / Navigation Labels
NAV_HEADER = "⛪ 系統選單"
NAV_LABEL_FORM = "📝 新增資料表單"
NAV_LABEL_DATA = "📊 資料查詢與管理"

# Form Sections
FORM_TITLE = "📝 提交新紀錄"
SECTION_BASIC = "1. 基本資訊"
SECTION_CATEGORY = "2. 紀錄類型與對應內容"

# Form Field Labels
LABEL_DATE = "日期"
LABEL_USER = "紀錄人 / 提交者"
LABEL_RECORD_TYPE = "選擇紀錄類型"
LABEL_CONTENT = "內容詳情 / 禱告事項"

# Record Type Options
TYPE_GRACE = "📖 恩典與體會日記"
TYPE_SERVICE = "📅 未來事奉人手排班"
TYPE_VENUE = "🏠 教會房間/場地借用"

RECORD_TYPES = [TYPE_GRACE, TYPE_SERVICE, TYPE_VENUE]

# Dynamic Options - Service Roster
LABEL_SERVICE_ROLE = "事奉崗位"
SERVICE_ROSTER_OPTIONS = [
    "敬拜讚美隊",
    "主日學老師",
    "音控與直播組",
    "招待與款待組",
    "聖餐服侍組",
    "其他 / 請自行於下方輸入"
]
LABEL_CUSTOM_ROLE = "請輸入自訂事奉崗位"
LABEL_SERVICE_WORKERS = "服侍同工名單（多人請用逗點分隔）"
HELP_SERVICE_WORKERS = "例如：張小明, 李大華, John Doe"

# Dynamic Options - Venue Booking
LABEL_VENUE_NAME = "借用場地/房間"
VENUE_OPTIONS = [
    "大堂 (Main Sanctuary)",
    "副堂 (Fellowship Hall)",
    "小組教室 A (Room A)",
    "小組教室 B (Room B)",
    "舞蹈/練琴房 (Music Room)",
    "其他 / 請自行於下方輸入"
]
LABEL_CUSTOM_VENUE = "請輸入自訂場地名稱"
LABEL_TIME_SLOT = "借用時段"
TIME_SLOT_OPTIONS = [
    "早禱會 (07:30 - 08:30)",
    "主日早場 (09:00 - 11:00)",
    "主日午場 (11:30 - 13:30)",
    "午後團契 (14:00 - 16:30)",
    "晚間聚會 (19:30 - 21:30)",
    "全天借用"
]
LABEL_CONTACT_PERSON = "場地負責人 / 聯絡同工"

# Buttons & Messages
BTN_SUBMIT = "提交紀錄"
BTN_FORCE_SAVE = "⚠️ 強制儲存（忽略衝突）"

MSG_SUCCESS = "✅ 紀錄成功寫入資料庫！"
MSG_FORCE_SUCCESS = "⚠️ 已成功強制寫入資料庫！"
MSG_MISSING_FIELDS = "❌ 請填寫所有必填欄位。"
MSG_DB_ERROR = "❌ 資料庫操作失敗："
MSG_NO_DATA = "目前尚無任何紀錄。"

# Conflict Warning Messages
WARN_WORKER_CONFLICT = "⚠️ 同工排班衝突警示："
WARN_VENUE_CONFLICT = "⚠️ 場地撞期警示："

# Database Field Mappings (Supabase English Keys -> Traditional Chinese Display)
COLUMN_MAP = {
    "created_at": "建立時間",
    "event_date": "日期",
    "submitted_by": "紀錄人",
    "record_type": "紀錄類型",
    "content": "詳情/心得",
    "service_role": "事奉崗位",
    "service_workers": "服侍同工",
    "venue_name": "借用場地",
    "time_slot": "時段",
    "contact_person": "場地負責人"
}
