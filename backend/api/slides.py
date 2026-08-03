from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from backend import crud, schemas, models
from backend.database import get_db
from backend.auth import get_current_user
from backend.websocket_manager import notify_clients
import os
import shutil
from datetime import datetime

router = APIRouter()

# Создание слайда
@router.post("/slides", response_model=schemas.SlideOut)
def create_slide(
    slide: schemas.SlideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    db_slide = crud.create_slide(db, slide)
    # Оповещение экранов через WebSocket
    background_tasks.add_task(notify_clients, {"type": "slide_created", "id": db_slide.id})
    return db_slide

# Получение всех слайдов
@router.get("/slides", response_model=List[schemas.SlideOut])
def get_all_slides(db: Session = Depends(get_db)):
    return crud.get_all_slides(db)

# Получение слайда по ID
@router.get("/slides/{slide_id}", response_model=schemas.SlideOut)
def get_slide(slide_id: int, db: Session = Depends(get_db)):
    db_slide = crud.get_slide(db, slide_id)
    if not db_slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    return db_slide

# Обновление слайда
@router.put("/slides/{slide_id}", response_model=schemas.SlideOut)
def update_slide(
    slide_id: int,
    slide: schemas.SlideUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    db_slide = crud.update_slide(db, slide_id, slide)
    if not db_slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    background_tasks.add_task(notify_clients, {"type": "slide_updated", "id": db_slide.id})
    return db_slide

# Удаление слайда
@router.delete("/slides/{slide_id}")
def delete_slide(
    slide_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not crud.delete_slide(db, slide_id):
        raise HTTPException(status_code=404, detail="Slide not found")
    background_tasks.add_task(notify_clients, {"type": "slide_deleted", "id": slide_id})
    return {"ok": True}

# Загрузка изображения на сервер
@router.post("/slides/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    # Проверка типа файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Можно загружать только изображения (JPEG, PNG, GIF и т.д.)"
        )

    # Создание папки для загрузок
    upload_dir = "resources/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Генерация уникального имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    filename = f"{timestamp}_{safe_filename}"
    filepath = os.path.join(upload_dir, filename)

    # Сохранение файла
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сохранения файла: {str(e)}"
        )

    # Возврат URL для доступа к картинке
    image_url = f"/resources/uploads/{filename}"
    return {"image_url": image_url}

# Создание сводки производственных показателей из CSV
@router.post("/slides/create-metric-slide")
def create_metric_slide(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    from backend.core.csv_reader import read_metrics

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    title = data.get('title', '📊 Производственные показатели')
    styles = data.get('styles', {})

    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Укажите даты начала и окончания")

    metrics = read_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Файл metrics.csv не найден или пуст")

    # Формирование HTML-таблицы показателей
    rows = []
    for m in metrics:
        name = m.get('name', '—')
        value = m.get('value', '0')
        trend = m.get('trend', 'stable')
        unit = m.get('unit', '')

        trend_icon = '▲' if trend == 'up' else '▼' if trend == 'down' else '●'
        trend_color = '#00ff88' if trend == 'up' else '#ff4444' if trend == 'down' else '#ffd700'

        rows.append(f"""
            <tr>
                <td style="text-align:left; padding:10px 14px; font-size:1.1em;">{name}</td>
                <td style="text-align:right; padding:10px 14px; font-size:1.3em; font-weight:bold;">{value} {unit}</td>
                <td style="text-align:center; padding:10px 14px; font-size:1.2em; color:{trend_color};">{trend_icon}</td>
            </tr>
        """)

    table_html = f"""
    <div style="width:100%; max-width:900px; margin:0 auto; padding:20px;">
        <h2 style="text-align:center; font-size:2.2em; margin-bottom:20px;">{title}</h2>
        <table style="width:100%; border-collapse:collapse; background:rgba(255,255,255,0.05); border-radius:16px; overflow:hidden;">
            <thead>
                <tr style="background:rgba(255,255,255,0.1);">
                    <th style="text-align:left; padding:12px 16px; font-size:1em;">Показатель</th>
                    <th style="text-align:right; padding:12px 16px; font-size:1em;">Значение</th>
                    <th style="text-align:center; padding:12px 16px; font-size:1em;">Тренд</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <p style="text-align:center; font-size:0.8em; color:#6a7a9a; margin-top:16px;">
            Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        </p>
    </div>
    """

    # Поиск существующей сводки
    existing = db.query(models.Slide).filter(
        models.Slide.type == 'metric',
        models.Slide.title == title
    ).first()

    if existing:
        # Обновление существующей сводки
        existing.content = table_html
        existing.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        existing.end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        existing.styles = styles
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        background_tasks.add_task(notify_clients, {"type": "slide_updated", "id": existing.id})
        return {"message": f"Слайд-сводка '{title}' обновлена", "slide_id": existing.id}
    else:
        # Создание новой сводки
        new_slide = models.Slide(
            type='metric',
            title=title,
            content=table_html,
            extra_data={'is_metric_summary': True},
            start_date=datetime.fromisoformat(start_date.replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(end_date.replace('Z', '+00:00')),
            priority=1,
            is_auto_generated=False,
            styles=styles
        )
        db.add(new_slide)
        db.commit()
        db.refresh(new_slide)
        background_tasks.add_task(notify_clients, {"type": "slide_created", "id": new_slide.id})
        return {"message": f"Слайд '{title}' создан", "slide_id": new_slide.id}

# Создание поздравления вручную (из панели уведомлений)
@router.post("/slides/create-greeting")
def create_greeting_slide(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    name = data.get('name')
    title = data.get('title', f'С Днём рождения, {name}!')
    content = data.get('content', 'Поздравляем! Желаем счастья, здоровья, успехов!')

    if not name:
        raise HTTPException(status_code=400, detail="Укажите имя сотрудника")

    extra_data = {
        'name': name,
        'is_manual': True
    }

    new_slide = models.Slide(
        type='greeting',
        title=title,
        content=content,
        extra_data=extra_data,
        start_date=datetime.now(),
        end_date=datetime.now().replace(hour=23, minute=59, second=59),
        priority=1,
        is_auto_generated=False
    )
    db.add(new_slide)
    db.commit()
    db.refresh(new_slide)

    background_tasks.add_task(notify_clients, {"type": "slide_created", "id": new_slide.id})
    return {"message": f"Поздравление для {name} создано", "slide_id": new_slide.id}