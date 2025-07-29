import cv2
import time
from face_recognition_module import FaceRecognizer
from database_manager import DatabaseManager

def debug_recognition():
    """
    A dedicated script to debug the face recognition process.
    This will help diagnose why an unregistered user might be getting a match.
    """
    print("--- Face Recognition Debugger ---")
    
    # 1. Initialize components
    try:
        db_manager = DatabaseManager()
        # Explicitly initialize with the correct model to ensure 128-dim embeddings
        face_recognizer = FaceRecognizer(model_name="Facenet")
        print("Components initialized successfully.")
    except Exception as e:
        print(f"Error initializing components: {e}")
        return

    # 2. Load registered embeddings
    print("\nLoading registered student embeddings...")
    registered_embeddings = db_manager.get_all_embeddings()
    if not registered_embeddings:
        print("No registered students found in the database. Please register a student first.")
        return
    
    print(f"Loaded {len(registered_embeddings)} embeddings for the following students:")
    
    # Create a set to store unique student names and IDs
    unique_students = set()
    for student_id, name, _ in registered_embeddings:
        unique_students.add((student_id, name))
        
    # Print the unique student names and IDs
    for student_id, name in sorted(list(unique_students)):
        print(f"  - {name} (ID: {student_id})")

    # 3. Capture image from webcam
    print("\nPreparing to capture image from webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Webcam opened. Press 'c' to capture an image for testing.")
    print("Please ensure an UNREGISTERED person is in front of the camera.")
    
    capture_frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        display_frame = frame.copy()
        cv2.putText(display_frame, "Press 'c' to capture, 'q' to quit", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Debug Capture", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            print("Debug session cancelled.")
            return
        elif key == ord('c'):
            capture_frame = frame
            print("Image captured.")
            break
            
    cap.release()
    cv2.destroyAllWindows()

    if capture_frame is None:
        print("No image was captured. Aborting.")
        return

    # 4. Run recognition and get detailed results
    print("\n--- Running Recognition ---")
    
    # We need to get inside the recognize_face function's logic
    # to see all scores. Let's replicate parts of it here for debugging.
    
    print("Step 1: Extracting embedding from the captured image...")
    live_embedding = face_recognizer.get_face_embedding(capture_frame)
    
    if live_embedding is None:
        print("Could not extract a face embedding from the captured image. Aborting.")
        return
        
    print("Live embedding extracted successfully.")
    
    print("\nStep 2: Comparing live embedding against all registered embeddings...")
    
    all_scores = []
    for student_id, name, reg_embedding in registered_embeddings:
        if live_embedding.shape != reg_embedding.shape:
            print(f"  - Skipping {name} (ID: {student_id}) due to shape mismatch.")
            continue
            
        similarity = face_recognizer.compare_embeddings(live_embedding, reg_embedding)
        all_scores.append({'student_id': student_id, 'name': name, 'score': similarity})
        print(f"  - Comparison with {name} (ID: {student_id}): Score = {similarity:.4f}")

    # 5. Analyze the results
    print("\n--- Analysis ---")
    if not all_scores:
        print("No comparisons could be made.")
        return
        
    best_match_info = max(all_scores, key=lambda x: x['score'])
    best_score = best_match_info['score']
    best_match_name = best_match_info['name']
    best_match_id = best_match_info['student_id']
    
    threshold = face_recognizer.threshold
    
    print(f"Highest score found: {best_score:.4f} for {best_match_name} (ID: {best_match_id})")
    print(f"Current recognition threshold: {threshold}")
    
    if best_score >= threshold:
        print("\n[!!!] CRITICAL ISSUE: A match was found above the threshold.")
        print("This indicates a FALSE POSITIVE. The system incorrectly identified the unregistered person.")
    else:
        print("\n[OK] As expected, no match was found above the threshold.")
        print("The system correctly rejected the unregistered person.")

if __name__ == "__main__":
    debug_recognition()
