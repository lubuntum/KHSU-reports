import logging
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles

from services.calculate_lessons_hours import calculate_lessons_hours
from services.load_lessons_data import get_teacher_schedule

app = FastAPI() #create fast api
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory = "templates") #import ninja2 templates directory
logger = logging.getLogger(__name__)
@app.get("/")
async def main(request: Request):
    months = [
        {"number": 1, "name": "Январь"},
        {"number": 2, "name": "Февраль"},
        {"number": 3, "name": "Март"},
        {"number": 4, "name": "Апрель"},
        {"number": 5, "name": "Май"},
        {"number": 6, "name": "Июнь"},
        {"number": 7, "name": "Июль"},
        {"number": 8, "name": "Август"},
        {"number": 9, "name": "Сентябрь"},
        {"number": 10, "name": "Октябрь"},
        {"number": 11, "name": "Ноябрь"},
        {"number": 12, "name": "Декабрь"}
    ]
    return templates.TemplateResponse(name="main.html", request=request ,context={
        "title": "Отчеты для преподавателей ХГУ",
        "months": months})
@app.post("/generate-report")
async def generate_report(
        request: Request,
        teacher: str = Form(...),
        month: int = Form(...)):
    try:
        schedule = await get_teacher_schedule(teacher, month)
    except Exception as e:
        logger.error(f"Error fetching schedule for {teacher}, month {month}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке расписания преподавателя"
        )
    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail=f"Расписание учителя {teacher} не найдено за месяц {month}"
        )

    try:
        xlsx_report = calculate_lessons_hours(schedule, teacher, month)
    except Exception as e:
        logger.error(f"Error generating report for {teacher}, month {month}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации отчета"
        )
    if xlsx_report is None:
        raise HTTPException(
            status_code=500,
            detail="Ошибка при генерации отчета."
        )
    encoded_filename = quote(f"{teacher}_{month}_report.xlsx", safe="")
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }
    return StreamingResponse(
        xlsx_report,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
