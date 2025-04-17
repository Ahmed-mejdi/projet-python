from pydantic import BaseModel, EmailStr
from typing import List, Optional

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    
    class Config:
        orm_mode = True

class FormationBase(BaseModel):
    title: str
    description: Optional[str] = None
    department_id: int

class FormationCreate(FormationBase):
    pass

class Formation(FormationBase):
    id: int
    
    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    email: EmailStr
    full_name: str
    age: Optional[int] = None
    department_id: Optional[int] = None

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int
    department: Optional[Department] = None
    formations: List[Formation] = []
    
    class Config:
        orm_mode = True

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class AdminBase(BaseModel):
    email: EmailStr
    full_name: str

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: bool = False