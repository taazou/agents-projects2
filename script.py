# File: company_model.py
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    """SQLAlchemy model for the Company table."""
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True)
    founded_date = Column(Date)
    is_active = Column(Boolean, default=True)

    # Define relationship to Employee. Note: This assumes Employee model is imported later to avoid circular dependency.
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"

# File: company_schemas.py
from datetime import date
from typing import Optional
from pydantic import BaseModel

class CompanyBase(BaseModel):
    """Base schema for Company."""
    name: str
    registration_number: Optional[str] = None
    founded_date: Optional[date] = None
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    """Schema used when creating a new company."""
    pass

class CompanyRead(CompanyBase):
    """Schema used for reading company data."""
    id: int

    class Config:
        orm_mode = True

# File: company_router.py
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead
from app.database import get_db

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanyRead)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    """Create a new company.
    
    :param company: Company data
    :param db: Database session dependency
    :return: Created Company
    """
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/", response_model=List[CompanyRead])
def get_companies(db: Session = Depends(get_db)) -> List[Company]:
    """Retrieve all companies.
    
    :param db: Database session dependency
    :return: List of companies
    """
    companies = db.query(Company).all()
    return companies

# File: employee_model.py
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    """SQLAlchemy model for the Employee table."""
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), default=0.00)
    is_active = Column(Boolean, default=True)

    # Relationship to Company; assumes the Company model defines a matching relationship
    company = relationship("Company", back_populates="employees")

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}')>"

# File: employee_schemas.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr

class EmployeeBase(BaseModel):
    """Base schema for Employee."""
    company_id: int
    first_name: str
    last_name: str
    email: EmailStr
    hire_date: date
    salary: Optional[float] = 0.00
    is_active: Optional[bool] = True

class EmployeeCreate(EmployeeBase):
    """Schema used when creating a new employee."""
    pass

class EmployeeRead(EmployeeBase):
    """Schema used for reading employee data."""
    id: int

    class Config:
        orm_mode = True

# File: employee_router.py
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeRead)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)) -> Employee:
    """Create a new employee.
    
    :param employee: Employee data
    :param db: Database session dependency
    :return: Created Employee
    """
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/", response_model=List[EmployeeRead])
def get_employees(db: Session = Depends(get_db)) -> List[Employee]:
    """Retrieve all employees.
    
    :param db: Database session dependency
    :return: List of employees
    """
    employees = db.query(Employee).all()
    return employees
