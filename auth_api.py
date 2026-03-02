from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import os, jwt
from db.database import FlatFileDB

app = FastAPI(title="Auth API")

db = FlatFileDB()

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ADMIN_ID = os.environ.get("ADMIN_ID", "admin")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(person_id: str, password: str):
    # load raw record to get hashed password
    raw = db._load_data()
    for u in raw.get("userdb", []):
        if u["person_id"] == person_id:
            if db.security.verify_password(u["password"], password):
                user = db.get_decrypted_user(person_id)
                if not user["enabled"]:
                    return None
                return user
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        person_id: str = payload.get("sub")
        if person_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.get_decrypted_user(person_id)
    if not user:
        raise credentials_exception
    if not user["enabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def admin_required(current_user=Depends(get_current_user)):
    if current_user["person_id"] != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


@app.on_event("startup")
def ensure_admin():
    data = db._load_data()
    if not data.get("userdb"):
        admin_pass = os.environ.get("ADMIN_PASS", "admin")
        # first-time bootstrap
        db.add_secure_user({
            "person_id": ADMIN_ID,
            "first_name": "Admin",
            "last_name": "User",
            "address": "",
            "password": admin_pass,
        })


@app.post("/token")
def login_for_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["person_id"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/register")
def register_user(user: dict, current_user=Depends(admin_required)):
    # only admin may register new accounts
    if db.user_exists(user["person_id"]):
        raise HTTPException(status_code=400, detail="User already exists")
    db.add_secure_user(user)
    return {"person_id": user["person_id"]}


@app.post("/users/{person_id}/password")
def change_password(person_id: str, body: dict, current_user=Depends(get_current_user)):
    new_pw = body.get("new_password")
    if current_user["person_id"] != person_id and current_user["person_id"] != ADMIN_ID:
        raise HTTPException(status_code=403)
    success = db.change_password(person_id, new_pw)
    if not success:
        raise HTTPException(status_code=404)
    return {"status": "ok"}


@app.post("/users/{person_id}/deactivate")
def deactivate_account(person_id: str, current_user=Depends(get_current_user)):
    if current_user["person_id"] != person_id:
        raise HTTPException(status_code=403)
    db.update_user_status(person_id, False)
    return {"status": "deactivated"}


@app.post("/users/{person_id}/activate")
def activate_account(person_id: str, current_user=Depends(admin_required)):
    db.update_user_status(person_id, True)
    return {"status": "activated"}
