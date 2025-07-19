import sqlite3
import numpy as np
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='students.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create face embeddings table (multiple per student)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            face_embedding BLOB NOT NULL,
            description TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')
        
        # Create authentication logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            auth_result TEXT,
            liveness_score REAL,
            confidence_score REAL,
            exam_session_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def connect(self):
        """Create and return a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return None

    def register_student(self, student_id, name, face_embedding, description="Default embedding"):
        """Register a new student or add a new face embedding to existing student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if student already exists
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            student_exists = cursor.fetchone() is not None
            
            if not student_exists:
                # Add new student
                cursor.execute(
                    "INSERT INTO students (student_id, name) VALUES (?, ?)",
                    (student_id, name)
                )
            
            # Convert numpy array to binary blob
            face_embedding_blob = face_embedding.tobytes()
            
            # Add face embedding
            cursor.execute(
                "INSERT INTO face_embeddings (student_id, face_embedding, description) VALUES (?, ?, ?)",
                (student_id, face_embedding_blob, description)
            )
            
            conn.commit()
            conn.close()
            
            if student_exists:
                return True, f"New face embedding added for student {name} (ID: {student_id})"
            else:
                return True, f"Student {name} (ID: {student_id}) registered successfully"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def get_all_embeddings(self):
        """Get all registered face embeddings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.student_id, s.name, e.face_embedding 
                FROM students s
                JOIN face_embeddings e ON s.student_id = e.student_id
            """)
            results = cursor.fetchall()
            conn.close()
            
            # Process embeddings
            processed_results = []
            current_size = None
            
            for student_id, name, embedding_blob in results:
                # Convert BLOB to numpy array
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                
                # Set expected size if not set
                if current_size is None:
                    current_size = embedding.shape[0]
                    print(f"Using embeddings of size {current_size}")
                
                # Check if embedding size matches
                if embedding.shape[0] != current_size:
                    print(f"Skipping embedding for {name} with incompatible size {embedding.shape[0]}")
                    continue
                    
                processed_results.append((student_id, name, embedding))
            
            return processed_results
        except Exception as e:
            print(f"Error getting embeddings: {str(e)}")
            return []

    def get_student_embeddings(self, student_id):
        """Retrieve all face embeddings for a specific student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.student_id, s.name, e.face_embedding, e.description 
                FROM students s
                JOIN face_embeddings e ON s.student_id = e.student_id
                WHERE s.student_id = ?
            """, (student_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            result = []
            for row in rows:
                student_id, name, embedding_blob, description = row
                # Convert binary blob back to numpy array
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                result.append((student_id, name, embedding, description))
            
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None

    def delete_embedding(self, embedding_id):
        """Delete a specific face embedding"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM face_embeddings WHERE id = ?", (embedding_id,))
            
            conn.commit()
            conn.close()
            return True, "Embedding deleted successfully"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def log_authentication(self, student_id, auth_result, liveness_score, confidence_score, exam_session_id):
        """Log authentication attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO auth_logs (student_id, timestamp, auth_result, liveness_score, confidence_score, exam_session_id) VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, datetime.now(), auth_result, liveness_score, confidence_score, exam_session_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Logging error: {str(e)}")
            return False

    def get_student_by_id(self, student_id):
        """Retrieve a student by their ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id, name, face_embedding FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                student_id, name, embedding_blob = row
                # Convert binary blob back to numpy array
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                return student_id, name, embedding
            else:
                return None
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None

    def get_auth_logs(self, student_id=None, exam_session_id=None, limit=50):
        """Retrieve authentication logs with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM auth_logs"
            params = []
            
            # Add filters if provided
            if student_id or exam_session_id:
                query += " WHERE"
                
                if student_id:
                    query += " student_id = ?"
                    params.append(student_id)
                    
                    if exam_session_id:
                        query += " AND"
                
                if exam_session_id:
                    query += " exam_session_id = ?"
                    params.append(exam_session_id)
            
            # Add ordering and limit
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            logs = cursor.fetchall()
            conn.close()
            
            return logs
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []

    def delete_student(self, student_id):
        """Delete a student and all their face embeddings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if student exists
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            student_exists = cursor.fetchone() is not None
            
            if not student_exists:
                conn.close()
                return False, f"Student with ID {student_id} not found"
            
            # Get student name for confirmation message
            cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
            student_name = cursor.fetchone()[0]
            
            # Delete face embeddings first (due to foreign key constraint)
            cursor.execute("DELETE FROM face_embeddings WHERE student_id = ?", (student_id,))
            embeddings_deleted = cursor.rowcount
            
            # Delete student record
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            
            conn.commit()
            conn.close()
            
            return True, f"Student {student_name} (ID: {student_id}) deleted successfully with {embeddings_deleted} face embeddings"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def delete_student_embeddings(self, student_id):
        """Delete all embeddings for a specific student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM face_embeddings WHERE student_id = ?", (student_id,))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error deleting student embeddings: {str(e)}")
            return False

    def get_all_students(self):
        """Get all registered students"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id, name FROM students ORDER BY name")
            students = cursor.fetchall()
            conn.close()
            
            return students
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []




