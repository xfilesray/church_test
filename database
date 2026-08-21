# database.py
"""
Church Ministry Management & Grace Journal System
Database Operations, Supabase Client Setup, and Business Logic
"""

import os
import re
import pandas as pd
from supabase import create_client, Client
import streamlit as st

# --- Helper Functions ---
def parse_names(raw_text: str) -> list[str]:
    """
    Parses comma-separated, space-separated, or newline-separated names
    and handles full-width and half-width Chinese punctuation.
    """
    if not raw_text:
        return []
    # Split by half-width comma, full-width comma, enumeration comma, spaces, or newlines
    tokens = re.split(r'[,，\s\n、]+', raw_text.strip())
    return [t.strip() for t in tokens if t.strip()]


# --- Supabase Client Connection ---
def get_supabase_client() -> Client:
    """
    Initializes and returns the Supabase Client.
    Supports credentials from Streamlit Secrets or Environment Variables.
    """
    url = None
    key = None

    # Check Streamlit Secrets first
    if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    else:
        # Fallback to Environment Variables
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "Missing Supabase credentials! Please set SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml or environment variables."
        )

    return create_client(url, key)


# --- Business Logic: Conflict Detection ---
def check_conflicts(supabase: Client, date_str: str, time_slot: str, room: str, personnel_text: str) -> dict:
    """
    Checks for room reservation collisions and personnel scheduling double-bookings
    for a specific date and time slot.
    
    Returns:
        dict: {
            "has_room_conflict": bool,
            "conflicting_people": list[str]
        }
    """
    # Query existing records for the same date and time slot
    response = supabase.table("church_records") \
        .select("room_name, personnel") \
        .eq("event_date", date_str) \
        .eq("time_slot", time_slot) \
        .execute()

    records = response.data if response.data else []

    # 1. Room Conflict Check
    has_room_conflict = False
    if room and room.strip():
        for rec in records:
            if rec.get("room_name") and rec["room_name"].strip() == room.strip():
                has_room_conflict = True
                break

    # 2. Personnel Conflict Check
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


# --- Database CRUD Operations ---
def save_record(supabase: Client, payload: dict) -> dict:
    """
    Inserts a new ministry record into the Supabase database.
    """
    response = supabase.table("church_records").insert(payload).execute()
    return response.data


def load_records(supabase: Client) -> pd.DataFrame:
    """
    Fetches all records from Supabase ordered by event_date descending,
    and returns them as a Pandas DataFrame.
    """
    response = supabase.table("church_records") \
        .select("*") \
        .order("event_date", desc=True) \
        .execute()

    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()
