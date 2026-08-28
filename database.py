# -*- coding: utf-8 -*-
"""
database.py - 專責 Supabase (PostgreSQL) CRUD 與衝突檢測
"""

import os
import re
import pandas as pd
from typing import List, Dict, Tuple
from supabase import create_client, Client

# Supabase 初始化
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL 及 Key 未設定，請配置環境變數。")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ── 輔助函式：分隔解析多位同工 ──
def parse_worker_names(name_string: str) -> List[str]:
    """解析以中英文逗號或頓號分隔的同工姓名，並去除空白與空值"""
    if not name_string:
        return []
    names = re.split(r'[,，、]', name_string)
    return [name.strip() for name in names if name.strip()]

# ── 模組 A：恩典紀錄 ──
def save_grace_record(date_str: str, time_slot: str, worker_name: str, gift: str, reflection: str, prayer: str) -> bool:
    supabase = get_client()
    data = {
        "event_date": date_str,
        "time_slot": time_slot,
        "worker_name": worker_name,
        "gift_item": gift,
        "reflection": reflection,
        "prayer_item": prayer
    }
    res = supabase.table("grace_records").insert(data).execute()
    return len(res.data) > 0

# ── 模組 B：場地防撞檢查與儲存 ──
def check_venue_conflict(date_str: str, time_slot: str, venue: str) -> Tuple[bool, List[Dict]]:
    """檢查場地在相同日期與時段是否已被預約"""
    supabase = get_client()
    res = supabase.table("venue_bookings") \
        .select("*") \
        .eq("event_date", date_str) \
        .eq("time_slot", time_slot) \
        .eq("venue_name", venue) \
        .execute()
    has_conflict = len(res.data) > 0
    return has_conflict, res.data

def save_venue_booking(date_str: str, time_slot: str, venue: str, applicant: str, purpose: str) -> bool:
    supabase = get_client()
    data = {
        "event_date": date_str,
        "time_slot": time_slot,
        "venue_name": venue,
        "applicant": applicant,
        "purpose": purpose
    }
    res = supabase.table("venue_bookings").insert(data).execute()
    return len(res.data) > 0

# ── 模組 C：排班重複檢查與儲存 ──
def check_roster_conflict(date_str: str, time_slot: str, current_roles: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    檢查：
    1. 表單內部是否有同一同工兼任多職
    2. 雲端資料庫同日同場次是否已有該同工的事奉排班
    """
    warnings = []
    
    # 1. 表單內部重覆性檢測
    all_workers = []
    role_mapping = {}
    for role, names_str in current_roles.items():
        parsed = parse_worker_names(names_str)
        for name in parsed:
            if name in role_mapping:
                warnings.append(f"同工【{name}】在本次排班中同時擔任「{role_mapping[name]}」與「{role}」")
            else:
                role_mapping[name] = role
            all_workers.append(name)

    # 2. 雲端資料庫跨紀錄檢測
    if all_workers:
        supabase = get_client()
        res = supabase.table("roster_records") \
            .select("roles_data") \
            .eq("event_date", date_str) \
            .eq("time_slot", time_slot) \
            .execute()
        
        for record in res.data:
            existing_roles = record.get("roles_data", {})
            for role, names_str in existing_roles.items():
                existing_names = parse_worker_names(str(names_str))
                for w in set(all_workers):
                    if w in existing_names:
                        warnings.append(f"同工【{w}】在資料庫同日同場次已有排班記錄（崗位：{role}）")

    return len(warnings) > 0, warnings

def save_roster_record(date_str: str, time_slot: str, roles_data: Dict[str, str]) -> bool:
    supabase = get_client()
    data = {
        "event_date": date_str,
        "time_slot": time_slot,
        "roles_data": roles_data
    }
    res = supabase.table("roster_records").insert(data).execute()
    return len(res.data) > 0

# ── 模組 D：不限大小寫 & 跨中英文關鍵字查詢 ──
# ── database.py ──
from postgrest.exceptions import APIError

def query_records(table_name: str, keyword: str = "", start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    查詢指定資料表紀錄，支援日期區間與 Pandas 層級的全欄位不限大小寫搜尋。
    包含 PostgREST APIError 異常處理機制。
    """
    try:
        supabase = get_client()
        query = supabase.table(table_name).select("*")
        
        # 僅在有指定日期時加入篩選條件
        if start_date:
            query = query.gte("event_date", start_date)
        if end_date:
            query = query.lte("event_date", end_date)
            
        res = query.execute()
        df = pd.DataFrame(res.data)
        
        if df.empty:
            return pd.DataFrame()
        
        # 跨欄位 case=False 關鍵字模糊搜尋
        if keyword and keyword.strip():
            kw = keyword.strip().lower()
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(kw, regex=False).any(), axis=1)
            df = df[mask]
            
        return df

    except APIError as e:
        # 捕捉 Supabase PostgREST API 報錯（如 RLS 擋住、表名或欄位不存在）
        print(f"[Supabase APIError] Table: {table_name}, Details: {e}")
        # 回傳帶有錯誤標記的空 DataFrame，讓前端提示使用者
        return pd.DataFrame({"error": [f"資料庫查詢失敗 (APIError)：請檢查 Supabase 是否已建立【{table_name}】資料表或已設定 RLS 存取權限。"]})
    except Exception as e:
        print(f"[Unexpected Error]: {e}")
        return pd.DataFrame({"error": [f"系統發生未預期錯誤：{str(e)}"]})

# ── database.py ──

# 新增：撈取活躍同工名單 (供下拉選單選取)
def get_active_worker_names() -> List[str]:
    """取得目前系統中狀態為啟用 (Active) 的同工姓名列表"""
    try:
        supabase = get_client()
        res = supabase.table("workers").select("name").eq("status", "Active").execute()
        if res.data:
            return [w["name"] for w in res.data if w.get("name")]
        return []
    except Exception:
        # 若資料庫尚未建立 workers 表，回傳預設空清單
        return []

# 修正：支援列表與字串格式的排班防撞檢查
def check_roster_conflict(date_str: str, time_slot: str, current_roles: Dict[str, any]) -> Tuple[bool, List[str]]:
    """
    檢查：
    1. 表單內部是否有同一同工兼任多職 (接受 List[str] 或逗號分隔字串)
    2. 雲端資料庫同日同場次是否已有該同工的事奉排班
    """
    warnings = []
    
    # 1. 表單內部重複性檢測
    role_mapping = {}
    all_workers = []
    
    for role, value in current_roles.items():
        # 自動適應 List 或 String 輸入
        if isinstance(value, list):
            parsed = value
        else:
            parsed = parse_worker_names(str(value))
            
        for name in parsed:
            if not name:
                continue
            if name in role_mapping:
                warnings.append(f"同工【{name}】在本次排班中同時擔任「{role_mapping[name]}」與「{role}」")
            else:
                role_mapping[name] = role
            all_workers.append(name)

    # 2. 雲端資料庫跨紀錄檢測
    if all_workers:
        try:
            supabase = get_client()
            res = supabase.table("roster_records") \
                .select("roles_data") \
                .eq("event_date", date_str) \
                .eq("time_slot", time_slot) \
                .execute()
            
            for record in res.data:
                existing_roles = record.get("roles_data", {})
                for role, names_val in existing_roles.items():
                    if isinstance(names_val, list):
                        existing_names = names_val
                    else:
                        existing_names = parse_worker_names(str(names_val))
                    
                    for w in set(all_workers):
                        if w in existing_names:
                            warnings.append(f"同工【{w}】在資料庫同日同場次已有排班記錄（崗位：{role}）")
        except Exception as e:
            pass

    return len(warnings) > 0, warnings
