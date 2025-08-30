# Import required libraries
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Header  # FastAPI for web app, dependency injection, error handling, file uploads
from fastapi.responses import FileResponse  # For sen ding files as responses
import jwt  # For JSON Web Token (JWT) handling
import os  # For file system operations
import subprocess  # For running FFmpeg commands
import uuid  # For generating unique video IDs
import sqlite3  # For SQLite database operations
from functools import wraps  # For creating decorators
from pydantic import BaseModel  # For defining request body models
from typing import Optional  # For optional type hints
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # For handling Bearer token authentication

# Initialize FastAPI application
app = FastAPI()

# Secret key for JWT encoding/decoding
SECRET = "q9w8e7r6t5y4u3i2o1p"

# Define upload folder for videos
UPLOAD_FOLDER = 'uploads'

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hard-coded array of users with usernames and passwords
users = [
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"}
]

# Pydantic model for login request body
class LoginRequest(BaseModel):
    username: str  # Username field
    password: str  # Password field

# Initialize SQLite database for video metadata
def init_db():
    conn = sqlite3.connect('videos.db')  # Connect to SQLite database
    c = conn.cursor()  # Create a cursor object
    # Create videos table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id TEXT PRIMARY KEY, user TEXT, original_path TEXT, transcoded_path TEXT)''')
    conn.commit()  # Commit changes
    conn.close()  # Close connection

# Call init_db to set up the database
init_db()

# Helper function to get database connection
def get_db():
    return sqlite3.connect('videos.db')  # Return connection to videos.db

# Authentication dependency for validating JWT token
security = HTTPBearer()  # Initialize Bearer token security
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Extract token from Authorization header
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")  # Raise error if no token
    try:
        # Decode JWT token to get user info
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        current_user = data['user']  # Extract username
        return current_user  # Return current user
    except:
        raise HTTPException(status_code=401, detail="Token is invalid")  # Raise error if token is invalid

# Endpoint for user login
@app.post("/login")
async def login(login_data: LoginRequest):
    username = login_data.username  # Extract username from request body
    password = login_data.password  # Extract password from request body
    # Check if username and password match any user in the array
    for user in users:
        if user['username'] == username and user['password'] == password:
            # Generate JWT token for valid user
            token = jwt.encode({'user': username}, SECRET, algorithm="HS256")
            return {"token": token}  # Return token
    # Raise error for invalid credentials
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Endpoint for uploading videos
@app.post("/upload")
async def upload(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    # Check if a file was uploaded
    if not file:
        raise HTTPException(status_code=400, detail="No video file provided")
    # Check if a valid file was selected
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")
    video_id = str(uuid.uuid4())  # Generate unique ID for video
    # Create path for saving original video
    original_path = os.path.join(UPLOAD_FOLDER, f"{video_id}_{file.filename}")
    # Save the video file
    with open(original_path, "wb") as f:
        f.write(await file.read())  # Write file content to disk
    # Store video metadata in database
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create cursor
    # Insert video metadata into database
    c.execute("INSERT INTO videos (id, user, original_path, transcoded_path) VALUES (?, ?, ?, ?)",
              (video_id, current_user, original_path, None))
    conn.commit()  # Commit changes
    conn.close()  # Close connection
    # Return success message with video ID
    return {"message": "Video uploaded successfully", "video_id": video_id}

# Pydantic model for transcode request body
class TranscodeRequest(BaseModel):
    format: str = "webm"  # Target format, default to webm

# Endpoint for transcoding videos
@app.post("/transcode/{video_id}")
async def transcode(video_id: str, transcode_data: TranscodeRequest, current_user: str = Depends(get_current_user)):
    target_format = transcode_data.format  # Get target format from request body
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create cursor
    # Query video metadata by ID
    c.execute("SELECT original_path, user FROM videos WHERE id=?", (video_id,))
    row = c.fetchone()  # Fetch result
    if not row:
        conn.close()  # Close connection
        raise HTTPException(status_code=404, detail="Video not found")
    original_path, owner = row  # Extract path and owner
    # Check if user is authorized to transcode this video
    if owner != current_user:
        conn.close()  # Close connection
        raise HTTPException(status_code=403, detail="Not authorized to transcode this video")
    # Create path for transcoded video
    transcoded_path = original_path.rsplit('.', 1)[0] + '.' + target_format
    try:
        # Run FFmpeg to transcode video
        subprocess.run(['ffmpeg', '-i', original_path, transcoded_path], check=True)
    except subprocess.CalledProcessError:
        conn.close()  # Close connection
        raise HTTPException(status_code=500, detail="Transcoding failed")
    # Update database with transcoded path
    c.execute("UPDATE videos SET transcoded_path=? WHERE id=?", (transcoded_path, video_id))
    conn.commit()  # Commit changes
    conn.close()  # Close connection
    # Return success message with transcoded path
    return {"message": "Video transcoded successfully", "transcoded_path": transcoded_path}

# Endpoint for downloading videos
@app.get("/download/{video_id}")
async def download(video_id: str, current_user: str = Depends(get_current_user)):
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create cursor
    # Query video metadata by ID
    c.execute("SELECT original_path, transcoded_path, user FROM videos WHERE id=?", (video_id,))
    row = c.fetchone()  # Fetch result
    conn.close()  # Close connection
    if not row:
        raise HTTPException(status_code=404, detail="Video not found")
    original_path, transcoded_path, owner = row  # Extract paths and owner
    # Check if user is authorized to download
    if owner != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to download this video")
    # Use transcoded video if available, else original
    path = transcoded_path if transcoded_path else original_path
    return FileResponse(path, filename=os.path.basename(path))  # Send file to client

# Endpoint to list user's videos
@app.get("/files")
async def list_files(current_user: str = Depends(get_current_user)):
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create cursor
    # Query all videos for the current user
    c.execute("SELECT id, original_path, transcoded_path FROM videos WHERE user=?", (current_user,))
    rows = c.fetchall()  # Fetch all results
    conn.close()  # Close connection
    # Format video metadata as list of dictionaries
    files = [{"id": row[0], "original_path": row[1], "transcoded_path": row[2]} for row in rows]
    return {"files": files}  # Return list of files

# Run the FastAPI app (use `uvicorn main:app --reload` to run in development)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)