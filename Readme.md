To run server in dev mode use:

fastapi dev main.py

To run with unicorn:

uvicorn backend:app --host 0.0.0.0 --port 8000


Models:

alembic revision --autogenerate -m "Initial migration"
alembic upgrade head