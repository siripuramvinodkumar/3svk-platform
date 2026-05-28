from fastapi import FastAPI
from pydantic import BaseModel
from libsql_client import create_client
import os

app = FastAPI()

db = create_client(
    url=os.environ["TURSO_DATABASE_URL"],
    auth_token=os.environ["TURSO_AUTH_TOKEN"]
)

class User(BaseModel):
    username: str
    password: str
    email: str

@app.get("/")
def read_root():
    return {"message": "Hello! 3SVK Platform is live."}

@app.post("/register")
async def register_user(user: User):
    query = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    await db.execute(query, (user.username, user.password, user.email))
    return {"message": "User registered successfully"}