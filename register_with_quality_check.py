import cv2
import numpy as np
import os
import time
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer
from deepface import DeepFace

def register_with_quality_check():
    """Register a student with quality checks for better face recognition"""
    db_manager = DatabaseManager()
    face_recognizer = FaceRecognizer()
    
    # Get student details
    student_id = input("Enter student ID: ")
    name = input("Enter student name: ")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Create directory for saving images
    save_dir = f"student_images/{student_id}"
    os.makedirs(save_dir, exist_ok=True)
    
    images_captured = 0
    max_images = 5
    
    print(f"Starting high-quality registration for {name} (ID: {student_id})")
    print("Position your face in different angles for better recognition")
    print("Press SPACE to capture an image, ESC to finish")
    
    while images_captured < max_images:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Display instructions
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Student: {name} (ID: {student_id})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Captured: {images_captured}/{max_images}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, "Press SPACE to capture, ESC to finish", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Face detection for guidance
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_recognizer.face_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        # Draw rectangle around detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow("High-Quality Registration", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            break
        elif key == 32:  # SPACE key
            # Only proceed if a face is detected
            if len(faces) == 0:
                cv2.putText(display_frame, "No face detected! Please position yourself better.", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("High-Quality Registration", display_frame)
                cv2.waitKey(1500)
                continue
            
            # Process the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Quality check - face size
            if w < 100 or h < 100:
                cv2.putText(display_frame, "Face too small! Move closer to the camera.", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("High-Quality Registration", display_frame)
                cv2.waitKey(1500)
                continue
            
            # Extract face region
            face_img = frame[y:y+h, x:x+w]
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
                    cv2.putText(display_frame, f"Wrong embedding size: {embedding.shape[0]}! Expected 128.", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow("High-Quality Registration", display_frame)
                    cv2.waitKey(1500)
                    continue
                
                print(f"Generated embedding with size: {embedding.shape[0]}")
                
                # Save the image
                timestamp = int(time.time())
                image_path = os.path.join(save_dir, f"face_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)
                
                # Register in database
                description = f"High-quality image {images_captured+1}"
                success, message = db_manager.register_student(student_id, name, embedding, description)
                
                if success:
                    images_captured += 1
                    cv2.putText(display_frame, f"Image {images_captured} captured successfully!", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame, f"Failed to register: {message}", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow("High-Quality Registration", display_frame)
                cv2.waitKey(1500)  # Show result for 1.5 seconds
                
            except Exception as e:
                print(f"Error extracting embedding: {str(e)}")
                cv2.putText(display_frame, f"Error: {str(e)}", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("High-Quality Registration", display_frame)
                cv2.waitKey(1500)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Force close any remaining windows
    for i in range(5):
        cv2.waitKey(1)
    
    if images_captured > 0:
        print(f"Successfully registered {images_captured} high-quality images for {name} (ID: {student_id})")
    else:
        print("Failed to register any images")

if __name__ == "__main__":
    register_with_quality_check()
