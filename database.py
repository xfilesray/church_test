# ==============================================================================
# File: database.py
# Description: Supabase client initialization, conflict checks, and CRUD queries.
# ==============================================================================
import os
import datetime
from typing import List, Dict, Any, Tuple
from supabase import create_client, Client

# 初始化 Supabase 客戶端 (優先從環境變數讀取)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None


# ------------------------------------------------------------------------------
# Common Utilities
# ------------------------------------------------------------------------------
def parse_workers_string(raw_input: str) -> List[str]:
    """將中英文逗號分隔的同工字串解析為獨立姓名串列，並去除空白。"""
    if not raw_input:
        return []
    normalized = raw_input.replace("，", ",")
    return [name.strip() for name in normalized.split(",") if name.strip()]


# ------------------------------------------------------------------------------
# Module A: Grace Records
# ------------------------------------------------------------------------------
def insert_grace_record(worker_name: str, ministry_item: str, reflection: str, prayer_request: str = "") -> bool:
    """寫入恩典紀錄"""
    try:
        data = {
            "worker_name": worker_name,
            "ministry_item": ministry_item,
            "reflection": reflection,
            "prayer_request": prayer_request
        }
        res = supabase.table("grace_records").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error inserting grace record: {e}")
        return False


# ------------------------------------------------------------------------------
# Module B: Venue Bookings & Conflict Detection
# ------------------------------------------------------------------------------
def check_venue_conflict(venue_name: str, booking_date: datetime.date, start_time: datetime.time, end_time: datetime.time) -> bool:
    """
    檢查場地預約時間衝突 (StartA < EndB AND EndA > StartB)
    """
    try:
        res = supabase.table("venue_bookings") \
            .select("*") \
            .eq("venue_name", venue_name) \
            .eq("booking_date", booking_date.isoformat()) \
            .execute()

        for booking in res.data:
            b_start = datetime.datetime.strptime(booking["start_time"], "%H:%M:%S").time()
            b_end = datetime.datetime.strptime(booking["end_time"], "%H:%M:%S").time()

            if start_time < b_end and end_time > b_start:
                return True # 發現重疊衝突
        return False
    except Exception as e:
        print(f"Error checking venue conflict: {e}")
        return False


def insert_venue_booking(venue_name: str, applicant_name: str, purpose: str, booking_date: datetime.date, start_time: datetime.time, end_time: datetime.time, notes: str = "") -> bool:
    """寫入場地預約紀錄"""
    try:
        data = {
            "venue_name": venue_name,
            "applicant_name": applicant_name,
            "purpose": purpose,
            "booking_date": booking_date.isoformat(),
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
            "notes": notes
        }
        res = supabase.table("venue_bookings").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error inserting venue booking: {e}")
        return False


# ------------------------------------------------------------------------------
# Module C: Ministry Roster & Conflict Detection
# ------------------------------------------------------------------------------
def check_roster_conflicts(service_date: datetime.date, roles_map: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
    """
    同時檢查單次表單內重複指派與雲端資料庫同日跨紀錄衝突。
    回傳: (self_conflicts, db_conflicts)
    """
    self_conflicts = []
    db_conflicts = []

    # 1. 檢查表單內部重複
    worker_counts = {}
    for role, workers in roles_map.items():
        for worker in workers:
            worker_counts[worker] = worker_counts.get(worker, 0) + 1
            if worker_counts[worker] > 1 and worker not in self_conflicts:
                self_conflicts.append(worker)

    # 2. 檢查雲端資料庫跨紀錄衝突
    try:
        res = supabase.table("roster_schedules") \
            .select("*") \
            .eq("service_date", service_date.isoformat()) \
            .execute()

        all_input_workers = set([w for workers in roles_map.values() for w in workers])
        
        for record in res.data:
            db_workers_in_record = set()
            for col in ["worship_leader", "speaker", "sound_av", "usher", "sunday_school", "other_roles"]:
                if record.get(col):
                    db_workers_in_record.update(parse_workers_string(record[col]))
            
            overlap = all_input_workers.intersection(db_workers_in_record)
            for w in overlap:
                if w not in db_conflicts:
                    db_conflicts.append(w)
    except Exception as e:
        print(f"Error checking roster conflicts: {e}")

    return self_conflicts, db_conflicts


def insert_roster_schedule(service_date: datetime.date, service_type: str, roles_map: Dict[str, str], notes: str = "", is_force_saved: bool = False) -> bool:
    """寫入事奉排班紀錄"""
    try:
        data = {
            "service_date": service_date.isoformat(),
            "service_type": service_type,
            "worship_leader": roles_map.get("worship_leader", ""),
            "speaker": roles_map.get("speaker", ""),
            "sound_av": roles_map.get("sound_av", ""),
            "usher": roles_map.get("usher", ""),
            "sunday_school": roles_map.get("sunday_school", ""),
            "other_roles": roles_map.get("other_roles", ""),
            "notes": notes,
            "is_force_saved": is_force_saved
        }
        res = supabase.table("roster_schedules").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error inserting roster schedule: {e}")
        return False


# ------------------------------------------------------------------------------
# Module D: Dynamic Worker Management & Global Search
# ------------------------------------------------------------------------------
def fetch_church_workers() -> List[str]:
    """動態讀取所有在籍同工名單"""
    try:
        res = supabase.table("workers") \
            .select("name") \
            .eq("status", "在籍 (Active)") \
            .order("name") \
            .execute()
        return [row["name"] for row in res.data] if res.data else []
    except Exception as e:
        print(f"Error fetching workers: {e}")
        return []


def add_church_worker(name: str, primary_role: str = "一般同工") -> bool:
    """新增同工至名單"""
    if not name or not name.strip():
        return False
    try:
        payload = {"name": name.strip(), "primary_role": primary_role, "status": "在籍 (Active)"}
        res = supabase.table("workers").upsert(payload, on_conflict="name").execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"Error adding worker: {e}")
        return False


def fetch_all_workers_details() -> List[Dict[str, Any]]:
    """取得所有同工完整明細"""
    try:
        res = supabase.table("workers").select("*").order("name").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error fetching worker details: {e}")
        return []


def search_all_records(keyword: str, module_filter: str = "全部模組") -> Dict[str, List[Dict[str, Any]]]:
    """
    全欄位不限大小寫 (Case-Insensitive) 跨模組模糊搜尋
    """
    results = {"grace_records": [], "venue_bookings": [], "roster_schedules": []}
    if not keyword or not keyword.strip():
        return results

    kw = keyword.strip()

    try:
        # 1. 搜尋恩典紀錄
        if module_filter in ["全部模組", "恩典紀錄"]:
            res = supabase.table("grace_records") \
                .select("*") \
                .or_(f"worker_name.ilike.%{kw}%,ministry_item.ilike.%{kw}%,reflection.ilike.%{kw}%,prayer_request.ilike.%{kw}%") \
                .execute()
            results["grace_records"] = res.data or []

        # 2. 搜尋場地預約
        if module_filter in ["全部模組", "場地預約"]:
            res = supabase.table("venue_bookings") \
                .select("*") \
                .or_(f"venue_name.ilike.%{kw}%,applicant_name.ilike.%{kw}%,purpose.ilike.%{kw}%,notes.ilike.%{kw}%") \
                .execute()
            results["venue_bookings"] = res.data or []

        # 3. 搜尋事奉排班
        if module_filter in ["全部模組", "事奉排班"]:
            res = supabase.table("roster_schedules") \
                .select("*") \
                .or_(f"service_type.ilike.%{kw}%,worship_leader.ilike.%{kw}%,speaker.ilike.%{kw}%,sound_av.ilike.%{kw}%,usher.ilike.%{kw}%,sunday_school.ilike.%{kw}%,other_roles.ilike.%{kw}%,notes.ilike.%{kw}%") \
                .execute()
            results["roster_schedules"] = res.data or []

    except Exception as e:
        print(f"Error during search: {e}")

    return results
