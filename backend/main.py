from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import slides, active_slides, screens, auth_router, employees
from backend.websocket_manager import router as websocket_router
from backend.database import engine, Base

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Signage API",
    description="System for managing digital signage displays",
    version="2.0.0"
)

# CORS для доступа с любых устройств
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация роутеров
app.include_router(active_slides.router, prefix="/api", tags=["slides"])
app.include_router(slides.router, prefix="/api", tags=["slides"])
app.include_router(screens.router, prefix="/api", tags=["screens"])
app.include_router(auth_router.router, prefix="/api", tags=["auth"])
app.include_router(employees.router, prefix="/api", tags=["employees"])
app.include_router(websocket_router, prefix="", tags=["websocket"])

# Раздача статики (картинки, загрузки)
app.mount("/resources", StaticFiles(directory="resources"), name="resources")

# Генерация уникального кода для экрана
@app.get("/api/generate-code")
def generate_code():
    from backend.database import SessionLocal
    from backend.models import Screen
    import random
    
    db = SessionLocal()
    try:
        existing_codes = [s[0] for s in db.query(Screen.code).all()]
        for _ in range(100):
            code = f"{random.randint(0, 999):03d}"
            if code not in existing_codes:
                return {"code": code}
        raise HTTPException(status_code=500, detail="No free codes available")
    finally:
        db.close()

# Отдача HTML-страниц
@app.get("/main.html")
async def get_main():
    return FileResponse("frontend/main.html")

@app.get("/admin.html")
async def get_admin():
    return FileResponse("frontend/admin.html")

@app.get("/index.html")
async def get_index():
    return FileResponse("frontend/index.html")

# Корневой путь
@app.get("/")
def root():
    return {
        "message": "Digital Signage API v2.0",
        "docs": "/docs",
        "admin": "/admin.html",
        "display": "/index.html",
        "login": "/main.html"
    }

@app.on_event("startup")
async def startup_event():
    print("API started")