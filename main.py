import os
from fastapi import FastAPI
from pydantic import BaseModel
from libsql_client import create_client
from fastapi.middleware.cors import CORSMiddleware  # 1. Import this

app = FastAPI()

# 2. Add the CORS middleware block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (your GitHub Codespace domain)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the global variable
db = None

# Use the startup event to initialize the database
@app.on_event("startup")
async def startup():
    global db
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
    # Use the global db here
    await db.execute(query, (user.username, user.password, user.email))
    return {"message": "User registered successfully"}