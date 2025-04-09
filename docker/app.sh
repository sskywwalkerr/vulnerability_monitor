#!/bin/bash

alembic revision --autogenerate -m "migr" && alembic upgrade head && gunicorn api.db.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

# Применяем миграции (если они есть)
#alembic upgrade head
#
## Запускаем gunicorn
#gunicorn api.db.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000