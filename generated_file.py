[
  {
    "filename": "company_app.py",
    "content": "from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import Session
from app.database import Base, get_db  # Assumes a separate module for DB setup


class Company(Base):
    """SQLAlchemy model for the company table."""
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True, index=True)
    founded_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)


class CompanyBase(BaseModel):
    """Base schema for company."""
    name: str = Field(..., max_length=255, description="Name of the company")
    registration_number: Optional[str] = Field(None, max_length=50, description="Unique registration number")
    founded_date: Optional[str] = Field(None, description="Date when the company was founded (YYYY-MM-DD)")
    is_active: Optional[bool] = Field(True, description="Active status")


class CompanyCreate(CompanyBase):
    """Schema used when creating a company."""
    pass


class CompanyUpdate(CompanyBase):
    """Schema used when updating a company. All fields are optional."""
    pass


class CompanyOut(CompanyBase):
    """Schema for outputting company details."""
    id: int

    class Config:
        orm_mode = True


router = APIRouter(prefix='/companies', tags=['Companies'])


@router.get('/', response_model=List[CompanyOut])
async def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[CompanyOut]:
    """Retrieve a list of companies with pagination."""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies


@router.post('/', response_model=CompanyOut, status_code=201)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)) -> CompanyOut:
    """Create a new company record."""
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get('/{company_id}', response_model=CompanyOut)
async def get_company(company_id: int, db: Session = Depends(get_db)) -> CompanyOut:
    """Retrieve a company by its ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail='Company not found')
    return company


@router.put('/{company_id}', response_model=CompanyOut)
async def update_company(company_id: int, company_update: CompanyUpdate, db: Session = Depends(get_db)) -> CompanyOut:
    """Update an existing company record."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail='Company not found')
    update_data = company_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete('/{company_id}', response_model=dict)
async def delete_company(company_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a company by its ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail='Company not found')
    db.delete(company)
    db.commit()
    return {'detail': 'Company deleted'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.company_app:router', host='127.0.0.1', port=8000, reload=True)"
  },
  {
    "filename": "employee_app.py",
    "content": "from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import Session, relationship
from app.database import Base, get_db  # Assumes a separate module for DB setup
from app.company_app import Company  # Import the Company model for foreign key relationship


class Employee(Base):
    """SQLAlchemy model for the employee table."""
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), default=0.00)
    is_active = Column(Boolean, default=True)

    company = relationship('Company', backref='employees')

Index('idx_employee_email', Employee.email)


class EmployeeBase(BaseModel):
    """Base schema for employee."""
    company_id: int = Field(..., description='ID of the company the employee belongs to')
    first_name: str = Field(..., max_length=100, description='Employee first name')
    last_name: str = Field(..., max_length=100, description='Employee last name')
    email: str = Field(..., max_length=255, description='Employee unique email address')
    hire_date: str = Field(..., description='Hire date in YYYY-MM-DD format')
    salary: Optional[float] = Field(0.00, description='Employee salary')
    is_active: Optional[bool] = Field(True, description='Active status of the employee')


class EmployeeCreate(EmployeeBase):
    """Schema used when creating an employee record."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema used when updating an employee record. All fields are optional."""
    company_id: Optional[int] = Field(None, description='ID of the company')
    first_name: Optional[str] = Field(None, max_length=100, description='First name')
    last_name: Optional[str] = Field(None, max_length=100, description='Last name')
    email: Optional[str] = Field(None, max_length=255, description='Email address')
    hire_date: Optional[str] = Field(None, description='Hire date in YYYY-MM-DD format')
    salary: Optional[float] = Field(None, description='Salary')
    is_active: Optional[bool] = Field(None, description='Active status')


class EmployeeOut(EmployeeBase):
    """Schema for outputting employee details."""
    id: int

    class Config:
        orm_mode = True


router = APIRouter(prefix='/employees', tags=['Employees'])


@router.get('/', response_model=List[EmployeeOut])
async def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[EmployeeOut]:
    """Retrieve a list of employees with pagination."""
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees


@router.post('/', response_model=EmployeeOut, status_code=201)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeOut:
    """Create a new employee record."""
    company = db.query(Company).filter(Company.id == employee.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail='Company does not exist')
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get('/{employee_id}', response_model=EmployeeOut)
async def get_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeOut:
    """Retrieve an employee by its ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee not found')
    return employee


@router.put('/{employee_id}', response_model=EmployeeOut)
async def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)) -> EmployeeOut:
    """Update an existing employee record."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee not found')
    update_data = employee_update.dict(exclude_unset=True)
    if 'company_id' in update_data and update_data['company_id'] is not None:
        company = db.query(Company).filter(Company.id == update_data['company_id']).first()
        if not company:
            raise HTTPException(status_code=400, detail='Referenced company does not exist')
    for key, value in update_data.items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete('/{employee_id}', response_model=dict)
async def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete an employee by its ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee not found')
    db.delete(employee)
    db.commit()
    return {'detail': 'Employee deleted'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.employee_app:router', host='127.0.0.1', port=8001, reload=True)"
  }
]