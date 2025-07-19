import cv2
from face_recognition_system import ExamProctorSystem

def main():
    # Create the exam proctor system
    system = ExamProctorSystem()
    
    # Start the main system loop
    system.main_loop()

if __name__ == "__main__":
    main()
