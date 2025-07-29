#!/usr/bin/env python3
"""
Fix Embedding Dimensions Script

This script addresses the issue where face embeddings stored in the database
have 256 dimensions instead of the expected 128 dimensions for Facenet model.

The script provides options to:
1. Clear all existing embeddings and start fresh
2. Check current embedding dimensions in the database
3. Verify the current model configuration
"""

import sqlite3
import numpy as np
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer
from deepface import DeepFace
import cv2
import os

def check_current_model():
    """Check what the current FaceRecognizer model produces"""
    print("=== Checking Current Model Configuration ===")
    
    try:
        face_recognizer = FaceRecognizer(model_name="Facenet")
        print(f"Model: {face_recognizer.model_name}")
        print(f"Expected embedding size: {face_recognizer.embedding_size}")
        print(f"Threshold: {face_recognizer.threshold}")
        
        # Test with a dummy image
        test_img = np.zeros((160, 160, 3), dtype=np.uint8)
        cv2.circle(test_img, (80, 80), 50, (255, 255, 255), -1)
        
        embedding = face_recognizer.get_face_embedding(test_img)
        if embedding is not None:
            print(f"Actual embedding size produced: {embedding.shape[0]}")
            print("✓ Model is working correctly")
        else:
            print("✗ Model failed to produce embedding")
            
    except Exception as e:
        print(f"✗ Error testing model: {str(e)}")

def check_database_embeddings():
    """Check the dimensions of embeddings currently stored in the database"""
    print("\n=== Checking Database Embeddings ===")
    
    try:
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        total_count = cursor.fetchone()[0]
        print(f"Total embeddings in database: {total_count}")
        
        if total_count == 0:
            print("No embeddings found in database")
            conn.close()
            return
        
        cursor.execute("SELECT student_id, face_embedding FROM face_embeddings LIMIT 5")
        rows = cursor.fetchall()
        
        embedding_sizes = {}
        for student_id, embedding_blob in rows:
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            size = embedding.shape[0]
            if size not in embedding_sizes:
                embedding_sizes[size] = 0
            embedding_sizes[size] += 1
        
        print("Embedding dimensions found:")
        for size, count in embedding_sizes.items():
            status = "✓ Correct" if size == 128 else "✗ Incorrect"
            print(f"  {size} dimensions: {count} samples {status}")
        
        conn.close()
        
        # Check if there are any incorrect dimensions
        incorrect_dims = [size for size in embedding_sizes.keys() if size != 128]
        if incorrect_dims:
            print(f"\n⚠️  WARNING: Found embeddings with incorrect dimensions: {incorrect_dims}")
            print("This will cause compatibility issues with the current Facenet model (128 dimensions)")
            return False
        else:
            print("\n✓ All embeddings have correct dimensions (128)")
            return True
            
    except Exception as e:
        print(f"✗ Error checking database: {str(e)}")
        return False

def clear_all_embeddings():
    """Clear all embeddings from the database"""
    print("\n=== Clearing All Embeddings ===")
    
    try:
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        embedding_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        print(f"Found {embedding_count} embeddings and {student_count} students")
        
        if embedding_count == 0 and student_count == 0:
            print("Database is already empty")
            conn.close()
            return True
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete all {embedding_count} embeddings and {student_count} students? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Operation cancelled")
            conn.close()
            return False
        
        # Delete all data
        cursor.execute("DELETE FROM face_embeddings")
        cursor.execute("DELETE FROM students")
        
        conn.commit()
        conn.close()
        
        print("✓ All embeddings and students cleared successfully")
        print("You can now register students with the correct 128-dimensional embeddings")
        return True
        
    except Exception as e:
        print(f"✗ Error clearing database: {str(e)}")
        return False

def test_deepface_directly():
    """Test DeepFace directly to confirm it produces 128-dimensional embeddings"""
    print("\n=== Testing DeepFace Directly ===")
    
    try:
        # Create test image
        test_img = np.zeros((160, 160, 3), dtype=np.uint8)
        cv2.circle(test_img, (80, 80), 50, (255, 255, 255), -1)
        
        # Test Facenet model
        result = DeepFace.represent(
            img_path=test_img,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="opencv"
        )
        
        if isinstance(result, list) and len(result) > 0 and "embedding" in result[0]:
            embedding = np.array(result[0]["embedding"])
            print(f"DeepFace Facenet embedding size: {embedding.shape[0]}")
            if embedding.shape[0] == 128:
                print("✓ DeepFace is correctly producing 128-dimensional embeddings")
                return True
            else:
                print(f"✗ DeepFace is producing {embedding.shape[0]}-dimensional embeddings instead of 128")
                return False
        else:
            print("✗ DeepFace returned unexpected format")
            return False
            
    except Exception as e:
        print(f"✗ Error testing DeepFace: {str(e)}")
        return False

def main():
    """Main function to run the embedding dimension fix"""
    print("Face Embedding Dimension Fix Tool")
    print("=" * 50)
    
    # Step 1: Check current model
    check_current_model()
    
    # Step 2: Test DeepFace directly
    deepface_ok = test_deepface_directly()
    
    # Step 3: Check database embeddings
    db_ok = check_database_embeddings()
    
    # Step 4: Provide recommendations
    print("\n=== Recommendations ===")
    
    if deepface_ok and db_ok:
        print("✓ Everything looks good! No action needed.")
    elif deepface_ok and not db_ok:
        print("✗ Database contains embeddings with incorrect dimensions")
        print("Recommended actions:")
        print("1. Clear all existing embeddings (option below)")
        print("2. Re-register all students using the registration scripts")
        
        # Offer to clear embeddings
        print("\nOptions:")
        print("1. Clear all embeddings and start fresh")
        print("2. Exit and manually handle the issue")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            clear_all_embeddings()
        else:
            print("Exiting. Please manually resolve the embedding dimension issue.")
    else:
        print("✗ There are issues with the model configuration")
        print("Please check your DeepFace installation and model configuration")

if __name__ == "__main__":
    main()
