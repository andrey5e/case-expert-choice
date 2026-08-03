from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import models
from backend.database import get_db
from backend.auth import get_current_user
from backend.core.csv_reader import read_employees, get_todays_birthdays, get_upcoming_birthdays

router = APIRouter()

# Получение всех сотрудников из CSV
@router.get("/employees")
def get_all_employees(current_user: models.User = Depends(get_current_user)):
    employees = read_employees()
    for emp in employees:
        if 'birth_date' in emp and hasattr(emp['birth_date'], 'isoformat'):
            emp['birth_date'] = emp['birth_date'].isoformat()
    return employees

# Сотрудники у которых ДР сегодня
@router.get("/employees/birthdays/today")
def get_todays_birthdays_endpoint():
    employees = read_employees()
    birthdays = get_todays_birthdays(employees)
    for b in birthdays:
        if 'birth_date' in b and hasattr(b['birth_date'], 'isoformat'):
            b['birth_date'] = b['birth_date'].isoformat()
    return birthdays

# Сотрудники у которых ДР через 0-3 дня
@router.get("/employees/birthdays/upcoming")
def get_upcoming_birthdays_endpoint():
    employees = read_employees()
    birthdays = get_upcoming_birthdays(employees, days_ahead=3)
    for b in birthdays:
        if 'birth_date' in b and hasattr(b['birth_date'], 'isoformat'):
            b['birth_date'] = b['birth_date'].isoformat()
        if 'birth_date_this_year' in b and hasattr(b['birth_date_this_year'], 'isoformat'):
            b['birth_date_this_year'] = b['birth_date_this_year'].isoformat()
    return birthdays