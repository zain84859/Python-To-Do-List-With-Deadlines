from datetime import datetime
from constants import DIFF_WEIGHT, URGENCY_DUE_TODAY, URGENCY_OVERDUE, URGENCY_DAY_DECAY

def calculate_task_priority(task, date_str):
    
    #Returns a numeric urgency score for a task.
    #Higher = more urgent


    today = datetime.now().date()
    task_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    days_until = (task_date - today).days

    #base urgency by date
    if days_until < 0:
        urgency = URGENCY_OVERDUE
    elif days_until == 0:
        urgency = URGENCY_DUE_TODAY
    else:
        urgency = max(0, URGENCY_DUE_TODAY - days_until * URGENCY_DAY_DECAY)

    # difficulty multiplier
    urgency += DIFF_WEIGHT.get(task["diff"], 1) * 5

    # completed tasks drop to bottom
    if task.get("completed"):
        urgency = 0

    return urgency
