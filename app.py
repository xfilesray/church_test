import constants as c
from datetime import datetime, time
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# 頁面配置
st.set_page_config(page_title=c.PAGE_TITLE, page_icon="⛪", layout="wide")

# Supabase 初始化
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    @st.cache_resource
    def get_supabase_client() -> Client:
        return create_client(SUPABASE_URL, SUPABASE_KEY)

    supabase = get_supabase_client()
else:
    st.error("缺少 Supabase 金鑰設定 (Secrets Missing)。")
    st.stop()

# 初始化頁籤狀態
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = c.TABS[0]

st.title(c.MAIN_TITLE)
st.markdown("---")

# 側邊欄 - 資料輸入表單
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

    # 通用欄位：選擇小組
    sel_group = st.selectbox("請選擇小組/單位", c.GROUPS)
    if sel_group == c.OTHER_CUSTOM_TRIGGER:
        final_group = st.text_input(
            "自訂小組/單位名稱", placeholder="請輸入小組名稱..."
        )
    else:
        final_group = sel_group

    if selected_type_key == "ROOMS":
        sel_room = st.selectbox("請選擇場地/房間", c.ROOMS)
        if sel_room == c.OTHER_CUSTOM_TRIGGER:
            final_room = st.text_input(
                "自訂場地/房間名稱", placeholder="請輸入場地名稱..."
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
        sel_role = st.selectbox("請選擇事奉崗位", c.ROLES)
        if sel_role == c.OTHER_CUSTOM_TRIGGER:
            role = st.text_input(
                "自訂崗位名稱", placeholder="請輸入崗位名稱..."
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

# 讀取雲端資料
try:
    response = (
        supabase.table("service_records")
        .select(
            "service_date, service_time, role, content, group_name, people, grace_notes, record_type, room_name"
        )
        .order("service_date", desc=False)
        .execute()
    )
    df_raw = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"讀取資料失敗：{e}")
    df_raw = pd.DataFrame()

# 資料清理與格式化
if not df_raw.empty:
    df_raw["record_type"] = df_raw["record_type"].fillna("DIARY").astype(str)
    df_raw["service_date"] = df_raw["service_date"].fillna("").astype(str)
    df_raw["service_time"] = df_raw["service_time"].fillna("00:00").astype(str)
    df_raw["role"] = df_raw["role"].fillna("").astype(str)
    df_raw["group_name"] = df_raw["group_name"].fillna("").astype(str)
    df_raw["people"] = df_raw["people"].fillna("").astype(str)
    df_raw["content"] = df_raw["content"].fillna("").astype(str)
    df_raw["grace_notes"] = df_raw["grace_notes"].fillna("").astype(str)
    df_raw["room_name"] = df_raw["room_name"].fillna("").astype(str)


def save_to_supabase(
    d_str, t_str, r_str, c_str, g_str, p_str, n_str, type_str, rm_str
):
    insert_data = {
        "service_date": d_str,
        "service_time": t_str,
        "role": r_str,
        "content": c_str,
        "group_name": g_str,
        "people": p_str,
        "grace_notes": n_str,
        "record_type": type_str,
        "room_name": rm_str,
    }
    try:
        supabase.table("service_records").insert(insert_data).execute()
        st.success("🎉 資料已成功儲存！")

        # 自動切換分頁
        if type_str == "SCHEDULE":
            st.session_state["active_tab"] = c.TABS[0]
        elif type_str == "ROOMS":
            st.session_state["active_tab"] = c.TABS[1]
        else:
            st.session_state["active_tab"] = c.TABS[2]

        st.session_state.pop("c_m", None)
        st.session_state.pop("p_d", None)

        import time as t_mod

        t_mod.sleep(0.8)
        st.rerun()
    except Exception as save_err:
        st.error(f"儲存失敗：{save_err}")


# 重複與撞期防錯檢查邏輯
if submit_button:
    date_str = s_date.strftime("%Y-%m-%d")
    conflict_detected = False
    conflict_msg = []

    if not df_raw.empty:
        # 1. 場地撞期檢查
        if final_room.strip():
            same_room_time = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
                & (df_raw["room_name"] == final_room.strip())
            ]
            if not same_room_time.empty:
                conflict_detected = True
                conflict_msg.append(
                    f"⚠️ 場地衝突：場地 [{final_room.strip()}] 在 {date_str} {time_str} 已被預約！"
                )

        # 2. 同工重複排班檢查
        if people.strip():
            input_names = [
                n.strip()
                for n in people.replace("，", ",").split(",")
                if n.strip()
            ]
            day_time_records = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
            ]
            for name in input_names:
                for idx, row in day_time_records.iterrows():
                    existing_people = [
                        p.strip()
                        for p in str(row["people"]).replace("，", ",").split(",")
                        if p.strip()
                    ]
                    if name in existing_people:
                        conflict_detected = True
                        conflict_msg.append(
                            f"⚠️ 人員衝突：同工 [{name}] 在 {date_str} {time_str} 已有其他事奉/借用紀錄！"
                        )

        # 3. 事奉崗位重複檢查
        if selected_type_key == "SCHEDULE" and role.strip():
            same_time_role = df_raw[
                (df_raw["service_date"] == date_str)
                & (df_raw["service_time"] == time_str)
                & (df_raw["role"] == role.strip())
                & (df_raw["record_type"] == "SCHEDULE")
            ]
            if not same_time_role.empty:
                conflict_detected = True
                conflict_msg.append(
                    f"⚠️ 崗位衝突：崗位 [{role.strip()}] 在 {date_str} {time_str} 已安排人員！"
                )

    if conflict_detected:
        st.session_state["c_m"] = conflict_msg
        st.session_state["p_d"] = (
            date_str,
            time_str,
            role,
            content,
            final_group,
            people,
            grace_notes,
            selected_type_key,
            final_room,
        )
    else:
        save_to_supabase(
            date_str,
            time_str,
            role,
            content,
            final_group,
            people,
            grace_notes,
            selected_type_key,
            final_room,
        )

# 衝突提示與強制儲存彈窗
if "c_m" in st.session_state:
    st.error("🚨 偵測到預約/排班衝突：")
    for msg in st.session_state["c_m"]:
        st.warning(msg)
    col_ok, col_no = st.columns(2)
    with col_ok:
        if st.button("⚠️ 強制寫入/儲存", type="primary"):
            p1, p2, p3, p4, p5, p6, p7, p8, p9 = st.session_state["p_d"]
            save_to_supabase(p1, p2, p3, p4, p5, p6, p7, p8, p9)
    with col_no:
        if st.button("❌ 取消"):
            st.session_state.pop("c_m", None)
            st.session_state.pop("p_d", None)
            st.rerun()

# 主展示區分頁控制
selected_tab = st.radio(
    "",
    options=c.TABS,
    index=c.TABS.index(st.session_state.get("active_tab", c.TABS[0])),
    key="tab_selector",
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state["active_tab"] = selected_tab
st.markdown("---")

today_str = datetime.now().strftime("%Y-%m-%d")

# 全欄位搜尋函式
def filter_all_columns(df, query):
    if not query:
        return df
    # 檢查每一行的所有欄位，只要有任何一個欄位包含搜尋關鍵字即保留
    mask = df.astype(str).apply(
        lambda row: row.str.contains(query, case=False, na=False).any(), axis=1
    )
    return df[mask]


# 分頁 1: 未來事奉排班
if selected_tab == c.TABS[0]:
    st.subheader(c.TABS[0])
    if df_raw.empty:
        st.info("目前尚無資料。")
    else:
        df_s = (
            df_raw[
                (df_raw["record_type"] == "SCHEDULE")
                & (df_raw["service_date"] >= today_str)
            ]
            .copy()
            .sort_values(by=["service_date", "service_time"])
        )
        
        # 重新命名欄位以便呈現與搜尋
        df_s_disp = df_s.rename(columns=c.DF_COL_MAP_SCHEDULE)[
            list(c.DF_COL_MAP_SCHEDULE.values())
        ]
        
        q_s = st.text_input("🔍 搜尋事奉排班（可搜尋所有欄位）：", placeholder="輸入任意關鍵字（日期、崗位、姓名、備註...）")
        if q_s:
            df_s_disp = filter_all_columns(df_s_disp, q_s)

        st.dataframe(df_s_disp, use_container_width=True)

# 分頁 2: 場地借用管理
elif selected_tab == c.TABS[1]:
    st.subheader(c.TABS[1])
    if df_raw.empty:
        st.info("目前尚無資料。")
    else:
        df_r = (
            df_raw[
                (df_raw["record_type"] == "ROOMS")
                & (df_raw["service_date"] >= today_str)
            ]
            .copy()
            .sort_values(by=["service_date", "service_time"])
        )
        
        df_r_disp = df_r.rename(columns=c.DF_COL_MAP_ROOMS)[
            list(c.DF_COL_MAP_ROOMS.values())
        ]
        
        q_r = st.text_input("🔍 搜尋場地預約（可搜尋所有欄位）：", placeholder="輸入任意關鍵字（日期、場地、小組、負責人...）")
        if q_r:
            df_r_disp = filter_all_columns(df_r_disp, q_r)

        st.dataframe(df_r_disp, use_container_width=True)

# 分頁 3: 恩典體會日記
elif selected_tab == c.TABS[2]:
    st.subheader(c.TABS[2])
    if df_raw.empty:
        st.info("目前尚無資料。")
    else:
        df_g = (
            df_raw[df_raw["record_type"] == "DIARY"]
            .copy()
            .sort_values(by="service_date", ascending=False)
        )
        
        df_g_disp = df_g.rename(columns=c.DF_COL_MAP_DIARY)[
            list(c.DF_COL_MAP_DIARY.values())
        ]
        
        q_g = st.text_input("🔍 搜尋恩典日記（可搜尋所有欄位）：", placeholder="輸入任意關鍵字（日期、同工、心得、摘要...）")
        if q_g:
            df_g_disp = filter_all_columns(df_g_disp, q_g)

        st.dataframe(df_g_disp, use_container_width=True)
        st.markdown("---")

        if not df_g_disp.empty:
            selected_key = st.selectbox(
                "請選擇欲查看詳細內容的紀錄：",
                df_g_disp.index,
                format_func=lambda x: f"{df_g_disp.loc[x, '日期']} - {df_g_disp.loc[x, '崗位']}",
            )
            if selected_key is not None:
                f_row = df_g_disp.loc[selected_key]
                st.info(
                    f"詳細資訊：{f_row['日期']} {f_row['時間']} | {f_row['崗位']} | {f_row['所屬小組']}"
                )
                st.write(f"同行同工：{f_row['同行同工']}")
                st.write(f"事奉摘要：{f_row['摘要']}")
                st.success(f"恩典體會：\n{f_row['恩典體會']}")
