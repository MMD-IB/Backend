# app/api/routes.py
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from Backend.mmd.user.services.user_service import get_users_psycopg
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

class MyUserSchema(BaseModel):
    id:int
    name:str
    surname:str
    email:str

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

@router.get("/users",response_model=MyUserSchema)
def api_get_users():
    rows = get_users_psycopg()
    return [{
        "id":r[0], "name":r[1], "surname":r[2], "email":r[3]
    }
    for r in rows
    ]