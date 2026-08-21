# ==========================================
# constants.py - 教會事奉管理系統 繁體中文設定檔
# ==========================================

# 1. 頁面標題與系統名稱
PAGE_TITLE = "教會事奉管理與恩典紀錄系統"
MAIN_TITLE = "⛪ 教會事奉管理與恩典紀錄系統"

# 2. 分頁名稱 (Tabs)
TABS = ["📅 未來事奉排班", "🏠 場地借用管理", "🌟 恩典體會日記"]

# 3. 紀錄類型對照表 (Record Types)
RECORD_TYPE_KEYS = ["SCHEDULE", "ROOMS", "DIARY"]
RECORD_TYPE_MAP = {
    "SCHEDULE": "📅 事奉排班",
    "ROOMS": "🏠 場地借用",
    "DIARY": "🌟 恩典日記",
}

# 4. 下拉式選單觸發詞 (用於啟動動態文字輸入框)
OTHER_CUSTOM_TRIGGER = "其他 / 請自行於下方輸入"

# 5. 下拉選單預設基礎選項 (Base Options)
# 當同工輸入並儲存新的小組、崗位或場地後，系統會自動向 Supabase 撈取歷史紀錄並擴充至此選單中
GROUPS = [
    "青年小組",
    "社青小組",
    "婦女小組",
    "弟兄小組",
    "長者小組",
    "主日學部",
    "敬拜事奉處",
    "行政幹事部",
    OTHER_CUSTOM_TRIGGER,
]

ROLES = [
    "主領 / 司會",
    "領唱 / 歌手",
    "司琴 / 伴奏",
    "吉他手 / 樂手",
    "鼓手",
    "音控 / 直播",
    "簡播 / 投影",
    "接待 / 招待",
    "主日學老師",
    "講員 / 證道",
    OTHER_CUSTOM_TRIGGER,
]

ROOMS = [
    "大堂 (Main Hall)",
    "副堂 (Sub Hall)",
    "101 教室",
    "102 教室",
    "201 小組室",
    "副堂會客室",
    "舞蹈/舞蹈團契室",
    OTHER_CUSTOM_TRIGGER,
]

# 6. Dataframe 顯示欄位映射 (英中對照)

# 分頁 1: 未來事奉排班欄位映射
DF_COL_MAP_SCHEDULE = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "事奉崗位",
    "group_name": "小組",
    "people": "事奉同工",
    "content": "聚會摘要",
    "grace_notes": "備註",
}

# 分頁 2: 場地借用管理欄位映射
DF_COL_MAP_ROOMS = {
    "service_date": "日期",
    "service_time": "時間",
    "room_name": "借用場地",
    "group_name": "借用單位/小組",
    "people": "負責人",
    "content": "使用用途",
    "grace_notes": "器材需求/備註",
}

# 分頁 3: 恩典體會日記欄位映射
DF_COL_MAP_DIARY = {
    "service_date": "日期",
    "service_time": "時間",
    "role": "崗位",
    "group_name": "小組",
    "people": "同行同工",
    "content": "摘要",
    "grace_notes": "恩典體會",
}
