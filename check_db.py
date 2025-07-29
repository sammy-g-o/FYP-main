#!/usr/bin/env python3
"""
Simple script to check database contents
"""

import sqlite3
import os

def check_database():
    db_path = "students.db"
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in database:", [table[0] for table in tables])
        
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"Number of students: {student_count}")
        
        if student_count > 0:
            cursor.execute("SELECT student_id, name FROM students")
            students = cursor.fetchall()
            print("Students:")
            for student in students:
                print(f"  - {student[0]}: {student[1]}")
        
        # Check face embeddings
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        embedding_count = cursor.fetchone()[0]
        print(f"Number of face embeddings: {embedding_count}")
        
        # Check auth logs
        cursor.execute("SELECT COUNT(*) FROM auth_logs")
        log_count = cursor.fetchone()[0]
        print(f"Number of auth logs: {log_count}")
        
        if log_count > 0:
            cursor.execute("SELECT auth_result, COUNT(*) FROM auth_logs GROUP BY auth_result")
            results = cursor.fetchall()
            print("Auth results breakdown:")
            for result in results:
                print(f"  - {result[0]}: {result[1]} attempts")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()
