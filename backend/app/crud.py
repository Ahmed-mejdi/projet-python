from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_student(db: Session, student_id: int):
    """Récupère un étudiant par son ID"""
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_email(db: Session, email: str):
    """Récupère un étudiant par son email"""
    return db.query(models.Student).filter(models.Student.email == email).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    """Récupère une liste d'étudiants avec pagination"""
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate):
    """Crée un nouvel étudiant"""
    hashed_password = pwd_context.hash(student.password)
    db_student = models.Student(
        email=student.email,
        hashed_password=hashed_password,
        full_name=student.full_name,
        age=student.age,
        department_id=student.department_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_department(db: Session, department_id: int):
    """Récupère un département par son ID"""
    return db.query(models.Department).filter(models.Department.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    """Récupère la liste des départements"""
    return db.query(models.Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    """Crée un nouveau département"""
    db_department = models.Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def get_formation(db: Session, formation_id: int):
    """Récupère une formation par son ID"""
    return db.query(models.Formation).filter(models.Formation.id == formation_id).first()

def get_formations(db: Session, skip: int = 0, limit: int = 100):
    """Récupère la liste des formations"""
    return db.query(models.Formation).offset(skip).limit(limit).all()

def create_formation(db: Session, formation: schemas.FormationCreate):
    """Crée une nouvelle formation"""
    db_formation = models.Formation(**formation.dict())
    db.add(db_formation)
    db.commit()
    db.refresh(db_formation)
    return db_formation

def enroll_student_to_formation(db: Session, student_id: int, formation_id: int):
    """Inscrit un étudiant à une formation"""
    student = get_student(db, student_id)
    formation = get_formation(db, formation_id)
    if student and formation:
        student.formations.append(formation)
        db.commit()
        return True
    return False

def get_admin_by_email(db: Session, email: str):
    """Récupère un admin par son email"""
    return db.query(models.Admin).filter(models.Admin.email == email).first()

def create_admin(db: Session, admin: schemas.AdminCreate):
    """Crée un nouvel administrateur"""
    hashed_password = pwd_context.hash(admin.password)
    db_admin = models.Admin(
        email=admin.email,
        hashed_password=hashed_password,
        full_name=admin.full_name
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin