import os
import sqlite3
from database_manager import DatabaseManager

def reset_database():
    """Reset the database by clearing all face embeddings"""
    db_manager = DatabaseManager()
    
    # Connect to database
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get list of students before clearing
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    
    # Clear all face embeddings
    cursor.execute("DELETE FROM face_embeddings")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Cleared all face embeddings from database.")
    print(f"Retained {len(students)} student records without embeddings.")
    
    if students:
        print("\nRemaining students (need to re-register faces):")
        for student_id, name in students:
            print(f"  - {name} (ID: {student_id})")
    
    print("\nPlease re-register all students using the registration script.")

if __name__ == "__main__":
    reset_database()