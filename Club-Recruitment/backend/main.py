from fastapi import FastAPI, HTTPException, Header
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import functions
import jwt

app = FastAPI()

SECRET_KEY = "club_recruitment_secret_key_2026_secure"
ALGORITHM = "HS256"



def create_access_token(data):
    token_data = data.copy()
    token_data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data["type"] = "access"

    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data):
    token_data = data.copy()
    token_data["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    token_data["type"] = "refresh"

    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Header(...)):
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if user.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type" )

        return user

    except jwt.InvalidTokenError:
        raise HTTPException( status_code=401,  detail="Invalid or expired token" )


def check_role(user, role):
    if user["role"] != role:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

class UserRegister(BaseModel):
    username: str
    password: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


@app.get("/clubs")
def clubs(category=None):
    return functions.get_all_clubs(category=category)


@app.get("/clubs/{club_id}")
def club(club_id: int):

    response = functions.get_club(club_id)

    if response is None:
        raise HTTPException(status_code=404, detail="Club not found")

    return response


@app.post("/clubs")
def add_club(name,category, seats: int, deadline,token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "coordinator")

    if not name or not category or not deadline:
        raise HTTPException(status_code=422, detail="All fields are required")

    if category not in ["technical","cultural","sports","social", "literary"]:
        raise HTTPException(status_code=422,   detail="Invalid category")

    if seats < 1 or seats > 30:
        raise HTTPException( status_code=422,  detail="Seats must be between 1 and 30")

    try:
        datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")

    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid DateTime Format")

    return functions.add_club(name,category, seats,deadline)


@app.post("/clubs/{club_id}/applications")
def apply(club_id: int, roll_no: int,why_join: str,token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "student")

    if len(why_join) < 20:
        raise HTTPException(status_code=422, detail="Reason must be at least 20 characters")

    return functions.apply_to_club(club_id, roll_no,why_join )


@app.patch("/applications/{application_id}/status")
def update_status(application_id: int,status: str, token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "coordinator")

    response = functions.update_application_status(application_id,status)

    if response is None:
        raise HTTPException(status_code=404,  detail="Application not found")

    if response == "move_not_allowed":
        raise HTTPException(status_code=400,  detail="This status move is not allowed" )

    if response == "seats_full":
        raise HTTPException( status_code=400, detail="Club seats are full"  )

    return response


@app.patch("/applications/{application_id}/withdraw")
def withdraw(application_id: int,roll_no: int,token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "student")

    response = functions.withdraw_application(application_id,roll_no)

    if response is None:
        raise HTTPException(status_code=404,detail="Application not found")

    if response == "forbidden":
        raise HTTPException(status_code=403, detail="Not allowed")

    if response == "not_allowed":
        raise HTTPException(status_code=400,detail="Application cannot be withdrawn")

    return response


@app.get("/students/{roll_no}/applications")
def student_applications(roll_no: int, token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "student")

    return functions.get_student_applications(roll_no)


@app.get("/summary")
def summary(token: str = Header(...)):

    user = get_current_user(token)
    check_role(user, "coordinator")

    return functions.get_summary()


@app.post("/register")
def register(user: UserRegister):

    if user.role not in ["student", "coordinator"]:raise HTTPException(status_code=422,detail="Invalid role")

    response = functions.register_user(  user.username,user.password,user.role)

    if response is None:
        raise HTTPException( status_code=409, detail="Username already exists or registration failed"  )

    return response


@app.post("/login")
def login(user: UserLogin):

    response = functions.login_user(user.username,  user.password )

    if response is None:
        raise HTTPException(status_code=401,  detail="Invalid username or password" )

    user_data = {
        "id": response["id"],
        "username": response["username"],
        "role": response["role"]
    }

    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@app.post("/refresh")
def refresh_access_token(refresh_token: str = Header(...)):

    try:
        user = jwt.decode(refresh_token,SECRET_KEY,algorithms=[ALGORITHM]
        )

        if user.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token"  )

        user_data = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }

        new_access_token = create_access_token(user_data)

        return {
            "access_token": new_access_token
        }

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")