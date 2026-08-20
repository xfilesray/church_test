# 頁面與標題設定
PAGE_TITLE = "教會事奉管理與恩典紀錄系統"
MAIN_TITLE = "⛪ 教會事奉管理與恩典紀錄系統"

# 分頁名稱
TABS = ["📅 未來事奉排班", "🏠 場地借用管理", "🌟 恩典體會日記"]

# 紀錄類型選單對照
RECORD_TYPE_KEYS = ["SCHEDULE", "ROOMS", "DIARY"]
RECORD_TYPE_MAP = {
    "SCHEDULE": "📅 事奉排班",
    "ROOMS": "🏠 場地借用",
    "DIARY": "🌟 恩典日記",
}

# 選單觸發詞
OTHER_CUSTOM_TRIGGER = "其他 / 請自行於下方輸入"

# 小組列表
GROUPS = ["主日學", "青年社青", "婦女會", "弟兄會", "敬拜讚美隊", "其他 / 請自行於下方輸入"]

# 事奉崗位列表
ROLES = ["領唱/主領", "司琴/伴奏", "音控/直播", "司會", "接待/招聚", "其他 / 請自行於下方輸入"]

# 場地/房間列表
ROOMS = ["大堂", "副堂", "副堂A教室", "副堂B教室", "會客室", "其他 / 請自行於下方輸入"]

# Dataframe 表格欄位名稱映射
DF_COL_MAP_SCHEDULE = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "事奉崗位",
    "content": "事奉內容",
    "group_name": "所屬小組",
    "people": "同工姓名",
    "grace_notes": "備註",
}

DF_COL_MAP_ROOMS = {
    "service_date": "借用日期",
    "service_time": "借用時間",
    "room_name": "場地/房間",
    "content": "使用用途",
    "group_name": "借用單位/小組",
    "people": "聯絡負責人",
    "grace_notes": "器材/特別需求",
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
