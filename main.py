import os
import uuid
import pandas as pd
import io
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from libsql_client import create_client
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

# FastAPI Initialization
app = FastAPI(docs_url="/docs", redoc_url="/redoc")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

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

@app.api_route("/", methods=["GET", "HEAD", "OPTIONS"])
def read_root():
    return {"message": "Hello! 3SVK Platform is live."}

@app.post("/register")
async def register_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    query = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    await db.execute(query, (user.username, hashed_password, user.email))
    return {"message": "User registered successfully"}

@app.post("/upload-bulk-credentials")
async def bulk_upload(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    results = []
    for _, row in df.iterrows():
        cert_id = str(uuid.uuid4())
        db_firestore.collection("verifiable_credentials").document(cert_id).set({
            "student_name": row['name'],
            "email": row['email'],
            "skill": row['skill'],
            "status": "active",
            "issued_at": datetime.now()
        })
        results.append(cert_id)
    return {"message": f"Successfully processed {len(df)} credentials.", "ids": results}