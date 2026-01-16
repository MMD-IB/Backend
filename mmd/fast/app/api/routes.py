# app/api/routes.py
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from webapp.services.auth_service import login_user, register_user

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}


class LoginSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    name: str
    surname: str
    email: str
    password: str

@router.post("/login")
def api_login(data: LoginSchema):
    user = login_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali errate") #Lancia un eccezzione inviando una risposta HHTP 401 Non autorizzato
    return user

@router.post("/register")
def api_register(data: RegisterSchema):
    ok = register_user(
        data.name, data.surname, data.email, data.password
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Utente già registrato")
    return {"status": "ok"}



