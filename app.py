import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# 設置網頁標題與圖標
st.set_page_config(
    page_title="教會事奉管理與恩典紀錄系統",
    page_icon="⛪",
    layout="wide"
)

# 從 Streamlit Secrets 讀取雲端連線資訊
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    
    @st.cache_resource
    def get_supabase_client() -> Client:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    
    supabase = get_supabase_client()
else:
    st.error("⚠️ 未偵測到雲端資料庫設定！")
    st.info("💡 請前往 Streamlit Cloud 的 Settings -> Secrets 中貼入您的 SUPABASE_URL 與 SUPABASE_KEY。")
    st.stop()

# 應用程式標題
st.title("⛪ 教會事奉管理與恩典紀錄系統")
st.markdown("---")

# 事奉崗位清單
roles_list = [
    "敬拜隊/司琴", 
    "主日學/助教", 
    "音控/直播/投影片", 
    "接待/司事/總務", 
    "小組長/牧養/導師", 
    "關懷/探訪/新朋友跟進", 
    "主席/領會",
    "宣教/外展",
    "其他"
]

# 教會小組清單
groups_list = [
    "大衛小組",
    "約書亞青年團契",
    "迦勒長青團契",
    "喜樂家庭小組",
    "安得烈小組",
    "其他 / 請自行於下方輸入"
]

# 從 Supabase 撈取所有原始資料供全域與防重覆檢查使用
try:
    response = supabase.table("service_records").select("service_date, role, content, group_name, people, grace_notes, record_type").order("service_date", desc=False).execute()
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"雲端資料讀取失敗：{e}")
    df_raw = pd.DataFrame()

# 填補空值
if not df_raw.empty:
    df_raw["record_type"] = df_raw["record_type"].fillna("恩典日記")
    df_raw["service_date"] = df_raw["service_date"].fillna("").astype(str)
    df_raw["role"] = df_raw["role"].fillna("").astype(str)
    df_raw["group_name"] = df_raw["group_name"].fillna("").astype(str)
    df_raw["people"] = df_raw["people"].fillna("").astype(str)
    df_raw["content"] = df_raw["content"].fillna("").astype(str)
    df_raw["grace_notes"] = df_raw["grace_notes"].fillna("").astype(str)

today_str = datetime.now().strftime("%Y-%m-%d")

# ========================================================
# 🌟 側邊欄：輸入區（支援切換「恩典日記」與「事奉排班」）
# ========================================================
st.sidebar.header("✍️ 記錄新資料")
record_type = st.sidebar.radio("請選擇輸入類型：", ["🌟 恩典與體會日記", "📅 未來事奉人手排班"])

with st.sidebar.form(key="grace_form", clear_on_submit=True):
    service_date = st.date_input("事奉日期", datetime.now())
    role = st.selectbox("事奉崗位", roles_list)
    content = st.text_input("服侍內容/時段摘要", placeholder="例如：主日崇拜第一場、上午 10:00")
    
    selected_group = st.selectbox("選擇小組/團契名稱", groups_list)
    custom_group = st.text_input("若選擇『其他』，請在此輸入新小組：", placeholder="例如：提摩太小組")
    final_group = custom_group.strip() if (selected_group == "其他 / 請自行於下方輸入" and custom_group.strip()) else selected_group
    
    people = st.text_input("事奉人員 / 同行同工", placeholder="例如：張弟兄, 李姊妹 (多名請用半形逗號隔開)")
    
    if record_type == "🌟 恩典與體會日記":
        grace_notes = st.text_area("恩典與體會紀錄", placeholder="寫下神在這次服侍中給您的感動或學習...", height=150)
    else:
        grace_notes = st.text_area("備註事項 (選填)", placeholder="例如：當天需提前30分鐘到場...", height=100)
        
    submit_button = st.form_submit_button(label="儲存至雲端")

# 🌟 智慧防重覆檢查邏輯
if submit_button:
    if record_type == "🌟 恩典與體會日記" and not grace_notes:
        st.sidebar.error("❌ 記錄日記請務必填寫『恩典與體會紀錄』！")
    else:
        date_str = service_date.strftime("%Y-%m-%d")
        type_db = "恩典日記" if record_type == "🌟 恩典與體會日記" else "事奉排班"
        
        conflict_detected = False
        conflict_messages = []
        
        # 只有在「事奉排班」時才啟動時間與人手的嚴格重覆檢查
        if not df_raw.empty and type_db == "事奉排班":
            # 1. 檢查【時間 + 崗位】是否重覆：同一天同一個崗位是否已經被排班了
            check_role = df_raw[(df_raw["service_date"] == date_str) & (df_raw["role"] == role) & (df_raw["record_type"] == "事奉排班")]
            if not check_role.empty:
                conflict_detected = True
                conflict_messages.append(f"🚨【時間衝突】{date_str} 的「{role}」崗位已被預定！目前排班同工為：{check_role['people'].values[0]}")
            
            # 2. 檢查【時間 + 人手】是否重覆：輸入的同工在同一天是否已經有別的事奉
            if people.strip():
                # 兼容全形和半形逗號，將輸入的名字切開
                clean_people_input = people.replace("，", ",")
                input_names = [name.strip() for name in clean_people_input.split(",") if name.strip()]
                
                # 找出當天所有已存在的事奉排班
                current_day_schedules = df_raw[(df_raw["service_date"] == date_str) & (df_raw["record_type"] == "事奉排班")]
                
                for single_name in input_names:
                    for index, each_schedule in current_day_schedules.iterrows():
                        if single_name in each_schedule["people"]:
                            conflict_detected = True
                            conflict_messages.append(f"⚠️【人手重覆】同工「{single_name}」在 {date_str} 已經有「{each_schedule['role']}」的事奉紀錄！")

        # 寫入雲端資料庫
        data_to_save = {
            "service_date": date_str,
            "role": role,
            "content": content,
            "group_name": final_group,
            "people": people,
            "grace_notes": grace_notes,
            "record_type": type_db
        }
        
        try:
            supabase.table("service_records").insert(data_to_save).execute()
            
            # 儲存成功後，如果有衝突，就以強烈警告形式顯示在主畫面上
            if conflict_detected:
                st.sidebar.success(f"🎉 儲存成功，但系統偵測到以下排班重覆：")
                for single_msg in conflict_messages:
                    st.warning(single_msg)
            else:
                st.sidebar.success(f"🎉 成功同步一筆【{type_db}】至雲端！")
                
            st.rerun() # 刷新畫面
        except Exception as e:
            st.sidebar.error(f"❌ 儲存失敗：{e}")


# ========================================================
# 🔍 主頁面：分頁查詢系統（時間表 VS 恩典清單）
# ========================================================
tab1, tab2 = st.tabs(["📅 未來事奉人手時間表", "📜 歷史恩典紀錄與數算"])

# --------------------------------------------------------
# 頁籤一：📅 未來事奉人手時間表
# --------------------------------------------------------
with tab1:
    st.subheader("🗓️ 近期及未來事奉排班預告")
    st.caption("系統會自動篩選出今日（含）以後的事奉排班，方便同工對表。")
    
    if df_raw.empty:
        st.info("目前雲端尚無任何事奉排班資料。")
    else:
        df_schedule = df_raw[(df_raw["record_type"] == "事奉排班") & (df_raw["service_date"] >= today_str)].copy()
        
        search_sched = st.text_input("🔍 搜尋時間表 (支援不限大小寫英文字、日期片段)", placeholder="例如輸入：張弟兄、敬拜隊、2026-08...")
        if search_sched:
            k = search_sched.strip()
            df_schedule = df_schedule[
                df_schedule["service_date"].str.contains(k, case=False) |
                df_schedule["role"].str.contains(k, case=False) |
                df_schedule["group_name"].str.contains(k, case=False) |
                df_schedule["people"].str.contains(k, case=False) |
                df_schedule["content"].str.contains(k, case=False)
            ]
            
        if df_schedule.empty:
            st.warning("查無符合條件的未來事奉排班行程。")
        else:
            df_sched_disp = df_schedule.rename(columns={
                "service_date": "事奉日期",
                "role": "事奉崗位",
                "content": "服侍時段/摘要",
                "group_name": "事奉小組/團契",
                "people": "事奉人員/同工",
                "grace_notes": "備註事項"
            })
            
            st.dataframe(
                df_sched_disp[["事奉日期", "事奉崗位", "事奉小組/團契", "服侍時段/摘要", "事奉人員/同工", "備註事項"]],
                use_container_width=True
            )

# --------------------------------------------------------
# 頁籤二：📜 歷史恩典紀錄與數算
# --------------------------------------------------------
with tab2:
    st.subheader("🔍 數算與查詢恩典日記")
    
    if df_raw.empty:
        st.info("目前雲端尚無任何恩典紀錄。")
    else:
        df_grace = df_raw[df_raw["record_type"] == "恩典日記"].copy()
        df_grace = df_grace.sort_values(by="service_date", ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            search_universal = st.text_input("🔍 全方位萬用搜尋 (支援不限大小寫英文字、日期片段)", placeholder="可輸入：人名、小組、日子、感動文字...")
        with col2:
            search_role = st.selectbox("🏷️ 篩選事奉崗位", ["全部"] + roles_list)
            
        if search_role != "全部":
            df_grace = df_grace[df_grace["role"] == search_role]
        if search_universal:
            keyword = search_universal.strip()
            df_grace = df_grace[
                df_grace["service_date"].str.contains(keyword, case=False) |
                df_grace["content"].str.contains(keyword, case=False) | 
                df_grace["grace_notes"].str.contains(keyword, case=False) | 
                df_grace["people"].str.contains(keyword, case=False) | 
                df_grace["group_name"].str.contains(keyword, case=False)
            ]
            
        if df_grace.empty:
            st.warning("查無符合篩選條件的恩典日記。")
        else:
            df_grace_disp = df_grace.rename(columns={
                "service_date": "事奉日期",
                "role": "事奉崗位",
                "content": "服侍內容",
                "group_name": "所屬小組/團契",
                "people": "同行同工/人名",
                "grace_notes": "恩典與體會"
            })
            
            total_services = len(df_grace_disp)
            unique_roles = df_grace_disp["事奉崗位"].nunique() if total_services > 0 else 0
            stat_col1, stat_col2 = st.columns(2)
            stat_col1.metric("總服侍暨恩典次數", f"{total_services} 次")
            stat_col2.metric("投入崗位數", f"{unique_roles} 個")
            
            st.markdown("---")
            
            st.dataframe(
                df_grace_disp[["事奉日期", "事奉崗位", "所屬小組/團契", "服侍內容", "同行同工/人名", "恩典與體會"]],
                use_container_width=True
            )
            
            st.markdown("---")
            st.subheader("📖 恩典詳細閱讀器")
            selected_key = st.selectbox(
                "選擇要細細品味的紀錄：", 
                df_grace_disp.index, 
                format_func=lambda x: f"{df_grace_disp.loc[x, '事奉日期']} - 【{df_grace_disp.loc[x, '事奉崗位']}】 {str(df_grace_disp.loc[x, '服侍內容'])[:15]}..."
            )
if selected_key is not None:final_row = df_grace_disp.loc[selected_key]st.info(f"📅 日期： {final_row['事奉日期']}  |  🏷️ 崗位： {final_row['事奉崗位']}  |  🏘️ 小組： {final_row['所屬小組/團契']}")st.write(f"👤 同行同工： {final_row['同行同工/人名']}")st.write(f"📋 服侍摘要： {final_row['服侍內容']}")st.write("🕊️ 恩典與體會日記：")# 🌟 使用最安全的純字串讀取，完美解決網頁端的翻譯與錯字 Bugst.success(str(final_row['恩典與體會']))
