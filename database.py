# database.py
"""
Church Ministry Management & Grace Journal System
Database Operations, Supabase Client Setup, and Business Logic
"""

import os
import re
import pandas as pd
from supabase import create_client, Client
from postgrest.exceptions import APIError
import streamlit as st

def parse_names(raw_text: str) -> list[str]:
    """解析以逗號、頓點、換行或空格分隔的同工姓名"""
    if not raw_text:
        return []
    tokens = re.split(r'[,，\s\n、]+', raw_text.strip())
    return [t.strip() for t in tokens if t.strip()]

def get_supabase_client() -> Client:
    """初始化 Supabase 客戶端"""
    url = None
    key = None

    if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    else:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("未設定 SUPABASE_URL 與 SUPABASE_KEY！請檢查 secrets.toml 或環境變數。")

    return create_client(url, key)

def check_conflicts(supabase: Client, date_str: str, time_slot: str, room: str, personnel_text: str) -> dict:
    """檢查場地與同工排班衝突"""
    try:
        response = supabase.table("church_records") \
            .select("room_name, personnel") \
            .eq("event_date", date_str) \
            .eq("time_slot", time_slot) \
            .execute()
        records = response.data if response.data else []
    except Exception as err:
        st.error(f"⚠️ 防衝突檢查失敗 (查詢時發生錯誤): {err}")
        records = []

    has_room_conflict = False
    if room and room.strip():
        for rec in records:
            if rec.get("room_name") and rec["room_name"].strip() == room.strip():
                has_room_conflict = True
                break

    input_names = set(parse_names(personnel_text))
    conflicting_people = []
    if input_names:
        for rec in records:
            existing_names = set(parse_names(rec.get("personnel", "")))
            overlap = input_names.intersection(existing_names)
            if overlap:
                conflicting_people.extend(list(overlap))

    return {
        "has_room_conflict": has_room_conflict,
        "conflicting_people": list(set(conflicting_people))
    }

def save_record(supabase: Client, payload: dict) -> dict:
    """新增資料至 Supabase (附帶詳細 API 異常捕捉)"""
    try:
        response = supabase.table("church_records").insert(payload).execute()
        return response.data
    except APIError as api_err:
        # 印出 API 詳細錯誤，便於排查
        st.error(f"❌ Supabase API 拒絕存取 Details: {api_err.message} (Code: {api_err.code})")
        raise api_err
    except Exception as err:
        st.error(f"❌ 寫入資料庫時發生未預期錯誤: {err}")
        raise err

def load_records(supabase: Client) -> pd.DataFrame:
    """讀取所有歷史紀錄"""
    try:
        response = supabase.table("church_records") \
            .select("*") \
            .order("event_date", desc=True) \
            .execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as err:
        st.error(f"❌ 讀取歷史紀錄失敗: {err}")
        return pd.DataFrame()
