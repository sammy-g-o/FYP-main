import cv2
import numpy as np
from deepface import DeepFace
import os

def check_deepface_models():
    """Check which DeepFace models are available and their embedding sizes"""
    print("Checking DeepFace models...")
    
    # Create a simple test image
    test_img = np.zeros((160, 160, 3), dtype=np.uint8)
    cv2.circle(test_img, (80, 80), 50, (255, 255, 255), -1)
    
    # Save test image
    os.makedirs("debug_images", exist_ok=True)
    cv2.imwrite("debug_images/test_image.jpg", test_img)
    
    # Test different models
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]
    
    for model_name in models:
        try:
            print(f"Testing model: {model_name}")
            embedding = DeepFace.represent(
                img_path="debug_images/test_image.jpg",
                model_name=model_name,
                enforce_detection=False,
                detector_backend="opencv"
            )
            
            # Handle different return formats
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], dict) and "embedding" in embedding[0]:
                    # Newer DeepFace versions
                    emb = embedding[0]["embedding"]
                else:
                    # Some versions return a list directly
                    emb = embedding[0]
            elif isinstance(embedding, dict) and "embedding" in embedding:
                # Some versions return a dict
                emb = embedding["embedding"]
            else:
                # Fall back to original
                emb = embedding
                
            print(f"  Model: {model_name}, Embedding size: {len(emb)}")
        except Exception as e:
            print(f"  Error with model {model_name}: {str(e)}")
    
    print("Model check complete.")

if __name__ == "__main__":
    check_deepface_models()