from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import SessionLocal, engine
from typing import List
from datetime import timedelta

# Création des tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes pour les étudiants
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Crée un nouvel étudiant"""
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_student(db=db, student=student)

@app.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des étudiants"""
    students = crud.get_students(db, skip=skip, limit=limit)
    return students

@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    """Récupère un étudiant par son ID"""
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

# Routes pour l'authentification
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.StudentLogin, db: Session = Depends(get_db)):
    """Authentifie un étudiant et retourne un token JWT"""
    student = auth.authenticate_student(db, form_data.email, form_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": student.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/students/me/", response_model=schemas.Student)
async def read_students_me(current_student: schemas.Student = Depends(auth.get_current_student)):
    """Récupère les informations de l'étudiant courant"""
    return current_student

# Routes pour les départements
@app.post("/departments/", response_model=schemas.Department)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    """Crée un nouveau département"""
    return crud.create_department(db=db, department=department)

@app.get("/departments/", response_model=List[schemas.Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des départements"""
    departments = crud.get_departments(db, skip=skip, limit=limit)
    return departments

# Routes pour les formations
@app.post("/formations/", response_model=schemas.Formation)
def create_formation(formation: schemas.FormationCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle formation"""
    return crud.create_formation(db=db, formation=formation)

@app.get("/formations/", response_model=List[schemas.Formation])
def read_formations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des formations"""
    formations = crud.get_formations(db, skip=skip, limit=limit)
    return formations

@app.post("/formations/{formation_id}/enroll/{student_id}")
def enroll_student(
    formation_id: int, 
    student_id: int, 
    db: Session = Depends(get_db),
    current_student: schemas.Student = Depends(auth.get_current_student)
):
    """Inscrit un étudiant à une formation"""
    if current_student.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to enroll another student")
    
    success = crud.enroll_student_to_formation(db, student_id=student_id, formation_id=formation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student or formation not found")
    return {"message": "Enrollment successful"}

# Routes pour les admins
@app.post("/admin/login", response_model=schemas.Token)
async def admin_login(form_data: schemas.StudentLogin, db: Session = Depends(get_db)):
    """Authentifie un admin et retourne un token JWT"""
    admin = auth.authenticate_admin(db, form_data.email, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": admin.email, "is_admin": True}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/admin/", response_model=schemas.Admin)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    """Crée un nouvel administrateur"""
    db_admin = crud.get_admin_by_email(db, email=admin.email)
    if db_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_admin(db=db, admin=admin)

@app.get("/admin/students/", response_model=List[schemas.Student])
def admin_read_students(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_admin: schemas.Admin = Depends(auth.get_current_admin)
):
    """Récupère la liste des étudiants (admin seulement)"""
    return crud.get_students(db, skip=skip, limit=limit)