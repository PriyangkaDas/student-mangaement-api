from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import time
import jwt
from datetime import datetime, timedelta, timezone

# 1. Database Connection (SQLite)
DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Security Configuration ---
SECRET_KEY = "my-secret-token-key-for-development"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 2. Database Table Model
class StudentRecord(Base):
    __tablename__ = "students"
    roll_no = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)

# Create table on disk
Base.metadata.create_all(bind=engine)

# 3. Pydantic Models (Validation)
class StudentCreate(BaseModel):
    roll_no: int
    name: str
    branch: str
    semester: int = Field(..., ge=1, le=8, description="Semester must be between 1 and 8")
    cgpa: float = Field(..., ge=0.0, le=10.0, description="CGPA must be between 0.0 and 10.0")

class StudentUpdate(BaseModel):
    name: str | None = None
    branch: str | None = None
    semester: int | None = Field(default=None, ge=1, le=8, description="Semester must be between 1 and 8")
    cgpa: float | None = Field(default=None, ge=0.0, le=10.0, description="CGPA must be between 0.0 and 10.0")

class StudentResponse(BaseModel):
    roll_no: int
    name: str
    branch: str
    semester: int
    cgpa: float

    class Config:
        from_attributes = True

# 4. Dependency to manage database connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. FastAPI App
app = FastAPI(
    title="Student Record Management API",
    description="REST API connected to persistent SQLite database storage.",
    version="2.0.0"

)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# --- Token Verifier ---
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- ROUTES ---

@app.get("/")
def home():
    return {"status": "online", "database": "SQLite (Permanent Storage)"}

# --- Authentication Route ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simple hardcoded admin credentials
    if form_data.username != "admin" or form_data.password != "secret123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create token valid for 30 minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": form_data.username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

# GET all students with optional filters
@app.get("/students", response_model=List[StudentResponse])
def get_all_students(
    branch: str | None = None,
    min_cgpa: float | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(StudentRecord)
    if branch:
        query = query.filter(StudentRecord.branch.ilike(branch))
    if min_cgpa is not None:
        query = query.filter(StudentRecord.cgpa >= min_cgpa)
    return query.all()

# GET single student by Roll Number
@app.get("/students/{roll_no}", response_model=StudentResponse)
def get_student(roll_no: int, db: Session = Depends(get_db)):
    student = db.query(StudentRecord).filter(StudentRecord.roll_no == roll_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student

# POST: Add a new student
@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(StudentRecord).filter(StudentRecord.roll_no == student.roll_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this roll number already exists.")
    
    new_record = StudentRecord(
        roll_no=student.roll_no,
        name=student.name,
        branch=student.branch,
        semester=student.semester,
        cgpa=student.cgpa
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# DELETE: Remove a student
@app.delete("/students/{roll_no}")
def delete_student(
    roll_no: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(verify_token)
):
    student = db.query(StudentRecord).filter(StudentRecord.roll_no == roll_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    db.delete(student)
    db.commit()
    return {"message": f"Student with roll number {roll_no} permanently deleted."}
# PUT: Update an existing student's details
@app.put("/students/{roll_no}", response_model=StudentResponse)
def update_student(roll_no: int, update_data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(StudentRecord).filter(StudentRecord.roll_no == roll_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Convert incoming data to a dict, skipping fields the user didn't provide
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student