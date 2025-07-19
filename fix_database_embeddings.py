import os
import cv2
import numpy as np
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer
from deepface import DeepFace

def fix_database_embeddings():
    """Fix database embeddings by ensuring all use the same model"""
    db_manager = DatabaseManager()
    
    # Get all registered students
    students = db_manager.get_all_students()
    print(f"Found {len(students)} registered students")
    
    # Process each student
    for student_id, name in students:
        print(f"\nProcessing student: {name} (ID: {student_id})")
        
        # Check if student has images saved
        image_dir = f"student_images/{student_id}"
        if not os.path.exists(image_dir):
            print(f"No saved images found for {name}. Skipping.")
            continue
        
        # Get all images for this student
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if not image_files:
            print(f"No valid images found for {name}. Skipping.")
            continue
        
        print(f"Found {len(image_files)} images for {name}")
        
        # Delete all existing embeddings for this student
        db_manager.delete_student_embeddings(student_id)
        print(f"Deleted existing embeddings for {name}")
        
        # Process each image and create new embeddings
        successful_embeddings = 0
        for img_file in image_files:
            img_path = os.path.join(image_dir, img_file)
            image = cv2.imread(img_path)
            
            if image is None:
                print(f"Failed to load image: {img_path}")
                continue
            
            # Detect face
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) == 0:
                print(f"No face detected in: {img_path}")
                continue
            
            # Process the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_img = image[y:y+h, x:x+w]
            resized_face = cv2.resize(face_img, (160, 160))  # Facenet input size
            
            # Extract face embedding DIRECTLY using DeepFace with Facenet
            try:
                embedding_result = DeepFace.represent(
                    img_path=resized_face,
                    model_name="Facenet",  # Explicitly use Facenet
                    enforce_detection=False,
                    detector_backend="opencv"
                )
                
                # Handle different return formats
                if isinstance(embedding_result, list) and len(embedding_result) > 0:
                    if isinstance(embedding_result[0], dict) and "embedding" in embedding_result[0]:
                        embedding = np.array(embedding_result[0]["embedding"], dtype=np.float32)
                    else:
                        embedding = np.array(embedding_result[0], dtype=np.float32)
                elif isinstance(embedding_result, dict) and "embedding" in embedding_result:
                    embedding = np.array(embedding_result["embedding"], dtype=np.float32)
                else:
                    embedding = np.array(embedding_result, dtype=np.float32)
                
                # Verify embedding size
                if embedding.shape[0] != 128:
                    print(f"Wrong embedding size: {embedding.shape[0]}! Expected 128. Skipping.")
                    continue
                
                print(f"Generated embedding with size: {embedding.shape[0]} from {img_file}")
                
                # Register with new embedding
                description = f"Re-registered from {img_file}"
                success, message = db_manager.register_student(student_id, name, embedding, description)
                
                if success:
                    successful_embeddings += 1
                    print(f"Successfully re-registered embedding from {img_file}")
                else:
                    print(f"Failed to register embedding from {img_file}: {message}")
            
            except Exception as e:
                print(f"Error extracting embedding from {img_file}: {str(e)}")
        
        print(f"Re-registered {successful_embeddings}/{len(image_files)} embeddings for {name}")
    
    print("\nDatabase embedding fix complete!")

if __name__ == "__main__":
    fix_database_embeddings()


