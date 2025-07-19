import os
import sqlite3
from database_manager import DatabaseManager

def rebuild_database():
    """Completely rebuild the database tables"""
    db_manager = DatabaseManager()
    
    # Connect to database
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    print(f"Rebuilding database at: {db_manager.db_path}")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS face_embeddings")
    cursor.execute("DROP TABLE IF EXISTS authentication_logs")
    cursor.execute("DROP TABLE IF EXISTS students")
    
    # Create tables from scratch
    cursor.execute("""
        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE face_embeddings (
            embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            face_embedding BLOB NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE authentication_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            liveness_score REAL,
            recognition_score REAL,
            session_id TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    """)
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Database tables have been completely rebuilt.")
    print("Please register students using the registration script.")

if __name__ == "__main__":
    rebuild_database()