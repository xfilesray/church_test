import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 設置網頁標題與圖標
st.set_page_config(
    page_title="個人教會事奉恩典紀錄及查詢系統",
    page_icon="⛪",
    layout="wide"
)

# 初始化本地 SQLite 資料庫
def init_db():
    conn = sqlite3.connect("church_grace_web.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_date TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            grace_notes TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# 應用程式標題
st.title("⛪ 個人教會事奉恩典紀錄及查詢系統")
st.markdown("---")

# 側邊欄：新增恩典紀錄
st.sidebar.header("🌟 記錄新恩典")
with st.sidebar.form(key="grace_form", clear_on_submit=True):
    # 日期選擇器
    service_date = st.date_input("事奉日期", datetime.now())
    
    # 崗位選擇
    roles_list = ["敬拜隊/司琴", "主日學/助教", "音控/直播", "接待/司事", "小組長/牧養", "關懷/探訪", "其他"]
    role = st.selectbox("事奉崗位", roles_list)
    
    # 文字輸入
    content = st.text_input("服侍內容摘要", placeholder="例如：主日崇拜司琴、帶領小組查經...")
    grace_notes = st.text_area("恩典與體會紀錄", placeholder="寫下神在這次服侍中給您的感動、恩典或學習...", height=150)
    
    # 提交按鈕
    submit_button = st.form_submit_button(label="儲存恩典紀錄")

if submit_button:
    if not grace_notes:
        st.sidebar.error("❌ 請填寫『恩典與體會紀錄』！")
    else:
        date_str = service_date.strftime("%Y-%m-%d")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO service_records (service_date, role, content, grace_notes, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (date_str, role, content, grace_notes, now_str))
        conn.commit()
        st.sidebar.success("🎉 感謝主！恩典紀錄已成功儲存。")

# 主頁面：查詢與數算恩典
st.header("🔍 數算與查詢恩典")

# 篩選控制項
col1, col2 = st.columns(2)
with col1:
    search_keyword = st.text_input("關鍵字搜尋（服侍內容或恩典感言）", placeholder="輸入想尋找的關鍵字...")
with col2:
    search_role = st.selectbox("篩選事奉崗位", ["全部"] + roles_list)

# 從資料庫撈取資料
query = "SELECT id, service_date AS 事奉日期, role AS 事奉崗位, content AS 服侍內容, grace_notes AS 恩典與體會 FROM service_records WHERE 1=1"
params = []

if search_role != "全部":
    query += " AND role = ?"
    params.append(search_role)

if search_keyword:
    query += " AND (content LIKE ? OR grace_notes LIKE ?)"
    params.append(f"%{search_keyword}%")
    params.append(f"%{search_keyword}%")

query += " ORDER BY service_date DESC"

df = pd.read_sql_query(query, conn, params=params)

# 顯示統計數據
if not df.empty:
    st.subheader("📊 恩典統計")
    total_services = len(df)
    unique_roles = df["事奉崗位"].nunique()
    
    stat_col1, stat_col2 = st.columns(2)
    stat_col1.metric("總服侍次數", f"{total_services} 次")
    stat_col2.metric("投入崗位數", f"{unique_roles} 個")

# 顯示紀錄表格
st.subheader("📜 歷史紀錄清單")
if df.empty:
    st.info("目前尚無符合條件的恩典紀錄，快在左側寫下第一個恩典吧！")
else:
    # 隱藏資料庫內部的 ID 欄位，讓畫面更乾淨
    display_df = df.drop(columns=["id"])
    
    # 使用 Streamlit 的高互動性表格
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "恩典與體會": st.column_config.TextColumn("恩典與體會", width="large")
        }
    )
    
    # 詳細閱讀模式
    st.markdown("---")
    st.subheader("📖 恩典詳細閱讀器")
    selected_index = st.selectbox("選擇要細細品味的紀錄日期與崗位：", df.index, format_func=lambda x: f"{df.loc[x, '事奉日期']} - 【{df.loc[x, '事奉崗位']}】 {df.loc[x, '服侍內容'][:15]}...")
    
    if selected_index is not None:
        row = df.loc[selected_index]
        st.info(f"**📅 日期：** {row['事奉日期']}  |  **🏷️ 崗位：** {row['事奉崗位']}")
        if row['服侍內容']:
            st.write(f"**📋 服侍摘要：** {row['服侍內容']}")
        st.write("**🕊️ 恩典與體會日記：**")
        st.success(row['恩典與體會'])
