from fastapi import FastAPI
from pydantic import BaseModel
from libsql_client import create_client
import os

app = FastAPI()

# Database connection
db = create_client(
    url=os.environ["TURSO_DATABASE_URL"],
    auth_token=os.environ["TURSO_AUTH_TOKEN"]
)

class User(BaseModel):
    username: str
    password: str
    email: str

@app.post("/register")
async def register_user(user: User):
    # WARNING: In a real app, hash your passwords!
    query = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    await db.execute(query, (user.username, user.password, user.email))
    return {"message": "User registered successfully"}