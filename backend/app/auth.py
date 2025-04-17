from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import schemas, models, crud
from .database import SessionLocal
from sqlalchemy.orm import Session

# Configuration de sécurité
SECRET_KEY = "votre_secret_key_super_secrete"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    """Fournit une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str):
    """Vérifie si le mot de passe correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Génère un hash du mot de passe"""
    return pwd_context.hash(password)

def authenticate_student(db: Session, email: str, password: str):
    """Authentifie un étudiant"""
    student = crud.get_student_by_email(db, email)
    if not student:
        return False
    if not verify_password(password, student.hashed_password):
        return False
    return student

def authenticate_admin(db: Session, email: str, password: str):
    """Authentifie un administrateur"""
    admin = crud.get_admin_by_email(db, email)
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_student(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupère l'étudiant courant à partir du token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    student = crud.get_student_by_email(db, email=token_data.email)
    if student is None:
        raise credentials_exception
    return student

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupère l'admin courant à partir du token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    admin = crud.get_admin_by_email(db, email=token_data.email)
    if admin is None:
        raise credentials_exception
    return admin