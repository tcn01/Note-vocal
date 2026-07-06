@echo off
call venv\Scripts\activate
python -m alembic upgrade head
uvicorn app.main:app --reload
