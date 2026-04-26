from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import verify_password, create_token, USERS, get_current_user

router = APIRouter()

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form.username)
    if not user or not verify_password(form.password, form.username):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token({"sub": form.username, "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"]
    }

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "full_name": current_user["full_name"]
    }

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}