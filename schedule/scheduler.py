import os
import json
import time
import datetime
import threading
import winsound

schedules_lock = threading.Lock()
DB_PATH = os.path.join(os.path.dirname(__file__), 'schedules.json')

def load_schedules():
    with schedules_lock:
        if not os.path.exists(DB_PATH):
            return []
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            return []

def save_schedules(schedules):
    with schedules_lock:
        try:
            with open(DB_PATH, 'w') as f:
                json.dump(schedules, f, indent=2)
            return True
        except Exception:
            return False

def add_schedule(task_type, trigger_val, command, message=None, interval_mins=None):
    schedules = load_schedules()
    # Generate new ID
    new_id = 1
    if schedules:
        new_id = max(t.get('id', 0) for t in schedules) + 1
        
    task = {
        "id": new_id,
        "type": task_type,
        "command": command,
        "message": message,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if task_type == "one-shot":
        # trigger_val is either absolute datetime string or timestamp
        task["trigger_time"] = trigger_val
    elif task_type == "alarm":
        # trigger_val is HH:MM
        task["alarm_time"] = trigger_val
        task["last_fired_date"] = ""
    elif task_type == "recurring":
        task["interval_mins"] = interval_mins
        task["last_run"] = time.time()
        
    schedules.append(task)
    save_schedules(schedules)
    return task

def cancel_schedule(task_id):
    schedules = load_schedules()
    initial_len = len(schedules)
    schedules = [t for t in schedules if t.get('id') != task_id]
    if len(schedules) < initial_len:
        save_schedules(schedules)
        return True
    return False

def scheduler_loop(execute_callback):
    """
    Loop running in a daemon thread. Checks tasks every 3 seconds.
    """
    # Delay startup slightly to let main loop initialize
    time.sleep(2)
    
    while True:
        try:
            schedules = load_schedules()
            updated = False
            now = time.time()
            now_dt = datetime.datetime.now()
            today_str = now_dt.strftime("%Y-%m-%d")
            current_hhmm = now_dt.strftime("%H:%M")
            
            due_tasks = []
            
            for task in schedules:
                is_due = False
                
                if task["type"] == "one-shot":
                    t_val = task.get("trigger_time")
                    if isinstance(t_val, (int, float)):
                        if now >= t_val:
                            is_due = True
                    else:
                        try:
                            dt = datetime.datetime.strptime(t_val, "%Y-%m-%d %H:%M:%S")
                            if now_dt >= dt:
                                is_due = True
                        except Exception:
                            # Cleanup malformed time tasks
                            is_due = True
                            
                elif task["type"] == "alarm":
                    # Matches alarm hour/minute and hasn't fired today yet
                    if task.get("alarm_time") == current_hhmm and task.get("last_fired_date") != today_str:
                        is_due = True
                        task["last_fired_date"] = today_str
                        updated = True
                        
                elif task["type"] == "recurring":
                    last_run = task.get("last_run", 0)
                    interval_sec = task.get("interval_mins", 60) * 60
                    if now >= last_run + interval_sec:
                        is_due = True
                        task["last_run"] = now
                        updated = True
                        
                if is_due:
                    due_tasks.append(task)
            
            # Clean up completed one-shot tasks
            if any(t["type"] == "one-shot" for t in due_tasks):
                schedules = [t for t in schedules if t not in due_tasks or t["type"] != "one-shot"]
                updated = True
                
            if updated:
                save_schedules(schedules)
                
            # Execute due tasks
            for task in due_tasks:
                cmd = task.get("command")
                msg = task.get("message")
                
                if cmd == "alarm" and msg:
                    # Trigger alarm chime sound
                    # winsound.MB_ICONASTERISK = 0x00000040
                    winsound.MessageBeep(0x00000040)
                    # Force a print log and speak response
                    # Since we cannot import actions directly (to avoid circular import),
                    # we use the execute_callback or system speaker
                    try:
                        from actions import speak
                        speak(f"Alarm Notice: {msg}")
                    except Exception:
                        pass
                elif cmd:
                    # Run the command through Jarvis CLI processor
                    # Spawns on thread but since parse_and_execute is thread-safe, it's fine
                    execute_callback(cmd)
                    
        except Exception:
            pass
            
        time.sleep(3)
