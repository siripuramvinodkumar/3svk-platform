import os
import uuid
import pandas as pd
import io
import bcrypt
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from libsql_client import create_client
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialization
# Ensure serviceAccountKey.json is in your root directory
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

# FastAPI Initialization
app = FastAPI(docs_url="/docs", redoc_url="/redoc")

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
    # Ensure TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are set in your environment
    db = create_client(
        url=os.environ.get("TURSO_DATABASE_URL"),
        auth_token=os.environ.get("TURSO_AUTH_TOKEN")
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
    # 1. Truncate password to 72 bytes and convert to bytes
    password_bytes = user.password.encode('utf-8')[:72]
    
    # 2. Hash it using bcrypt directly
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # 3. Store the hash as a string in Turso
    query = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    try:
        await db.execute(query, (user.username, hashed_password.decode('utf-8'), user.email))
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload-bulk-credentials")
async def bulk_upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Read the file and normalize column names (strip whitespace and lowercase)
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate that the necessary columns exist
        required_cols = ['name', 'email', 'skill']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_cols}")

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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")