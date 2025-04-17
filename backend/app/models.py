from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Table d'association many-to-many entre étudiants et formations
student_formation_association = Table(
    'student_formation', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('formation_id', Integer, ForeignKey('formations.id'))
)

class Department(Base):
    """Modèle pour les départements universitaires"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(500))
    
    students = relationship("Student", back_populates="department")

class Formation(Base):
    """Modèle pour les formations/thèmes d'étude"""
    __tablename__ = "formations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(500))
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department")
    students = relationship("Student", secondary=student_formation_association, back_populates="formations")

class Student(Base):
    """Modèle pour les étudiants"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    age = Column(Integer)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="students")
    formations = relationship("Formation", secondary=student_formation_association, back_populates="students")

class Admin(Base):
    """Modèle pour les administrateurs"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))