import constants as c
from datetime import datetime, time
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ... 前段 Supabase 初始化與讀取資料 df_raw 保持不變 ...

# ----------------------------------------------------
# 🔄 動態提取下拉選單選項（基礎選項 + 雲端歷史新新增選項）
# ----------------------------------------------------
def get_dynamic_options(base_options, raw_df, column_name):
    # 預設基礎選單（先移除 "其他" 觸發詞以進行合併）
    clean_base = [x for x in base_options if x != c.OTHER_CUSTOM_TRIGGER]
    
    # 從雲端歷史紀錄抓取已輸入過的自訂名稱
    db_options = []
    if not raw_df.empty and column_name in raw_df.columns:
        db_options = raw_df[column_name].dropna().unique().tolist()
    
    # 合併並去重，確保不重複，最後再加上 "其他 / 請自行於下方輸入"
    all_options = []
    for opt in clean_base + db_options:
        opt_str = str(opt).strip()
        if opt_str and opt_str not in all_options and opt_str != "場地借用":
            all_options.append(opt_str)
            
    all_options.append(c.OTHER_CUSTOM_TRIGGER)
    return all_options

# 動態生成最新的選單清單
dynamic_groups = get_dynamic_options(c.GROUPS, df_raw, "group_name")
dynamic_roles = get_dynamic_options(c.ROLES, df_raw, "role")
dynamic_rooms = get_dynamic_options(c.ROOMS, df_raw, "room_name")


# ----------------------------------------------------
# 📋 側邊欄 - 資料輸入表單
# ----------------------------------------------------
st.sidebar.header("📋 資料輸入表單")

selected_type_key = st.sidebar.radio(
    "請選擇紀錄類型：",
    c.RECORD_TYPE_KEYS,
    format_func=lambda x: c.RECORD_TYPE_MAP[x],
)

with st.sidebar.form(key="f_main", clear_on_submit=False):
    s_date = st.date_input("日期", datetime.now())
    t_in = st.time_input("時間", time(9, 30))
    time_str = t_in.strftime("%H:%M")

    # 動態選單：選擇小組
    sel_group = st.selectbox("請選擇小組/單位", dynamic_groups)
    if sel_group == c.OTHER_CUSTOM_TRIGGER:
        final_group = st.text_input(
            "自訂小組/單位名稱", placeholder="請輸入新小組名稱..."
        )
    else:
        final_group = sel_group

    if selected_type_key == "ROOMS":
        # 動態選單：選擇場地
        sel_room = st.selectbox("請選擇場地/房間", dynamic_rooms)
        if sel_room == c.OTHER_CUSTOM_TRIGGER:
            final_room = st.text_input(
                "自訂場地/房間名稱", placeholder="請輸入新場地名稱..."
            )
        else:
            final_room = sel_room

        role = "場地借用"
        content = st.text_input(
            "使用用途摘要", placeholder="例如：青年詩班練習"
        )
        people = st.text_input("聯絡負責人", placeholder="例如：張小明")
        grace_notes = st.text_area(
            "器材需求 / 備註", placeholder="需使用投影機、麥克風...", height=100
        )

    else:
        final_room = ""
        # 動態選單：選擇崗位
        sel_role = st.selectbox("請選擇事奉崗位", dynamic_roles)
        if sel_role == c.OTHER_CUSTOM_TRIGGER:
            role = st.text_input(
                "自訂崗位名稱", placeholder="請輸入新崗位名稱..."
            )
        else:
            role = sel_role

        content = st.text_input(
            "事奉/聚會內容摘要", placeholder="例如：主日敬拜聚會"
        )
        people = st.text_input(
            "事奉同工姓名", placeholder="例如：陳大衛, 林雅各（多位請用逗號分開）"
        )
        grace_notes = st.text_area(
            "恩典體會 / 禱告事項 / 備註", placeholder="在此寫下服侍心得或禱告事項...", height=150
        )

    submit_button = st.form_submit_button(label="💾 儲存至雲端")
