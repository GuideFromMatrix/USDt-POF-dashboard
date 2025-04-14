from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, List
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DATABASE_URL = "sqlite:///./pof.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    wallet = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

    balances = relationship("WalletBalance", back_populates="user")
    ab_tests = relationship("ABTestResultDB", back_populates="user")

class WalletBalance(Base):
    __tablename__ = "wallet_balances"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dashboard_balance = Column(Float, default=0.0)
    external_balance = Column(Float, default=0.0)

    user = relationship("UserDB", back_populates="balances")

class ABTestResultDB(Base):
    __tablename__ = "ab_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    result_id = Column(String)
    summary = Column(String)
    timestamp = Column(DateTime)

    user = relationship("UserDB", back_populates="ab_tests")

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    username: str
    email: str
    wallet: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    wallet: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ABTestResult(BaseModel):
    result_id: str
    summary: str
    timestamp: datetime

class BalanceResponse(BaseModel):
    dashboard_balance: float
    external_balance: float

class ABTestHistoryResponse(BaseModel):
    history: List[ABTestResult]

class ResetBalancesRequest(BaseModel):
    username: str

class TokenRequest(BaseModel):
    amount: float
    option: Optional[str] = "temporary"

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: UserDB = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def calculate_temporary_fee(amount: float) -> float:
    if amount <= 25000000:
        return 0.2 * amount
    elif amount <= 45000000:
        return 0.15 * amount
    elif amount <= 100000000:
        return 0.12 * amount
    elif amount <= 200000000:
        return 0.1 * amount
    else:
        return 0.05 * amount

def calculate_lifetime_fee(amount: float) -> float:
    if amount <= 25000000:
        return 0.40 * amount
    elif amount <= 45000000:
        return 0.35 * amount
    elif amount <= 100000000:
        return 0.30 * amount
    elif amount <= 200000000:
        return 0.25 * amount
    else:
        return 0.20 * amount

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = UserDB(username=user.username, email=user.email, wallet=user.wallet, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.add(WalletBalance(user_id=new_user.id))
    db.commit()
    return {"msg": "Signup successful"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": user.username}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/balance", response_model=BalanceResponse)
def get_balance(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    balance = db.query(WalletBalance).filter(WalletBalance.user_id == current_user.id).first()
    return {
        "dashboard_balance": balance.dashboard_balance,
        "external_balance": balance.external_balance
    }

@app.get("/ab-test-history", response_model=ABTestHistoryResponse)
def ab_test_history(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(ABTestResultDB).filter(ABTestResultDB.user_id == current_user.id).all()
    return {"history": results}

@app.post("/request-token")
def request_token(request: TokenRequest, current_user: UserDB = Depends(get_current_user)):
    option_type = request.option.lower()
    fee = calculate_temporary_fee(request.amount) if option_type == "temporary" else calculate_lifetime_fee(request.amount)
    readable_type = "Lifetime" if option_type == "lifetime" else "Temporary"
    return {
        "msg": f"Token request for {request.amount} submitted",
        "type": readable_type,
        "service_fee": fee,
        "note": "All service fees must be paid in USDT TETHER TRC20."
    }
