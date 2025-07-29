
import cv2
import dlib
import numpy as np
import os
import sqlite3
import torch
import time
from datetime import datetime
import uuid

from database_manager import DatabaseManager
from liveness_detection import LivenessDetector
from face_recognition_module import FaceRecognizer
from alert_manager import ProctorAlerter

class ExamProctorSystem:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.liveness_detector = LivenessDetector()
        # Explicitly initialize with the correct model to ensure 128-dim embeddings
        self.face_recognizer = FaceRecognizer(model_name="Facenet")
        self.alerter = ProctorAlerter()
        
        # Monitoring parameters
        self.monitoring_interval = 30  # seconds between checks
        self.last_check_time = 0
        
        # Current exam session
        self.current_session_id = None
        self.current_student_id = None
    
    def start_exam_session(self):
        """Start a new exam session"""
        self.current_session_id = str(uuid.uuid4())
        self.last_check_time = time.time()
        return self.current_session_id
    
    def authenticate_student(self, image):
        """Authenticate a student for exam access"""
        print("Starting authentication process...")
        
        # Step 1: Liveness Detection
        print("Performing liveness detection...")
        is_live, liveness_score, liveness_message = self.liveness_detector.check_liveness(image)
        print(f"Liveness result: {is_live}, score: {liveness_score}, message: {liveness_message}")
        
        if not is_live:
            # Log failed liveness check and send alert
            log_student_id = self.current_student_id if self.current_student_id else "UNKNOWN"
            self.db_manager.log_authentication(
                log_student_id, 
                "FAILED_LIVENESS", 
                liveness_score, 
                0.0, 
                self.current_session_id
            )
            self.alerter.log_alert(
                'LIVENESS_FAILURE',
                log_student_id,
                self.current_session_id,
                liveness_score,
                liveness_message
            )
            return False, None, liveness_score, 0.0, liveness_message
        
        # Step 2: Face Recognition
        print("Performing face recognition...")
        registered_embeddings = self.db_manager.get_all_embeddings()
        print(f"Retrieved {len(registered_embeddings)} registered embeddings")
        
        student_match, confidence_score, recognition_message = self.face_recognizer.recognize_face(
            image, registered_embeddings
        )
        print(f"Recognition result: {student_match}, score: {confidence_score}, message: {recognition_message}")
        
        if student_match:
            student_id, name = student_match
            self.current_student_id = student_id
            
            # Log successful authentication
            self.db_manager.log_authentication(
                student_id, 
                "SUCCESS", 
                liveness_score, 
                confidence_score, 
                self.current_session_id
            )
            
            return True, (student_id, name), liveness_score, confidence_score, "Authentication successful"
        else:
            # Log failed recognition and send alert
            log_student_id = self.current_student_id if self.current_student_id else "UNKNOWN"
            
            self.db_manager.log_authentication(
                log_student_id,
                "FAILED_RECOGNITION",
                liveness_score,
                confidence_score,
                self.current_session_id
            )
            self.alerter.log_alert(
                'RECOGNITION_FAILURE',
                log_student_id,
                self.current_session_id,
                confidence_score,
                recognition_message
            )
            
            return False, None, liveness_score, confidence_score, recognition_message
    
    def continuous_monitoring(self, image):
        """Perform periodic re-authentication during exam"""
        current_time = time.time()
        
        # Check if it's time for re-authentication
        if current_time - self.last_check_time >= self.monitoring_interval:
            self.last_check_time = current_time
            
            # Perform re-authentication
            success, student_match, liveness_score, confidence_score, message = self.authenticate_student(image)
            
            if not success:
                # Authentication failed during monitoring
                return False, message
            
            if student_match and student_match[0] != self.current_student_id:
                # Different student detected
                return False, "Different student detected during exam"
            
            # Re-authentication successful
            return True, "Re-authentication successful"
        
        # No check needed at this time
        return True, "No re-authentication needed"
    
    def main_loop(self):
        """Main system loop for exam proctoring"""
        # Start a new exam session
        session_id = self.start_exam_session()
        print(f"Starting exam session: {session_id}")
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        
        # Initial authentication
        authenticated = False
        student_name = None
        
        # Instructions for liveness check
        liveness_instructions = [
            "1. Look directly at the camera",
            "2. Blink naturally a few times",
            "3. Avoid wearing sunglasses or masks",
            "4. Ensure good lighting on your face"
        ]
        
        print("Press 'q' to quit at any time")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            # Make a copy for display
            display_frame = frame.copy()
            
            if not authenticated:
                # Initial authentication phase
                cv2.putText(display_frame, "Please look at the camera for authentication", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Add authentication instructions
                cv2.putText(display_frame, "Press 'a' to authenticate", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
                # Add liveness check instructions
                cv2.putText(display_frame, "Liveness Check Instructions:", 
                           (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                for i, instruction in enumerate(liveness_instructions):
                    cv2.putText(display_frame, instruction, 
                               (10, 130 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # Add quit instruction
                cv2.putText(display_frame, "Press 'q' to quit", 
                           (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow("Exam Proctoring System", display_frame)
                
                # Process authentication on key press - use waitKey correctly
                key = cv2.waitKeyEx(1) & 0xFF
                
                # Check for quit key
                if key == ord('q'):
                    print("Quitting application...")
                    break
                    
                if key == ord('a'):  # 'a' for authenticate
                    print("Manual authentication triggered...")
                    
                    # Show "Processing..." message
                    processing_frame = display_frame.copy()
                    cv2.putText(processing_frame, "Processing authentication...", 
                               (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
                    cv2.imshow("Exam Proctoring System", processing_frame)
                    cv2.waitKey(1)  # Update display
                    
                    # Perform authentication
                    success, student_match, liveness_score, confidence_score, message = self.authenticate_student(frame)
                    
                    if success:
                        authenticated = True
                        student_id, student_name = student_match
                        print(f"Authentication successful: {student_name} (ID: {student_id})")
                        print(f"Confidence score: {confidence_score:.4f}, Liveness score: {liveness_score:.4f}")
                    else:
                        print(f"Authentication failed: {message}")
                        # Display failure reason on screen
                        result_frame = display_frame.copy()
                        cv2.putText(result_frame, f"Authentication failed: {message}", 
                                   (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        cv2.imshow("Exam Proctoring System", result_frame)
                        cv2.waitKey(1)  # Update display immediately
            else:
                # Continuous monitoring phase
                monitor_success, monitor_message = self.continuous_monitoring(frame)
                
                status_color = (0, 255, 0) if monitor_success else (0, 0, 255)
                status_text = f"Student: {student_name} - Status: {'OK' if monitor_success else 'ALERT'}"
                
                cv2.putText(display_frame, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                
                if not monitor_success:
                    cv2.putText(display_frame, monitor_message, (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Add instructions for re-authentication
                    cv2.putText(display_frame, "Please look at the camera and stay still", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Add quit instruction
                cv2.putText(display_frame, "Press 'q' to quit", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow("Exam Proctoring System", display_frame)
                
                # Check for key press - use waitKey correctly
                key = cv2.waitKeyEx(1) & 0xFF
                
                # Check for quit key
                if key == ord('q'):
                    print("Quitting application...")
                    break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        
        # Force close any remaining windows
        for i in range(5):  # Try multiple times
            cv2.waitKey(1)

# Main execution
if __name__ == "__main__":
    system = ExamProctorSystem()
    
    # For registration (uncomment to use)
    
    # image_paths = [
    #     "./images/student1_front.jpg",
    #     "./images/student1_side.jpg",
    #     "./images/student1_glasses.jpg",
    #     "./images/student1_different_lighting.jpg"
    # ]
    # success, message = system.register_student_multiple_images("S12345", "John Doe", image_paths)

    # print(message)
    
    # Start the main system loop
    system.main_loop()
