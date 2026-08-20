PAGE_TITLE = "教會事奉、場地與恩典管理系統"
MAIN_TITLE = "⛪ 教會事奉、場地與恩典管理系統"

ROLES = [
    "敬拜隊/司琴",
    "主日學/助教",
    "音控/直播/投影片",
    "接待/司事/總務",
    "小組長/牧養/導師",
    "關懷/探訪/新朋友跟進",
    "主席/領會",
    "宣教/外展",
    "其他 / 請自行於下方輸入",
]

GROUPS = [
    "大衛小組",
    "約書亞青年團契",
    "迦勒長青團契",
    "喜樂家庭小組",
    "安得烈小組",
    "其他 / 請自行於下方輸入",
]

ROOMS = [
    "大堂",
    "副堂",
    "101 會議室",
    "201 小組室",
    "301 幼兒教室",
    "其他 / 請自行於下方輸入",
]

TYPE_OPTIONS = ["🌟 恩典與體會日記", "📅 未來事奉人手排班", "🏠 借用教會房間/場地"]
TABS = ["📅 未來事奉人手時間表", "🏠 房間/場地借用狀態", "📜 歷史恩典紀錄與數算"]

# 系統內部邏輯對照 (維持純英文以防編碼問題)
RECORD_TYPE_KEYS = ["DIARY", "SCHEDULE", "ROOMS"]
RECORD_TYPE_MAP = {
    "DIARY": "🌟 恩典與體會日記",
    "SCHEDULE": "📅 未來事奉人手排班",
    "ROOMS": "🏠 借用教會房間/場地",
}
OTHER_CUSTOM_TRIGGER = "其他 / 請自行於下方輸入"

# DataFrame 欄位轉譯對照表
DF_COL_MAP_SCHEDULE = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "事奉崗位",
    "people": "事奉同工",
    "group_name": "所屬小組",
    "content": "事奉內容",
    "grace_notes": "備註",
}

DF_COL_MAP_ROOMS = {
    "service_date": "日期",
    "service_time": "時間",
    "room_name": "借用房間",
    "group_name": "借用單位",
    "people": "聯絡人",
    "content": "用途摘要",
    "grace_notes": "借用備註",
}

DF_COL_MAP_DIARY = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "崗位",
    "group_name": "所屬小組",
    "people": "同行同工",
    "content": "摘要",
    "grace_notes": "恩典體會",
}
