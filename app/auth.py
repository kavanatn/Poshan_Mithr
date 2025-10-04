"""
Authentication and security utilities
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "nutrition-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer(auto_error=False)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    try:
        # Force database initialization check
        from app.models import Base, engine
        Base.metadata.create_all(bind=engine)
        
        user = get_user_by_username(db, username)
        
        # If no user found, try initializing database
        if not user:
            print(f"User '{username}' not found, checking if DB is seeded...")
            from app.database import init_db
            try:
                init_db()  # This will skip if already initialized
                user = get_user_by_username(db, username)
            except Exception as e:
                print(f"Database init error during auth: {e}")
        
        if not user:
            print(f"❌ User '{username}' does not exist in database")
            return False
            
        if not verify_password(password, user.password):
            print(f"❌ Invalid password for user '{username}'")
            return False
            
        print(f"✅ User '{username}' authenticated successfully")
        return user
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None
    return get_user_by_username(db, username=username)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user = get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker

