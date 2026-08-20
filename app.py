import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# 設置網頁標題與圖標
st.set_page_config(
    page_title="個人教會事奉恩典紀錄及查詢系統",
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
st.title("⛪ 個人教會事奉恩典紀錄及查詢系統 (雲端永久版)")
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

# 自訂您教會的常用小組/團契名稱
groups_list = [
    "大衛小組",
    "約書亞青年團契",
    "迦勒長青團契",
    "喜樂家庭小組",
    "安得烈小組",
    "其他 / 請自行於下方輸入"
]

# 側邊欄：新增恩典紀錄
st.sidebar.header("🌟 記錄新恩典")
with st.sidebar.form(key="grace_form", clear_on_submit=True):
    service_date = st.date_input("事奉日期", datetime.now())
    role = st.selectbox("事奉崗位", roles_list)
    content = st.text_input("服侍內容摘要", placeholder="例如：主日崇拜司琴...")
    
    selected_group = st.selectbox("選擇小組/團契名稱", groups_list)
    custom_group = st.text_input("✍️ 若選擇『其他』，請在此輸入新小組名稱：", placeholder="例如：提摩太小組")
    
    final_group = custom_group.strip() if (selected_group == "其他 / 請自行於下方輸入" and custom_group.strip()) else selected_group
    
    people = st.text_input("同行同工 / 相關人名", placeholder="例如：陳牧師、張弟兄")
    grace_notes = st.text_area("恩典與體會紀錄", placeholder="寫下神在這次服侍中給您的感動、恩典或學習...", height=150)
    submit_button = st.form_submit_button(label="儲存恩典紀錄")

if submit_button:
    if not grace_notes:
        st.sidebar.error("❌ 請填寫『恩典與體會紀錄』！")
    else:
        date_str = service_date.strftime("%Y-%m-%d")
        data = {
            "service_date": date_str,
            "role": role,
            "content": content,
            "group_name": final_group,
            "people": people,
            "grace_notes": grace_notes
        }
        try:
            supabase.table("service_records").insert(data).execute()
            st.sidebar.success("🎉 感謝主！恩典紀錄已成功同步至雲端資料庫。")
        except Exception as e:
            st.sidebar.error(f"❌ 儲存失敗，請檢查連線：{e}")

# 主頁面：查詢與數算恩典
st.header("🔍 數算與查詢恩典")

# 🔍 搜尋與篩選控制區
col1, col2 = st.columns([3, 1])
with col1:
    # 🌟 萬用搜尋框提示文字更新，加入日期與大小寫說明
    search_universal = st.text_input("🔍 全方位萬用搜尋 (支援不限大小寫英文字、日期片段)", placeholder="可輸入：人名、小組、事奉日子(如 2026 或 -08-)、摘要或感動文字...")
with col2:
    search_role = st.selectbox("🏷️ 篩選事奉崗位", ["全部"] + roles_list)

# 從 Supabase 撈取資料
try:
    response = supabase.table("service_records").select("service_date, role, content, group_name, people, grace_notes").order("service_date", desc=True).execute()
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"讀取資料失敗：{e}")
    df_raw = pd.DataFrame()

if df_raw.empty:
    st.info("目前雲端尚無符合條件的恩典紀錄，快在左側寫下第一個恩典吧！")
else:
    df = df_raw.copy()
    
    # 填補空值並轉為字串，確保篩選不報錯
    df["service_date"] = df["service_date"].fillna("").astype(str)
    df["group_name"] = df["group_name"].fillna("").astype(str)
    df["people"] = df["people"].fillna("").astype(str)
    df["content"] = df["content"].fillna("").astype(str)
    df["grace_notes"] = df["grace_notes"].fillna("").astype(str)
    
    # 進行前端事奉崗位篩選
    if search_role != "全部":
        df = df[df["role"] == search_role]
        
    if search_universal:
        keyword = search_universal.strip()
        # 🌟 核心修改：使用 case=False 實現不限大小寫搜尋，並加入 df["service_date"] 支援日子搜尋
        df = df[
            df["service_date"].str.contains(keyword, case=False, na=False) |
            df["content"].str.contains(keyword, case=False, na=False) | 
            df["grace_notes"].str.contains(keyword, case=False, na=False) | 
            df["people"].str.contains(keyword, case=False, na=False) | 
            df["group_name"].str.contains(keyword, case=False, na=False)
        ]

    # 重新命名欄位供前端顯示
    df_display = df.rename(columns={
        "service_date": "事奉日期",
        "role": "事奉崗位",
        "content": "服侍內容",
        "group_name": "所屬小組/團契",
        "people": "同行同工/人名",
        "grace_notes": "恩典與體會"
    })

    # 顯示統計數據
    st.subheader("📊 恩典統計")
    total_services = len(df_display)
    unique_roles = df_display["事奉崗位"].nunique() if total_services > 0 else 0
    
    stat_col1, stat_col2 = st.columns(2)
    stat_col1.metric("總服侍次數", f"{total_services} 次")
    stat_col2.metric("投入崗位數", f"{unique_roles} 個")

    # 顯示紀錄表格
    st.subheader("📜 歷史紀錄清單")
    if df_display.empty:
        st.warning("查無符合篩選條件的紀錄。")
    else:
        st.dataframe(
            df_display[["事奉日期", "事奉崗位", "所屬小組/團契", "服侍內容", "同行同工/人名", "恩典與體會"]],
            use_container_width=True,
            column_config={"恩典與體會": st.column_config.TextColumn("恩典與體會", width="large")}
        )
        
        st.markdown("---")
        st.subheader("📖 恩典詳細閱讀器")
        selected_index = st.selectbox(
            "選擇要細細品味的紀錄：", 
            df_display.index, 
            format_func=lambda x: f"{df_display.loc[x, '事奉日期']} - 【{df_display.loc[x, '事奉崗位']}】 {str(df_display.loc[x, '服侍內容'])[:15]}..."
        )
        
        if selected_index is not None:
            row = df_display.loc[selected_index]
            st.info(f"**📅 日期：** {row['事奉日期']}  |  **🏷️ 崗位：** {row['事奉崗位']}  |  **🏘️ 小組：** {row['所屬小組/團契'] if row['所屬小組/團契'] else '無紀錄'}")
            st.write(f"**👤 同行同工：** {row['同行同工/人名'] if row['同行同工/人名'] else '無紀錄'}")
            if row['服侍內容']:
                st.write(f"**📋 服侍摘要：** {row['服侍內容']}")
            st.write("**🕊️ 恩典與體會日記：**")
            st.success(row['恩典與體會'])
