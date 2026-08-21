import datetime
import re
import pandas as pd
import streamlit as st
from supabase import create_client, Client
import constants as c

# ------------------------------------------------------------------------------
# 1. Page Configuration & Supabase Initialization
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title=c.TITLE_APP,
    page_icon="⛪",
    layout="wide"
)

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client connection using secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as err:
    st.error(f"{c.ERR_DB_CONN}: {err}")
    st.stop()

# ------------------------------------------------------------------------------
# 2. Helper Functions
# ------------------------------------------------------------------------------
def parse_names(name_string: str) -> list[str]:
    """Parse string into a clean list of individual names (supports Chinese/English commas)."""
    if not name_string:
        return []
    # Split by Chinese comma '，', English comma ',', or whitespace
    raw_names = re.split(r'[,，\s]+', name_string)
    return [name.strip() for name in raw_names if name.strip()]

def check_schedule_conflicts(event_date: str, group_name: str, new_volunteers: list[str]) -> list[str]:
    """Check if any volunteer is already scheduled on the same date."""
    if not new_volunteers:
        return []
    
    response = supabase.table("schedules") \
        .select("volunteers, group_name") \
        .eq("event_date", event_date) \
        .execute()
    
    existing_records = response.data
    conflicts = []
    
    for record in existing_records:
        existing_volunteers = parse_names(record.get("volunteers", ""))
        for person in new_volunteers:
            if person in existing_volunteers:
                conflicts.append(f"{person} ({c.LABEL_ALREADY_SCHEDULED}: {record.get('group_name')})")
                
    return conflicts

def check_room_conflicts(event_date: str, time_slot: str, room_name: str) -> bool:
    """Check if a room is already booked for the specified date and time slot."""
    response = supabase.table("room_bookings") \
        .select("id") \
        .eq("event_date", event_date) \
        .eq("time_slot", time_slot) \
        .eq("room_name", room_name) \
        .execute()
    
    return len(response.data) > 0

# ------------------------------------------------------------------------------
# 3. UI Components & Layout
# ------------------------------------------------------------------------------
st.title(f"⛪ {c.TITLE_APP}")
st.markdown(f"*{c.SUBTITLE_APP}*")

tabs = st.tabs([c.TAB_GRACE, c.TAB_SCHEDULE, c.TAB_ROOM, c.TAB_DATA_VIEW])

# ------------------------------------------------------------------------------
# TAB 1: Grace & Reflection Diary
# ------------------------------------------------------------------------------
with tabs[0]:
    st.subheader(c.HEADER_GRACE_FORM)
    
    with st.form("grace_form", clear_on_submit=True):
        record_date = st.date_input(c.LABEL_DATE, value=datetime.date.today())
        author = st.text_input(c.LABEL_AUTHOR)
        
        selected_category = st.selectbox(c.LABEL_CATEGORY, c.GRACE_CATEGORIES)
        custom_category = ""
        if selected_category == c.OPTION_OTHER:
            custom_category = st.text_input(c.LABEL_CUSTOM_CATEGORY, key="grace_custom_cat")
            
        content = st.text_area(c.LABEL_GRACE_CONTENT, height=150)
        prayer_request = st.text_area(c.LABEL_PRAYER_REQUEST, height=100)
        
        submit_grace = st.form_submit_button(c.BTN_SUBMIT)
        
        if submit_grace:
            final_category = custom_category.strip() if selected_category == c.OPTION_OTHER else selected_category
            if not author or not content or (selected_category == c.OPTION_OTHER and not final_category):
                st.error(c.ERR_REQUIRED_FIELDS)
            else:
                payload = {
                    "record_date": str(record_date),
                    "author": author,
                    "category": final_category,
                    "content": content,
                    "prayer_request": prayer_request
                }
                supabase.table("grace_diaries").insert(payload).execute()
                st.success(c.MSG_SAVE_SUCCESS)

# ------------------------------------------------------------------------------
# TAB 2: Future Ministry Scheduling
# ------------------------------------------------------------------------------
with tabs[1]:
    st.subheader(c.HEADER_SCHEDULE_FORM)
    
    # Selection controls OUTSIDE form to trigger dynamic text input correctly
    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input(c.LABEL_EVENT_DATE, value=datetime.date.today(), key="sched_date")
    with col2:
        selected_group = st.selectbox(c.LABEL_GROUP, c.GROUP_OPTIONS, key="sched_group_select")
        
    custom_group = ""
    if selected_group == c.OPTION_OTHER:
        custom_group = st.text_input(c.LABEL_CUSTOM_GROUP, key="sched_custom_group")
        
    final_group_name = custom_group.strip() if selected_group == c.OPTION_OTHER else selected_group

    with st.form("schedule_form"):
        volunteers_input = st.text_input(c.LABEL_VOLUNTEERS, help=c.HELP_VOLUNTEERS)
        notes = st.text_input(c.LABEL_NOTES)
        force_save = st.checkbox(c.LABEL_FORCE_SAVE)
        
        submit_schedule = st.form_submit_button(c.BTN_SUBMIT)
        
        if submit_schedule:
            volunteers_list = parse_names(volunteers_input)
            if not final_group_name or not volunteers_list:
                st.error(c.ERR_REQUIRED_FIELDS)
            else:
                conflicts = check_schedule_conflicts(str(event_date), final_group_name, volunteers_list)
                
                if conflicts and not force_save:
                    st.error(f"{c.ERR_SCHEDULE_CONFLICT}: {', '.join(conflicts)}")
                    st.warning(c.WARN_FORCE_SAVE_HINT)
                else:
                    payload = {
                        "event_date": str(event_date),
                        "group_name": final_group_name,
                        "volunteers": ", ".join(volunteers_list),
                        "notes": notes
                    }
                    supabase.table("schedules").insert(payload).execute()
                    st.success(c.MSG_SAVE_SUCCESS)

# ------------------------------------------------------------------------------
# TAB 3: Room / Venue Booking
# ------------------------------------------------------------------------------
with tabs[2]:
    st.subheader(c.HEADER_ROOM_FORM)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        booking_date = st.date_input(c.LABEL_EVENT_DATE, value=datetime.date.today(), key="room_date")
        time_slot = st.selectbox(c.LABEL_TIME_SLOT, c.TIME_SLOTS)
    with col_r2:
        selected_room = st.selectbox(c.LABEL_ROOM, c.ROOM_OPTIONS, key="room_select")
        custom_room = ""
        if selected_room == c.OPTION_OTHER:
            custom_room = st.text_input(c.LABEL_CUSTOM_ROOM, key="room_custom_input")

    final_room_name = custom_room.strip() if selected_room == c.OPTION_OTHER else selected_room

    with st.form("room_booking_form"):
        applicant = st.text_input(c.LABEL_APPLICANT)
        purpose = st.text_input(c.LABEL_PURPOSE)
        force_save_room = st.checkbox(c.LABEL_FORCE_SAVE, key="force_room")
        
        submit_room = st.form_submit_button(c.BTN_SUBMIT)
        
        if submit_room:
            if not final_room_name or not applicant:
                st.error(c.ERR_REQUIRED_FIELDS)
            else:
                is_conflicted = check_room_conflicts(str(booking_date), time_slot, final_room_name)
                
                if is_conflicted and not force_save_room:
                    st.error(c.ERR_ROOM_CONFLICT)
                    st.warning(c.WARN_FORCE_SAVE_HINT)
                else:
                    payload = {
                        "event_date": str(booking_date),
                        "time_slot": time_slot,
                        "room_name": final_room_name,
                        "applicant": applicant,
                        "purpose": purpose
                    }
                    supabase.table("room_bookings").insert(payload).execute()
                    st.success(c.MSG_SAVE_SUCCESS)

# ------------------------------------------------------------------------------
# TAB 4: Data Search & Overview
# ------------------------------------------------------------------------------
with tabs[3]:
    st.subheader(c.HEADER_DATA_VIEW)
    
    dataset_type = st.radio(c.LABEL_SELECT_DATASET, [c.DATASET_GRACE, c.DATASET_SCHEDULE, c.DATASET_ROOM], horizontal=True)
    search_keyword = st.text_input(c.LABEL_SEARCH_KEYWORD)
    
    table_map = {
        c.DATASET_GRACE: "grace_diaries",
        c.DATASET_SCHEDULE: "schedules",
        c.DATASET_ROOM: "room_bookings"
    }
    
    target_table = table_map[dataset_type]
    data_response = supabase.table(target_table).select("*").order("created_at", desc=True).execute()
    
    if data_response.data:
        df = pd.DataFrame(data_response.data)
        
        # Keyword filtering across all text columns
        if search_keyword:
            mask = df.astype(str).apply(lambda row: row.str.contains(search_keyword, case=False).any(), axis=1)
            df = df[mask]
            
        # Rename columns using constants mapping for presentation
        df_display = df.rename(columns=c.COLUMN_MAPPINGS.get(target_table, {}))
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info(c.MSG_NO_DATA)
