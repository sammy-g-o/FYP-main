import cv2
import numpy as np
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from deepface import DeepFace
# Remove the problematic import
# from deepface.commons.functions import find_input_shape
import dlib
import time

class FaceRecognizer:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # DeepFace configuration - Use Facenet consistently throughout the project
        self.model_name = "Facenet"  # This model produces 128-dimensional embeddings
        self.detector_backend = "opencv"
        self.distance_metric = "cosine"
        
        # Set embedding size based on model
        self.embedding_size = 128  # Facenet produces 128-dimensional embeddings
        
        # Set threshold based on model
        self.threshold = 0.5  # Adjusted for better matching
        
        # Set input shape based on model
        self.input_shape = (160, 160)  # Facenet uses 160x160 input
        
        print(f"Using model: {self.model_name} with embedding size: {self.embedding_size}")
        print(f"Recognition threshold: {self.threshold}")
        
        # Initialize face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_detector = cv2.CascadeClassifier(cascade_path)
        
        # Create a temporary directory for DeepFace if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        print("Loading DeepFace model (this may take a moment on first run)...")
        # Just do a dummy call to ensure models are downloaded
        try:
            _ = DeepFace.represent(
                img_path=np.zeros((100, 100, 3), dtype=np.uint8),
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend=self.detector_backend
            )
        except:
            # Ignore errors from the dummy call
            pass
        
        print(f"DeepFace model '{self.model_name}' loaded successfully")
    
    def preprocess_face(self, image, face_location=None):
        """Preprocess face for the model"""
        try:
            # Debug: Print image shape
            print(f"DEBUG: Image shape: {image.shape}")
            
            # If face_location is provided, use it
            if face_location is not None:
                x, y, w, h = face_location
                face_region = image[y:y+h, x:x+w]
                
                # Resize to model's expected input size
                face_img = cv2.resize(face_region, (self.input_shape[1], self.input_shape[0]))
                print(f"DEBUG: Using provided face location: x={x}, y={y}, w={w}, h={h}")
                return face_img
            
            # Otherwise detect face
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            print(f"DEBUG: Detected {len(faces)} faces")
            
            if len(faces) == 0:
                # Try with more lenient parameters
                faces = self.face_detector.detectMultiScale(
                    gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20)
                )
                print(f"DEBUG: Retry with lenient params: Detected {len(faces)} faces")
                
                if len(faces) == 0:
                    # Save the problematic image for debugging
                    debug_dir = "debug_images"
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_path = os.path.join(debug_dir, f"no_face_detected_{int(time.time())}.jpg")
                    cv2.imwrite(debug_path, image)
                    print(f"DEBUG: Saved problematic image to {debug_path}")
                    return None
            
            # Get the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            print(f"DEBUG: Selected face: x={x}, y={y}, w={w}, h={h}")
            
            # Extract face region
            face_region = image[y:y+h, x:x+w]
            
            # Resize to model's expected input size
            face_img = cv2.resize(face_region, (self.input_shape[1], self.input_shape[0]))
            
            # Save the detected face for debugging
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, f"detected_face_{int(time.time())}.jpg")
            cv2.imwrite(debug_path, face_img)
            print(f"DEBUG: Saved detected face to {debug_path}")
            
            return face_img
            
        except Exception as e:
            print(f"Error in face preprocessing: {str(e)}")
            return None
    
    def get_face_embedding(self, image, face_location=None):
        """Extract face embedding from image"""
        try:
            # Preprocess face
            face_img = self.preprocess_face(image, face_location)
            if face_img is None:
                return None
            
            # Get embedding using DeepFace - updated for newer versions
            embedding = DeepFace.represent(
                img_path=face_img,
                model_name=self.model_name,
                enforce_detection=False,  # We already detected the face
                detector_backend=self.detector_backend,
                align=True
            )
            
            # Handle different return formats in different DeepFace versions
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], dict) and "embedding" in embedding[0]:
                    # Newer DeepFace versions return a list of dicts
                    return np.array(embedding[0]["embedding"])
                else:
                    # Some versions return a list directly
                    return np.array(embedding[0])
            elif isinstance(embedding, dict) and "embedding" in embedding:
                # Some versions return a dict
                return np.array(embedding["embedding"])
            else:
                # Fall back to original behavior
                return np.array(embedding)
        
        except Exception as e:
            print(f"Error in face embedding extraction: {str(e)}")
            return None
    
    def compare_embeddings(self, embedding1, embedding2):
        """Compare two face embeddings"""
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        
        # Convert to a 0-1 range (cosine similarity can be -1 to 1)
        # This maps -1 to 0 and 1 to 1
        normalized_similarity = (similarity + 1) / 2
        
        print(f"DEBUG: Raw similarity: {similarity:.4f}, Normalized: {normalized_similarity:.4f}")
        
        return normalized_similarity
    
    def recognize_face(self, image, registered_embeddings):
        """Recognize face from registered embeddings"""
        embedding = self.get_face_embedding(image)
        if embedding is None:
            print("DEBUG: No face detected in the image")
            return None, 0.0, "No face detected"
        
        if len(registered_embeddings) == 0:
            print("DEBUG: No registered embeddings to compare against")
            return None, 0.0, "No registered embeddings"
        
        best_match = None
        best_score = 0.0
        
        print(f"DEBUG: Comparing against {len(registered_embeddings)} registered faces")
        print(f"DEBUG: Current embedding shape: {embedding.shape}")
        
        for student_id, name, reg_embedding in registered_embeddings:
            # Check for dimension mismatch
            if embedding.shape != reg_embedding.shape:
                print(f"DEBUG: Dimension mismatch - Current: {embedding.shape}, Registered: {reg_embedding.shape}")
                continue
            
            similarity = self.compare_embeddings(embedding, reg_embedding)
            print(f"DEBUG: Similarity with {name} (ID: {student_id}): {similarity:.4f}")
            if similarity > best_score:
                best_score = similarity
                best_match = (student_id, name)
        
        print(f"DEBUG: Best match: {best_match}, Score: {best_score:.4f}, Threshold: {self.threshold}")
        
        if best_score >= self.threshold:
            return best_match, best_score, "Match found"
        else:
            return None, best_score, "No match found"
    
    def verify_face_direct(self, image1, image2):
        """Direct verification between two face images using DeepFace"""
        try:
            result = DeepFace.verify(
                img1_path=image1,
                img2_path=image2,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric
            )
            
            return result["verified"], result["distance"], "Verification complete"
            
        except Exception as e:
            print(f"Error in face verification: {str(e)}")
            return False, 0.0, f"Error: {str(e)}"























