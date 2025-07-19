import cv2
import numpy as np
import os
import argparse
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer

class StudentRegistrationSystem:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.face_recognizer = FaceRecognizer()
    
    def register_single_image(self, student_id, name, image_path):
        """Register a student with a single image"""
        # Load and check image
        img = cv2.imread(image_path)
        if img is None:
            return False, f"Could not load image from {image_path}"
        
        # Extract face embedding
        embedding = self.face_recognizer.get_face_embedding(img)
        if embedding is None:
            return False, "No face detected in the image"
        
        # Register in database
        return self.db_manager.register_student(student_id, name, embedding)
    
    def register_multiple_images(self, student_id, name, image_paths):
        """Register a student with multiple face images"""
        if not image_paths:
            return False, "No images provided"
        
        success_count = 0
        failed_paths = []
        
        for i, image_path in enumerate(image_paths):
            # Load and check image
            img = cv2.imread(image_path)
            if img is None:
                failed_paths.append(image_path)
                continue
            
            # Extract face embedding
            embedding = self.face_recognizer.get_face_embedding(img)
            if embedding is None:
                failed_paths.append(image_path)
                continue
            
            # Register in database with description
            description = f"Image {i+1} - {os.path.basename(image_path)}"
            success, _ = self.db_manager.register_student(student_id, name, embedding, description)
            
            if success:
                success_count += 1
            else:
                failed_paths.append(image_path)
        
        if success_count == 0:
            return False, "Failed to register any images"
        elif success_count == len(image_paths):
            return True, f"Successfully registered all {success_count} images for student {name} (ID: {student_id})"
        else:
            return True, f"Registered {success_count}/{len(image_paths)} images for student {name} (ID: {student_id}). Failed paths: {failed_paths}"
    
    def register_from_webcam(self, student_id, name, num_images=5):
        """Register a student by capturing images from webcam"""
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Error: Could not open camera."
        
        images_captured = 0
        embeddings_registered = 0
        
        print(f"Starting webcam registration for {name} (ID: {student_id})")
        print("Press SPACE to capture an image, ESC to cancel")
        
        while images_captured < num_images:
            ret, frame = cap.read()
            if not ret:
                return False, "Error: Failed to capture frame."
                break
            
            # Display instructions
            display_frame = frame.copy()
            cv2.putText(display_frame, f"Student: {name} (ID: {student_id})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Captured: {images_captured}/{num_images}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, "Press SPACE to capture, ESC to cancel", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow("Student Registration", display_frame)
            
            key = cv2.waitKeyEx(1) & 0xFF
            if key == 27:  # ESC key
                break
            elif key == 32:  # SPACE key
                images_captured += 1
                
                # Extract face embedding
                embedding = self.face_recognizer.get_face_embedding(frame)
                if embedding is None:
                    cv2.putText(display_frame, "No face detected! Try again.", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow("Student Registration", display_frame)
                    cv2.waitKey(1500)
                    images_captured -= 1
                    continue
                
                # Register in database
                description = f"Webcam image {images_captured}"
                success, message = self.db_manager.register_student(student_id, name, embedding, description)
                
                if success:
                    embeddings_registered += 1
                    cv2.putText(display_frame, f"Image {images_captured} captured successfully!", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame, f"Failed to register: {message}", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow("Student Registration", display_frame)
                cv2.waitKey(1500)  # Show result for 1.5 seconds
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Force close any remaining windows
        for i in range(5):  # Try multiple times
            cv2.waitKey(1)
        
        if embeddings_registered == 0:
            return False, "Failed to register any images"
        else:
            return True, f"Successfully registered {embeddings_registered}/{num_images} images for {name} (ID: {student_id})"
    
    def list_registered_students(self):
        """List all registered students"""
        try:
            conn = self.db_manager.connect()
            if conn is None:
                print("Error: Could not connect to the database.")
                return
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.student_id, s.name, COUNT(e.id) as embedding_count
                FROM students s
                LEFT JOIN face_embeddings e ON s.student_id = e.student_id
                GROUP BY s.student_id, s.name
                ORDER BY s.name
            """)
            
            students = cursor.fetchall()
            conn.close()
            
            if not students:
                print("No students registered in the system.")
                return
            
            print("\nRegistered Students:")
            print("=" * 60)
            print(f"{'ID':<15} {'Name':<30} {'Embeddings':<10}")
            print("-" * 60)
            
            for student_id, name, embedding_count in students:
                print(f"{student_id:<15} {name:<30} {embedding_count:<10}")
            
            print("=" * 60)
        
        except Exception as e:
            print(f"Error listing students: {str(e)}")

    def delete_student(self, student_id, force=False):
        """Delete a student and all their face embeddings"""
        if not force:
            # Get student name for confirmation
            conn = self.db_manager.connect()
            if conn is None:
                return False, "Error: Could not connect to the database."
                
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False, f"Student with ID {student_id} not found."
                
            student_name = result[0]
            
            # Ask for confirmation
            confirm = input(f"Are you sure you want to delete student {student_name} (ID: {student_id})? This will delete all face embeddings. [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                return False, "Deletion cancelled."
        
        # Proceed with deletion
        return self.db_manager.delete_student(student_id)

def main():
    parser = argparse.ArgumentParser(description='Student Registration System')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Register with single image
    single_parser = subparsers.add_parser('single', help='Register with a single image')
    single_parser.add_argument('student_id', help='Student ID')
    single_parser.add_argument('name', help='Student name')
    single_parser.add_argument('image_path', help='Path to the image file')
    
    # Register with multiple images
    multi_parser = subparsers.add_parser('multi', help='Register with multiple images')
    multi_parser.add_argument('student_id', help='Student ID')
    multi_parser.add_argument('name', help='Student name')
    multi_parser.add_argument('image_paths', nargs='+', help='Paths to the image files')
    
    # Register with webcam
    webcam_parser = subparsers.add_parser('webcam', help='Register using webcam')
    webcam_parser.add_argument('student_id', help='Student ID')
    webcam_parser.add_argument('name', help='Student name')
    webcam_parser.add_argument('--num_images', type=int, default=5, help='Number of images to capture')
    
    # List registered students
    subparsers.add_parser('list', help='List all registered students')
    
    # Delete a student
    delete_parser = subparsers.add_parser('delete', help='Delete a student and all their face embeddings')
    delete_parser.add_argument('student_id', help='Student ID to delete')
    delete_parser.add_argument('--force', action='store_true', help='Delete without confirmation')
    
    args = parser.parse_args()
    
    registration_system = StudentRegistrationSystem()
    
    if args.command == 'single':
        success, message = registration_system.register_single_image(
            args.student_id, args.name, args.image_path
        )
        print(message)
    
    elif args.command == 'multi':
        success, message = registration_system.register_multiple_images(
            args.student_id, args.name, args.image_paths
        )
        print(message)
    
    elif args.command == 'webcam':
        success, message = registration_system.register_from_webcam(
            args.student_id, args.name, args.num_images
        )
        print(message)
    
    elif args.command == 'list':
        registration_system.list_registered_students()
    
    elif args.command == 'delete':
        # Add delete functionality
        if not args.force:
            # Get student name for confirmation
            conn = registration_system.db_manager.connect()
            if conn is None:
                print("Error: Could not connect to the database.")
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM students WHERE student_id = ?", (args.student_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                print(f"Student with ID {args.student_id} not found.")
                return
                
            student_name = result[0]
            
            # Ask for confirmation
            confirm = input(f"Are you sure you want to delete student {student_name} (ID: {args.student_id})? This will delete all face embeddings. [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                print("Deletion cancelled.")
                return
        
        # Proceed with deletion
        success, message = registration_system.db_manager.delete_student(args.student_id)
        print(message)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()



