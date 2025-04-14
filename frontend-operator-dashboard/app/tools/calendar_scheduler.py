"""
Calendar Scheduler Tool for the Personal AI Agent System.

This module provides functionality to manage calendar events, appointments,
and scheduling tasks.
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("calendar_scheduler")

def run(
    action: str = "list",
    calendar_id: str = "primary",
    event_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    recurrence: Optional[str] = None,
    date_range: Optional[str] = None,
    limit: int = 10,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["calendar", "schedule"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Manage calendar events and scheduling.
    
    Args:
        action: Action to perform (list, create, update, delete, find_free_time)
        calendar_id: Calendar identifier
        event_id: Event identifier (for update/delete actions)
        title: Event title (for create/update actions)
        description: Event description (for create/update actions)
        location: Event location (for create/update actions)
        start_time: Event start time in ISO format (for create/update actions)
        end_time: Event end time in ISO format (for create/update actions)
        attendees: List of attendee email addresses (for create/update actions)
        recurrence: Recurrence rule (for create/update actions)
        date_range: Date range for listing events (today, tomorrow, this_week, next_week, custom)
        limit: Maximum number of events to return (for list action)
        store_memory: Whether to store the calendar data in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing calendar operation results
    """
    logger.info(f"Performing calendar {action} operation")
    
    try:
        # Validate inputs
        if action not in ["list", "create", "update", "delete", "find_free_time"]:
            raise ValueError(f"Invalid action: {action}. Supported actions: list, create, update, delete, find_free_time")
            
        if action in ["update", "delete"] and not event_id:
            raise ValueError(f"Event ID is required for {action} action")
            
        if action == "create":
            if not title:
                raise ValueError("Event title is required for create action")
            if not start_time:
                raise ValueError("Event start time is required for create action")
            if not end_time:
                raise ValueError("Event end time is required for create action")
        
        if action == "update":
            if not any([title, description, location, start_time, end_time, attendees, recurrence]):
                raise ValueError("At least one field to update is required for update action")
        
        if date_range and date_range not in ["today", "tomorrow", "this_week", "next_week", "custom"]:
            raise ValueError(f"Invalid date range: {date_range}. Supported ranges: today, tomorrow, this_week, next_week, custom")
        
        # In a real implementation, this would use calendar APIs
        # For now, we'll simulate the calendar operations
        
        # Simulate calendar operation
        if action == "list":
            result = _simulate_list_events(calendar_id, date_range, limit)
        elif action == "create":
            result = _simulate_create_event(calendar_id, title, description, location, start_time, end_time, attendees, recurrence)
        elif action == "update":
            result = _simulate_update_event(calendar_id, event_id, title, description, location, start_time, end_time, attendees, recurrence)
        elif action == "delete":
            result = _simulate_delete_event(calendar_id, event_id)
        else:  # find_free_time
            result = _simulate_find_free_time(calendar_id, start_time, end_time)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the calendar operation for memory storage
                if action == "list":
                    summary = f"Listed {len(result['events'])} calendar events"
                    if date_range:
                        summary += f" for {date_range}"
                elif action == "create":
                    summary = f"Created calendar event: {title}"
                elif action == "update":
                    summary = f"Updated calendar event: {event_id}"
                elif action == "delete":
                    summary = f"Deleted calendar event: {event_id}"
                else:  # find_free_time
                    summary = f"Found {len(result['free_slots'])} free time slots"
                
                memory_entry = {
                    "type": "calendar_operation",
                    "action": action,
                    "summary": summary,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add specific details based on action
                if action == "list" and result["events"]:
                    memory_entry["upcoming_events"] = [
                        {
                            "title": event["title"],
                            "start_time": event["start_time"],
                            "end_time": event["end_time"]
                        }
                        for event in result["events"][:3]
                    ]
                elif action == "create" or action == "update":
                    memory_entry["event"] = {
                        "id": result["event"]["id"],
                        "title": result["event"]["title"],
                        "start_time": result["event"]["start_time"],
                        "end_time": result["event"]["end_time"]
                    }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["calendar_" + action]
                )
                
                logger.info(f"Stored calendar operation in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store calendar operation in memory: {str(e)}")
        
        return {
            "success": True,
            "action": action,
            "calendar_id": calendar_id,
            "data": result
        }
    except Exception as e:
        error_msg = f"Error performing calendar operation: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "action": action,
            "calendar_id": calendar_id
        }

def _simulate_list_events(calendar_id: str, date_range: Optional[str], limit: int) -> Dict[str, Any]:
    """
    Simulate listing calendar events.
    
    Args:
        calendar_id: Calendar identifier
        date_range: Date range filter
        limit: Maximum number of events to return
        
    Returns:
        Dictionary with simulated calendar events
    """
    # Generate a deterministic but seemingly random seed
    seed = int(time.time() / 86400)  # Change seed daily
    random.seed(seed)
    
    # Determine date range
    now = datetime.now()
    
    if date_range == "today":
        start_date = datetime(now.year, now.month, now.day)
        end_date = start_date + timedelta(days=1)
    elif date_range == "tomorrow":
        start_date = datetime(now.year, now.month, now.day) + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
    elif date_range == "this_week":
        # Start from today, end at the end of the week (Sunday)
        start_date = datetime(now.year, now.month, now.day)
        days_until_sunday = 6 - now.weekday()  # 6 is Sunday
        end_date = start_date + timedelta(days=days_until_sunday)
    elif date_range == "next_week":
        # Start from next Monday, end at the end of next week (Sunday)
        days_until_monday = 7 - now.weekday()  # 0 is Monday
        start_date = datetime(now.year, now.month, now.day) + timedelta(days=days_until_monday)
        end_date = start_date + timedelta(days=7)
    else:  # custom or None
        # Default to next 7 days
        start_date = datetime(now.year, now.month, now.day)
        end_date = start_date + timedelta(days=7)
    
    # Generate events within the date range
    events = _generate_calendar_events(calendar_id, start_date, end_date)
    
    # Limit the number of events
    events = events[:limit]
    
    return {
        "events": events,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_count": len(events)
    }

def _simulate_create_event(
    calendar_id: str,
    title: str,
    description: Optional[str],
    location: Optional[str],
    start_time: str,
    end_time: str,
    attendees: Optional[List[str]],
    recurrence: Optional[str]
) -> Dict[str, Any]:
    """
    Simulate creating a calendar event.
    
    Args:
        calendar_id: Calendar identifier
        title: Event title
        description: Event description
        location: Event location
        start_time: Event start time
        end_time: Event end time
        attendees: List of attendee email addresses
        recurrence: Recurrence rule
        
    Returns:
        Dictionary with simulated created event
    """
    # Generate a unique event ID
    event_id = f"event_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Create event
    event = {
        "id": event_id,
        "calendar_id": calendar_id,
        "title": title,
        "description": description if description else "",
        "location": location if location else "",
        "start_time": start_time,
        "end_time": end_time,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    # Add attendees if provided
    if attendees:
        event["attendees"] = [{"email": email, "response_status": "needsAction"} for email in attendees]
    
    # Add recurrence if provided
    if recurrence:
        event["recurrence"] = recurrence
    
    return {
        "event": event,
        "created": True
    }

def _simulate_update_event(
    calendar_id: str,
    event_id: str,
    title: Optional[str],
    description: Optional[str],
    location: Optional[str],
    start_time: Optional[str],
    end_time: Optional[str],
    attendees: Optional[List[str]],
    recurrence: Optional[str]
) -> Dict[str, Any]:
    """
    Simulate updating a calendar event.
    
    Args:
        calendar_id: Calendar identifier
        event_id: Event identifier
        title: Event title
        description: Event description
        location: Event location
        start_time: Event start time
        end_time: Event end time
        attendees: List of attendee email addresses
        recurrence: Recurrence rule
        
    Returns:
        Dictionary with simulated updated event
    """
    # In a real implementation, this would retrieve the existing event
    # For simulation, we'll create a mock existing event
    existing_event = {
        "id": event_id,
        "calendar_id": calendar_id,
        "title": "Original Event Title",
        "description": "Original event description",
        "location": "Original Location",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "status": "confirmed"
    }
    
    # Update fields if provided
    updated_event = existing_event.copy()
    
    if title:
        updated_event["title"] = title
    
    if description:
        updated_event["description"] = description
    
    if location:
        updated_event["location"] = location
    
    if start_time:
        updated_event["start_time"] = start_time
    
    if end_time:
        updated_event["end_time"] = end_time
    
    if attendees:
        updated_event["attendees"] = [{"email": email, "response_status": "needsAction"} for email in attendees]
    
    if recurrence:
        updated_event["recurrence"] = recurrence
    
    # Update the updated_at timestamp
    updated_event["updated_at"] = datetime.now().isoformat()
    
    return {
        "event": updated_event,
        "updated": True
    }

def _simulate_delete_event(calendar_id: str, event_id: str) -> Dict[str, Any]:
    """
    Simulate deleting a calendar event.
    
    Args:
        calendar_id: Calendar identifier
        event_id: Event identifier
        
    Returns:
        Dictionary with deletion result
    """
    # In a real implementation, this would delete the event
    # For simulation, we'll just return success
    
    return {
        "event_id": event_id,
        "deleted": True
    }

def _simulate_find_free_time(
    calendar_id: str,
    start_time: Optional[str],
    end_time: Optional[str]
) -> Dict[str, Any]:
    """
    Simulate finding free time slots in a calendar.
    
    Args:
        calendar_id: Calendar identifier
        start_time: Start of time range to search
        end_time: End of time range to search
        
    Returns:
        Dictionary with simulated free time slots
    """
    # Determine time range
    now = datetime.now()
    
    if start_time:
        range_start = datetime.fromisoformat(start_time)
    else:
        range_start = datetime(now.year, now.month, now.day, 9, 0)  # Default to 9 AM today
    
    if end_time:
        range_end = datetime.fromisoformat(end_time)
    else:
        range_end = datetime(now.year, now.month, now.day, 17, 0)  # Default to 5 PM today
        if range_end < range_start:
            range_end = range_start + timedelta(hours=8)  # Ensure at least 8 hours range
    
    # Generate busy slots (simulated calendar events)
    busy_slots = []
    
    # Generate a deterministic but seemingly random seed
    seed = int(time.time() / 86400) + hash(calendar_id)  # Change seed daily
    random.seed(seed)
    
    # Generate 3-7 busy slots
    num_busy_slots = random.randint(3, 7)
    
    for _ in range(num_busy_slots):
        # Generate a random start time within the range
        slot_duration = timedelta(minutes=random.choice([30, 60, 90, 120]))
        max_start = range_end - slot_duration
        
        if max_start <= range_start:
            continue  # Skip if the range is too small
        
        # Generate random start time
        random_minutes = random.randint(0, int((max_start - range_start).total_seconds() / 60))
        slot_start = range_start + timedelta(minutes=random_minutes)
        
        # Round to nearest 30 minutes
        minutes = slot_start.minute
        if minutes < 15:
            slot_start = slot_start.replace(minute=0)
        elif minutes < 45:
            slot_start = slot_start.replace(minute=30)
        else:
            slot_start = slot_start.replace(minute=0, hour=slot_start.hour + 1)
        
        slot_end = slot_start + slot_duration
        
        busy_slots.append({
            "start": slot_start.isoformat(),
            "end": slot_end.isoformat()
        })
    
    # Sort busy slots by start time
    busy_slots.sort(key=lambda x: x["start"])
    
    # Find free slots between busy slots
    free_slots = []
    
    # Add free slot from range_start to first busy slot
    if busy_slots and range_start < datetime.fromisoformat(busy_slots[0]["start"]):
        free_slots.append({
            "start": range_start.isoformat(),
            "end": busy_slots[0]["start"],
            "duration_minutes": int((datetime.fromisoformat(busy_slots[0]["start"]) - range_start).total_seconds() / 60)
        })
    
    # Add free slots between busy slots
    for i in range(len(busy_slots) - 1):
        slot_end = datetime.fromisoformat(busy_slots[i]["end"])
        next_slot_start = datetime.fromisoformat(busy_slots[i + 1]["start"])
        
        if slot_end < next_slot_start:
            free_slots.append({
                "start": busy_slots[i]["end"],
                "end": busy_slots[i + 1]["start"],
                "duration_minutes": int((next_slot_start - slot_end).total_seconds() / 60)
            })
    
    # Add free slot from last busy slot to range_end
    if busy_slots and datetime.fromisoformat(busy_slots[-1]["end"]) < range_end:
        free_slots.append({
            "start": busy_slots[-1]["end"],
            "end": range_end.isoformat(),
            "duration_minutes": int((range_end - datetime.fromisoformat(busy_slots[-1]["end"])).total_seconds() / 60)
        })
    
    # If no busy slots, the entire range is free
    if not busy_slots:
        free_slots.append({
            "start": range_start.isoformat(),
            "end": range_end.isoformat(),
            "duration_minutes": int((range_end - range_start).total_seconds() / 60)
        })
    
    return {
        "time_range": {
            "start": range_start.isoformat(),
            "end": range_end.isoformat()
        },
        "busy_slots": busy_slots,
        "free_slots": free_slots
    }

def _generate_calendar_events(calendar_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Generate simulated calendar events within a date range.
    
    Args:
        calendar_id: Calendar identifier
        start_date: Start date
        end_date: End date
        
    Returns:
        List of simulated calendar events
    """
    # Generate a deterministic but seemingly random seed
    seed = int(time.time() / 86400) + hash(calendar_id)  # Change seed daily
    random.seed(seed)
    
    # Define event templates
    event_templates = [
        {"title": "Team Meeting", "duration": 60, "location": "Conference Room A", "attendees": ["team@example.com"]},
        {"title": "Project Review", "duration": 90, "location": "Conference Room B", "attendees": ["manager@example.com", "team@example.com"]},
        {"title": "Client Call", "duration": 30, "location": "Phone", "attendees": ["client@example.com"]},
        {"title": "Lunch Break", "duration": 60, "location": "", "attendees": []},
        {"title": "Product Demo", "duration": 45, "location": "Demo Room", "attendees": ["client@example.com", "sales@example.com"]},
        {"title": "1:1 Meeting", "duration": 30, "location": "Office", "attendees": ["manager@example.com"]},
        {"title": "Training Session", "duration": 120, "location": "Training Room", "attendees": ["team@example.com"]},
        {"title": "Planning Session", "duration": 60, "location": "Conference Room C", "attendees": ["team@example.com"]},
        {"title": "Interview", "duration": 45, "location": "HR Office", "attendees": ["hr@example.com", "hiring_manager@example.com"]},
        {"title": "Code Review", "duration": 60, "location": "Dev Room", "attendees": ["dev_team@example.com"]}
    ]
    
    # Generate events
    events = []
    
    # Number of days in the range
    days_in_range = (end_date - start_date).days
    
    # Generate events for each day
    for day in range(days_in_range):
        current_date = start_date + timedelta(days=day)
        
        # Skip weekends
        if current_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            continue
        
        # Generate 3-6 events per day
        num_events = random.randint(3, 6)
        
        # Track used time slots to avoid overlaps
        used_slots = []
        
        for _ in range(num_events):
            # Select a random event template
            template = random.choice(event_templates)
            
            # Generate a random start time between 9 AM and 5 PM
            max_start_hour = 17 - template["duration"] // 60  # Ensure event ends by 5 PM
            
            if max_start_hour <= 9:
                max_start_hour = 16  # Fallback if duration is too long
            
            start_hour = random.randint(9, max_start_hour)
            start_minute = random.choice([0, 30])  # Start at either XX:00 or XX:30
            
            event_start = current_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            event_end = event_start + timedelta(minutes=template["duration"])
            
            # Check for overlaps
            overlap = False
            for used_start, used_end in used_slots:
                if (event_start <= used_end and event_end >= used_start):
                    overlap = True
                    break
            
            if overlap:
                continue  # Skip this event if it overlaps
            
            # Add to used slots
            used_slots.append((event_start, event_end))
            
            # Generate a unique event ID
            event_id = f"event_{calendar_id}_{current_date.strftime('%Y%m%d')}_{start_hour}{start_minute}_{random.randint(1000, 9999)}"
            
            # Create event
            event = {
                "id": event_id,
                "calendar_id": calendar_id,
                "title": template["title"],
                "description": f"This is a simulated {template['title'].lower()} event.",
                "location": template["location"],
                "start_time": event_start.isoformat(),
                "end_time": event_end.isoformat(),
                "created_at": (current_date - timedelta(days=random.randint(1, 30))).isoformat(),
                "updated_at": (current_date - timedelta(days=random.randint(0, 7))).isoformat(),
                "status": "confirmed"
            }
            
            # Add attendees if any
            if template["attendees"]:
                event["attendees"] = [{"email": email, "response_status": random.choice(["accepted", "tentative", "needsAction"])} for email in template["attendees"]]
            
            events.append(event)
    
    # Sort events by start time
    events.sort(key=lambda x: x["start_time"])
    
    return events
