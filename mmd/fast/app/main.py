# app/main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.api.routes import router
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmd.settings")
django.setup()



app = FastAPI(
    title="FastAPI Service",
    version="1.0.0"
)

app.include_router(router)