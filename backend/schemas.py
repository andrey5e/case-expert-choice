from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str

# Схема для вывода пользователя
class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

# Базовая схема слайда (общие поля)
class SlideBase(BaseModel):
    type: str
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    start_date: datetime
    end_date: datetime
    priority: int = 0
    is_auto_generated: bool = False
    styles: Optional[Dict[str, Any]] = None

# Схема для создания слайда
class SlideCreate(SlideBase):
    pass

# Схема для обновления слайда
class SlideUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    styles: Optional[Dict[str, Any]] = None

# Схема для вывода слайда
class SlideOut(SlideBase):
    id: int
    views: int
    is_active: bool
    is_auto_generated: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# Схема для создания экрана
class ScreenCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, pattern=r"^[0-9]{3}$")
    name: Optional[str] = None
    location: Optional[str] = None

# Схема для обновления экрана
class ScreenUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_connected: Optional[bool] = None

# Схема для вывода экрана
class ScreenOut(BaseModel):
    id: int
    code: str
    name: Optional[str]
    location: Optional[str]
    is_connected: bool
    is_online: bool
    last_active: Optional[datetime]
    created_at: datetime
    class Config:
        from_attributes = True

# Схема для активации экрана по коду
class ScreenActivate(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, pattern=r"^[0-9]{3}$")

# Схема для вывода сотрудника
class EmployeeOut(BaseModel):
    id: int
    name: str
    birth_date: datetime
    department: Optional[str]
    photo_url: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Схема для вывода метрики
class MetricOut(BaseModel):
    id: int
    name: str
    value: float
    trend: str
    updated_at: datetime
    class Config:
        from_attributes = True