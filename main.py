import os
from fastapi import FastAPI
from pydantic import BaseModel
from libsql_client import create_client
from fastapi.middleware.cors import CORSMiddleware
# Import passlib for security
from passlib.context import CryptContext

# Change this line
app = FastAPI(docs_url="/docs", redoc_url="/redoc")

# Initialize the hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS middleware configuration - Set to "*" for debugging to rule out origin issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Global database variable
db = None

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

# Updated to explicitly handle multiple methods to fix 405 errors
@app.api_route("/", methods=["GET", "HEAD", "OPTIONS"])
def read_root():
    return {"message": "Hello! 3SVK Platform is live."}

@app.post("/register")
async def register_user(user: User):
    # 1. Hash the password before saving it to the database
    hashed_password = pwd_context.hash(user.password)
    
    # 2. Use the hashed_password in the query
    query = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    
    # 3. Execute the database operation
    await db.execute(query, (user.username, hashed_password, user.email))
    
    return {"message": "User registered successfully"}