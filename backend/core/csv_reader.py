import os
import csv
from datetime import datetime, date, timedelta
from typing import List, Dict

METRICS_CSV = "resources/csv/metrics.csv"
EMPLOYEES_CSV = "resources/csv/employees.csv"

# Чтение CSV файла и преобразование в список словарей
def read_csv(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Чтение производственных показателей
def read_metrics():
    return read_csv(METRICS_CSV)

# Чтение списка сотрудников
def read_employees():
    return read_csv(EMPLOYEES_CSV)

# Поиск сотрудников с ДР в ближайшие N дней
def get_upcoming_birthdays(employees: List[Dict], days_ahead: int = 3) -> List[Dict]:
    today = date.today()
    result = []
    
    for emp in employees:
        if not emp.get('is_active', True):
            continue
        try:
            birth = datetime.strptime(emp['birth_date'], '%Y-%m-%d').date()
            # ДР в этом году
            this_year_birth = birth.replace(year=today.year)
            # Если уже прошёл — берём следующий год
            if this_year_birth < today:
                this_year_birth = birth.replace(year=today.year + 1)
            
            days_until = (this_year_birth - today).days
            
            if 0 <= days_until <= days_ahead:
                emp_copy = emp.copy()
                emp_copy['days_until'] = days_until
                emp_copy['birth_date_this_year'] = this_year_birth
                emp_copy['age'] = this_year_birth.year - birth.year
                result.append(emp_copy)
        except:
            continue
    
    result.sort(key=lambda x: x['days_until'])
    return result

# Поиск сотрудников у которых ДР сегодня
def get_todays_birthdays(employees: List[Dict]) -> List[Dict]:
    today = date.today()
    result = []
    for emp in employees:
        try:
            birth = datetime.strptime(emp['birth_date'], '%Y-%m-%d').date()
            if birth.month == today.month and birth.day == today.day:
                emp['age'] = today.year - birth.year
                result.append(emp)
        except:
            continue
    return result