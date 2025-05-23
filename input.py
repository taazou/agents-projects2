# File: app/models/company_model.py
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    """SQLAlchemy model for the Company table."""
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=True)
    founded_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to Employee; cascade deletion ensures that deleting a company removes its employees.
    employees = relationship("Employee", back_populates="company", cascade="all, delete")

# File: app/schemas/company_schema.py
from datetime import date
from typing import Optional
from pydantic import BaseModel

class CompanyBase(BaseModel):
    """Shared properties for Company."""
    name: str
    registration_number: Optional[str] = None
    founded_date: Optional[date] = None
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    """Properties to create a new Company."""
    pass

class CompanyUpdate(CompanyBase):
    """Properties to update an existing Company. All fields are optional."""
    pass

class CompanyOut(CompanyBase):
    """Properties to return via API."""
    id: int

    class Config:
        orm_mode = True

# File: app/routers/company_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.company_model import Company
from app.schemas.company_schema import CompanyCreate, CompanyOut, CompanyUpdate
from app.database import get_db

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/", response_model=List[CompanyOut])
def get_companies(db: Session = Depends(get_db)) -> List[CompanyOut]:
    """Retrieve all companies."""
    companies = db.query(Company).all()
    return companies

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)) -> CompanyOut:
    """Retrieve a specific company by its ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company

@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)) -> CompanyOut:
    """Create a new company."""
    company = Company(**company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, company_in: CompanyUpdate, db: Session = Depends(get_db)) -> CompanyOut:
    """Update an existing company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    update_data = company_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a company by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    db.delete(company)
    db.commit()

# File: app/models/employee_model.py
from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Employee(Base):
    """SQLAlchemy model for the Employee table."""
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(12,2), default=0.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to Company
    company = relationship("Company", back_populates="employees")

# File: app/schemas/employee_schema.py
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr

class EmployeeBase(BaseModel):
    """Shared properties for Employee."""
    company_id: int
    first_name: str
    last_name: str
    email: EmailStr
    hire_date: date
    salary: Optional[Decimal] = 0.00
    is_active: Optional[bool] = True

class EmployeeCreate(EmployeeBase):
    """Properties to create a new Employee."""
    pass

class EmployeeUpdate(BaseModel):
    """Properties to update an Employee. All fields are optional."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = None
    is_active: Optional[bool] = None

class EmployeeOut(EmployeeBase):
    """Properties to return via API."""
    id: int

    class Config:
        orm_mode = True

# File: app/routers/employee_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[EmployeeOut])
def get_employees(db: Session = Depends(get_db)) -> List[EmployeeOut]:
    """Retrieve all employees."""
    employees = db.query(Employee).all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeOut:
    """Retrieve an employee by ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeOut:
    """Create a new employee."""
    employee = Employee(**employee_in.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session = Depends(get_db)) -> EmployeeOut:
    """Update an existing employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    update_data = employee_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an employee by ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    db.delete(employee)
    db.commit()
