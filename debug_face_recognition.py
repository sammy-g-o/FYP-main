import cv2
import numpy as np
import os
import time
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer

def debug_face_recognition():
    """Debug tool to visualize face recognition process"""
    db_manager = DatabaseManager()
    face_recognizer = FaceRecognizer()
    
    # Get all registered embeddings
    registered_embeddings = db_manager.get_all_embeddings()
    print(f"Found {len(registered_embeddings)} registered embeddings")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Press 'q' to quit, 's' to save debug image")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Make a copy for display
        display_frame = frame.copy()
        
        # Extract face embedding
        embedding = face_recognizer.get_face_embedding(frame)
        
        if embedding is not None:
            # Compare with all registered embeddings
            results = []
            for student_id, name, reg_embedding in registered_embeddings:
                if embedding.shape == reg_embedding.shape:
                    # Calculate raw similarity
                    raw_similarity = np.dot(embedding, reg_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(reg_embedding))
                    # Normalize to 0-1
                    normalized_similarity = (raw_similarity + 1) / 2
                    results.append((student_id, name, raw_similarity, normalized_similarity))
            
            # Sort by normalized similarity
            results.sort(key=lambda x: x[3], reverse=True)
            
            # Display results
            cv2.putText(display_frame, "Face Recognition Debug", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            y_pos = 60
            for i, (student_id, name, raw_sim, norm_sim) in enumerate(results[:5]):  # Show top 5
                color = (0, 255, 0) if norm_sim >= face_recognizer.threshold else (0, 0, 255)
                cv2.putText(display_frame, f"{i+1}. {name} (ID: {student_id})", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                y_pos += 25
                cv2.putText(display_frame, f"   Raw: {raw_sim:.4f}, Norm: {norm_sim:.4f}", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_pos += 30
            
            # Show threshold
            cv2.putText(display_frame, f"Threshold: {face_recognizer.threshold:.4f}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        else:
            cv2.putText(display_frame, "No face detected", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Face Recognition Debug", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save debug image
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, f"debug_{int(time.time())}.jpg")
            cv2.imwrite(debug_path, display_frame)
            print(f"Saved debug image to {debug_path}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Force close any remaining windows
    for i in range(5):
        cv2.waitKey(1)

if __name__ == "__main__":
    debug_face_recognition()