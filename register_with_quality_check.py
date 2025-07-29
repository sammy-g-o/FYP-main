import cv2
import numpy as np
import os
import time
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer

class QualityRegistration:
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Explicitly initialize with the correct model to ensure 128-dim embeddings
        self.face_recognizer = FaceRecognizer(model_name="Facenet")
        self.capture_duration = 3  # seconds
        self.num_images_to_capture = 5

    def register_student(self):
        """
        Guides the user through a high-quality registration process.
        """
        print("--- Student Registration with Quality Check ---")
        
        # 1. Get student details
        student_id = input("Enter Student ID: ").strip()
        name = input("Enter Student Name: ").strip()
        
        if not student_id or not name:
            print("Student ID and Name cannot be empty.")
            return

        # 2. Capture multiple high-quality images
        captured_embeddings = self._capture_high_quality_images()
        
        if not captured_embeddings:
            print("Registration failed: Could not capture enough high-quality images.")
            return

        # 3. Average the embeddings to create a robust profile
        if len(captured_embeddings) < self.num_images_to_capture:
            print(f"Warning: Only captured {len(captured_embeddings)} images. Registration may be less accurate.")

        final_embedding = np.mean(captured_embeddings, axis=0)

        # 4. Save to database
        success, message = self.db_manager.register_student(student_id, name, final_embedding)
        
        if success:
            print(f"\n{message}")
            print("Student registration completed successfully with a high-quality embedding.")
        else:
            print(f"\nRegistration failed: {message}")

    def _capture_high_quality_images(self):
        """
        Captures multiple images and performs quality checks.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return []

        embeddings = []
        
        instructions = [
            "Look straight ahead",
            "Turn slightly left",
            "Turn slightly right",
            "Tilt head up",
            "Tilt head down"
        ]

        for i in range(self.num_images_to_capture):
            print(f"\nPrepare for image {i+1}/{self.num_images_to_capture}: {instructions[i]}")
            print("Press 'c' to capture when ready. Press 'q' to quit.")
            
            captured = False
            while not captured:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame.")
                    break
                
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Pose: {instructions[i]}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(display_frame, "Press 'c' to capture", 
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Registration Capture", display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return []
                elif key == ord('c'):
                    # Quality Check: Get Embedding
                    embedding = self.face_recognizer.get_face_embedding(frame)
                    if embedding is None:
                        print("Quality check failed: Could not generate embedding. Please ensure your face is clearly visible and well-lit.")
                        continue
                    
                    embeddings.append(embedding)
                    print("Image captured and passed quality checks.")
                    captured = True
                    
                    # Briefly show the captured frame
                    cv2.imshow("Captured Image", frame)
                    cv2.waitKey(1000)

        cap.release()
        cv2.destroyAllWindows()
        return embeddings

if __name__ == "__main__":
    registration_system = QualityRegistration()
    registration_system.register_student()
