from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

# Database configuration
DATABASE_URL = "sqlite:///./test.db"  # Using SQLite for simplicity; replace with your DB of choice

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models

class Company(Base):
    """SQLAlchemy model for the Company table."""
    __tablename__ = "company"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True, index=True)
    founded_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationship to Employee
    employees = relationship("Employee", back_populates="company", cascade="all, delete")


class Employee(Base):
    """SQLAlchemy model for the Employee table."""
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    
    # Relationship to Company
    company = relationship("Company", back_populates="employees")

# Create all tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255, description="Company name")
    registration_number: Optional[str] = Field(None, max_length=50, description="Unique registration number")
    founded_date: Optional[str] = Field(None, description="Founded date in YYYY-MM-DD format")
    is_active: Optional[bool] = Field(True, description="Status of the company")

class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass

class CompanyRead(CompanyBase):
    id: int
    
    class Config:
        orm_mode = True

class EmployeeBase(BaseModel):
    company_id: int = Field(..., description="Associated company's id")
    first_name: str = Field(..., max_length=100, description="Employee's first name")
    last_name: str = Field(..., max_length=100, description="Employee's last name")
    email: EmailStr = Field(..., description="Employee's unique email address")
    hire_date: str = Field(..., description="Hire date in YYYY-MM-DD format")
    salary: Optional[float] = Field(0.00, description="Employee salary")
    is_active: Optional[bool] = Field(True, description="Status of the employee")

class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee."""
    pass

class EmployeeRead(EmployeeBase):
    id: int
    
    class Config:
        orm_mode = True

# Dependency function to get DB session

def get_db() -> Session:
    """Provides a SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI Application Instance

app = FastAPI(
    title="Company and Employee API",
    description="API to manage companies and their employees",
    version="1.0.0"
)

# Allow CORS if necessary (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Company Endpoints

@app.post("/companies/", response_model=CompanyRead, summary="Create a new company")
def create_company(company: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    """Create a new company using the provided details."""
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.get("/companies/", response_model=List[CompanyRead], summary="List companies")
def list_companies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[Company]:
    """Retrieve a list of companies with pagination."""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

@app.get("/companies/{company_id}", response_model=CompanyRead, summary="Get company details")
def get_company(company_id: int, db: Session = Depends(get_db)) -> Company:
    """Retrieve details of a specific company by its ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.delete("/companies/{company_id}", response_model=dict, summary="Delete a company")
def delete_company(company_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a company and its employees by company ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"detail": "Company deleted"}

# Employee Endpoints

@app.post("/employees/", response_model=EmployeeRead, summary="Create a new employee")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)) -> Employee:
    """Create a new employee. Ensures that the associated company exists."""
    company = db.query(Company).filter(Company.id == employee.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Associated company not found")

    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[EmployeeRead], summary="List employees")
def list_employees(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[Employee]:
    """Retrieve a list of employees with pagination."""
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees

@app.get("/employees/{employee_id}", response_model=EmployeeRead, summary="Get employee details")
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> Employee:
    """Retrieve details of a specific employee by its ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.delete("/employees/{employee_id}", response_model=dict, summary="Delete an employee")
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete an employee by its ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"detail": "Employee deleted"}

# Test stub for manual testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)