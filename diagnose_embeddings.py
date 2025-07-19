import os
import sqlite3
import numpy as np
from deepface import DeepFace
import cv2
from database_manager import DatabaseManager

def diagnose_embeddings():
    """Diagnose embedding size issues"""
    print("Diagnosing embedding size issues...")
    
    # 1. Check what DeepFace actually returns for Facenet
    print("\nTesting DeepFace Facenet model:")
    test_img = np.zeros((160, 160, 3), dtype=np.uint8)
    cv2.circle(test_img, (80, 80), 50, (255, 255, 255), -1)
    
    try:
        embedding = DeepFace.represent(
            img_path=test_img,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="opencv"
        )
        
        # Handle different return formats
        if isinstance(embedding, list) and len(embedding) > 0:
            if isinstance(embedding[0], dict) and "embedding" in embedding[0]:
                emb = embedding[0]["embedding"]
            else:
                emb = embedding[0]
        elif isinstance(embedding, dict) and "embedding" in embedding:
            emb = embedding["embedding"]
        else:
            emb = embedding
            
        print(f"  Facenet embedding size: {len(emb)}")
        print(f"  Embedding type: {type(emb)}")
    except Exception as e:
        print(f"  Error with Facenet: {str(e)}")
    
    # 2. Check database embeddings
    db_manager = DatabaseManager()
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    print("\nChecking database embeddings:")
    try:
        cursor.execute("SELECT student_id, face_embedding FROM face_embeddings LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            student_id, embedding_blob = row
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            print(f"  Student ID: {student_id}")
            print(f"  Embedding size in database: {embedding.shape[0]}")
            print(f"  Embedding type: {embedding.dtype}")
        else:
            print("  No embeddings found in database")
    except Exception as e:
        print(f"  Error checking database: {str(e)}")
    
    conn.close()
    
    # 3. Check the register_student method
    print("\nAnalyzing register_student method:")
    print("  This method should be storing 128-dimensional embeddings")
    print("  If it's storing 256-dimensional embeddings, there might be a model mismatch")
    
    print("\nRecommendations:")
    print("1. Run 'python standardize_facenet.py' to rebuild the database")
    print("2. Modify the register_with_quality_check.py script to explicitly use Facenet")
    print("3. Check if any other scripts are using a different model")

if __name__ == "__main__":
    diagnose_embeddings()