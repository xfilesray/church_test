PAGE_TITLE = "教會事奉、場地與恩典管理系統"
MAIN_TITLE = "⛪ 教會事奉、場地與恩典管理系統"

# 下拉選單選項
ROLES = [
    "敬拜隊/司琴", "主日學/助教", "音控/直播/投影片", 
    "接待/司事/總務", "小組長/牧養/導師", "關懷/探訪/新朋友跟進", 
    "主席/領會", "宣教/外展", "其他 / 請自行於下方輸入"
]

GROUPS = [
    "大衛小組", "約書亞青年團契", "迦勒長青團契", 
    "喜樂家庭小組", "安得烈小組", "其他 / 請自行於下方輸入"
]

ROOMS = [
    "大堂", "副堂", "101 會議室", "201 小組室", 
    "301 幼兒教室", "其他 / 請自行於下方輸入"
]

# 紀錄類型 (對應內部的 DIARY, SCHEDULE, ROOMS)
RECORD_TYPE_MAP = {
    "DIARY": "🌟 恩典與體會日記",
    "SCHEDULE": "📅 未來事奉人手排班",
    "ROOMS": "🏠 借用教會房間/場地"
}

RECORD_TYPE_KEYS = list(RECORD_TYPE_MAP.keys())

# 頁籤名稱
TABS = ["📅 未來事奉人手時間表", "🏠 房間/場地借用狀態", "📜 歷史恩典紀錄與數算"]

# 客製化輸入提示 (當選擇「其他」時)
OTHER_CUSTOM_TRIGGER = "其他 / 請自行於下方輸入"

# Dataframe 欄位對照表
DF_COL_MAP_SCHEDULE = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "崗位",
    "group_name": "所屬小組",
    "content": "服侍時段",
    "people": "同工名字",
    "grace_notes": "備註"
}

DF_COL_MAP_ROOMS = {
    "service_date": "日期",
    "service_time": "時間",
    "room_name": "借用房間",
    "group_name": "借用團體",
    "content": "借用用途",
    "people": "聯絡人",
    "grace_notes": "備註"
}

DF_COL_MAP_DIARY = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "崗位",
    "group_name": "所屬小組",
    "content": "摘要",
    "people": "同行同工",
    "grace_notes": "恩典體會"
}
