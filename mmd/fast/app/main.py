# app/main.py
from fastapi import FastAPI
from fast.app.api.routes import router
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmd.settings")
django.setup()


app = FastAPI(
    title="FastAPI Service",
    version="1.0.0"
)

app.include_router(router)
