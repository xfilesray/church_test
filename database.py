# -*- coding: utf-8 -*-
"""
database.py - 處理 Supabase 資料庫連線、CRUD 操作與衝突檢測 logic
"""

import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# 初始化 Supabase 連線 (從 secrets 或環境變數讀取)
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("❌ 未設定 Supabase URL 或 Key！請檢查 .streamlit/secrets.toml")
        st.stop()
        
    return create_client(url, key)

supabase = init_supabase()

# ==========================================
# 模組 A: 恩典與體會紀錄 (Grace Logs)
# ==========================================
def save_grace_log(event_date, time_slot, worker_name, gifts, reflection, prayer):
    """新增恩典紀錄"""
    data = {
        "event_date": str(event_date),
        "time_slot": time_slot,
        "worker_name": worker_name,
        "spiritual_gifts": gifts,
        "reflection": reflection,
        "prayer_requests": prayer
    }
    res = supabase.table("grace_logs").insert(data).execute()
    return res

# ==========================================
# 模組 B: 場地借用 (Venue Bookings & Conflicts)
# ==========================================
def check_venue_conflict(event_date, time_slot, venue_name):
    """檢查同日期、同時間、同場地是否已被預約"""
    res = supabase.table("venue_bookings") \
        .select("*") \
        .eq("event_date", str(event_date)) \
        .eq("time_slot", time_slot) \
        .eq("venue_name", venue_name) \
        .execute()
    
    return len(res.data) > 0

def save_venue_booking(event_date, time_slot, venue_name, applicant, purpose, is_forced=False):
    """寫入場地預約"""
    data = {
        "event_date": str(event_date),
        "time_slot": time_slot,
        "venue_name": venue_name,
        "applicant_name": applicant,
        "event_purpose": purpose,
        "is_forced": is_forced
    }
    res = supabase.table("venue_bookings").insert(data).execute()
    return res

# ==========================================
# 模組 C: 事奉時間表 (Ministry Rosters & Conflicts)
# ==========================================
def check_roster_conflict(event_date, time_slot, worker_list):
    """檢查同工在同一時段是否已在其他排班中被指派"""
    if not worker_list:
        return []
        
    # 查詢同日期同時間已存在的排班
    res = supabase.table("ministry_rosters") \
        .select("all_workers") \
        .eq("event_date", str(event_date)) \
        .eq("time_slot", time_slot) \
        .execute()
    
    conflicted_workers = set()
    for row in res.data:
        existing_workers = row.get("all_workers") or []
        for worker in worker_list:
            if worker in existing_workers:
                conflicted_workers.add(worker)
                
    return list(conflicted_workers)

def save_ministry_roster(event_date, time_slot, roles_dict, all_workers, is_forced=False):
    """儲存/更新事奉時間表"""
    data = {
        "event_date": str(event_date),
        "time_slot": time_slot,
        "worship_lead": roles_dict.get("worship_lead", ""),
        "speaker": roles_dict.get("speaker", ""),
        "av_team": roles_dict.get("av_team", ""),
        "usher_team": roles_dict.get("usher_team", ""),
        "sunday_school": roles_dict.get("sunday_school", ""),
        "other_roles": roles_dict.get("other_roles", ""),
        "all_workers": all_workers,
        "is_forced": is_forced
    }
    res = supabase.table("ministry_rosters").insert(data).execute()
    return res
    
# ------------------------------------------
# Module D: Search Logic
# ------------------------------------------
def query_records(table_name: str, keyword: str = "", start_date=None, end_date=None) -> pd.DataFrame:
    """跨模組動態查詢邏輯，支援 Python 端的 case=False 模糊比對與日期過濾"""
    query = supabase.table(table_name).select("*")
    
    # 執行資料庫查詢
    response = query.execute()
    data = response.data
    
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    
    # 日期區間過濾
    date_col = "created_at" if "created_at" in df.columns else ("booking_date" if "booking_date" in df.columns else "service_date")
    if date_col in df.columns and (start_date or end_date):
        df[date_col] = pd.to_datetime(df[date_col]).dt.date
        if start_date:
            df = df[df[date_col] >= start_date]
        if end_date:
            df = df[df[date_col] <= end_date]
            
    # 全欄位關鍵字不限大小寫比對 (case=False)
    if keyword.strip():
        kw = keyword.strip().lower()
        mask = df.astype(str).apply(lambda row: row.str.lower().str.contains(kw, na=False)).any(axis=1)
        df = df[mask]
        
    return df

# ------------------------------------------
# Module D: Worker Management Logic
# ------------------------------------------
def get_all_workers() -> pd.DataFrame:
    """取得完整同工清單"""
    res = supabase.table("workers").select("*").order("name").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def add_worker(name: str, primary_role: str, status: str = "在籍 (Active)") -> bool:
    """新增同工紀錄"""
    payload = {"name": name.strip(), "primary_role": primary_role, "status": status}
    res = supabase.table("workers").insert(payload).execute()
    return len(res.data) > 0

def update_worker_status(worker_id: int, new_status: str) -> bool:
    """更新指定同工狀態"""
    res = supabase.table("workers").update({"status": new_status}).eq("id", worker_id).execute()
    return len(res.data) > 0

def delete_worker(worker_id: int) -> bool:
    """刪除指定同工"""
    res = supabase.table("workers").delete().eq("id", worker_id).execute()
    return len(res.data) > 0
