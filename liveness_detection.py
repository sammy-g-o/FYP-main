import cv2
import dlib
import numpy as np
import time

class LivenessDetector:
    def __init__(self):
        # Initialize dlib's face detector and facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("./model/shape_predictor_68_face_landmarks.dat")
        
        # Eye aspect ratio threshold for blink detection
        self.EAR_THRESHOLD = 0.2
        
        # LBP parameters for texture analysis
        self.radius = 1
        self.n_points = 8 * self.radius
        
        # Improved texture analysis parameters
        self.lbp_grid_size = (8, 8)  # Divide face into 8x8 grid for LBP
        self.spoof_threshold = 0.65  # Threshold for spoof detection
        
        # Blink detection parameters
        self.blink_consecutive_frames = 2
        self.blink_counter = 0
        self.last_blink_time = 0
        self.min_blink_interval = 0.5  # Minimum time between blinks (seconds)
    
    def _calculate_ear(self, eye_points):
        """Calculate Eye Aspect Ratio (EAR)"""
        # Compute the euclidean distances between the vertical eye landmarks
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def _get_lbp_histogram(self, image):
        """Get LBP histogram for texture analysis"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Resize for consistency
        gray = cv2.resize(gray, (128, 128))
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Initialize LBP histogram
        lbp_hist = np.zeros(256, dtype=np.float32)
        
        # Compute LBP
        rows, cols = gray.shape
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                center = gray[i, j]
                code = 0
                
                # Compare with 8 neighbors
                code |= (gray[i-1, j-1] >= center) << 7
                code |= (gray[i-1, j] >= center) << 6
                code |= (gray[i-1, j+1] >= center) << 5
                code |= (gray[i, j+1] >= center) << 4
                code |= (gray[i+1, j+1] >= center) << 3
                code |= (gray[i+1, j] >= center) << 2
                code |= (gray[i+1, j-1] >= center) << 1
                code |= (gray[i, j-1] >= center) << 0
                
                lbp_hist[code] += 1
        
        # Normalize histogram
        lbp_hist /= (rows * cols)
        return lbp_hist
    
    def _get_grid_lbp_features(self, face_region):
        """Get LBP features from a grid of face regions"""
        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region
        
        # Resize for consistency
        gray = cv2.resize(gray, (128, 128))
        
        # Divide face into grid
        grid_h, grid_w = self.lbp_grid_size
        h, w = gray.shape
        cell_h, cell_w = h // grid_h, w // grid_w
        
        # Initialize feature vector
        features = []
        
        # Compute LBP for each cell
        for i in range(grid_h):
            for j in range(grid_w):
                # Extract cell
                cell = gray[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                
                # Get LBP histogram for cell
                hist = self._get_lbp_histogram(cell)
                
                # Add to features
                features.extend(hist)
        
        return np.array(features)
    
    def detect_blink(self, image, max_attempts=3, timeout=5):
        """Active liveness detection using blink challenge"""
        faces = self.detector(image)
        if len(faces) == 0:
            return False, 0.0, "No face detected"
        
        face = faces[0]
        landmarks = self.predictor(image, face)
        
        # Extract eye landmarks
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
        
        # Calculate EAR for both eyes
        left_ear = self._calculate_ear(left_eye)
        right_ear = self._calculate_ear(right_eye)
        
        # Average the EAR of both eyes
        ear = (left_ear + right_ear) / 2.0
        
        # Check if eyes are closed (blink detected)
        if ear < self.EAR_THRESHOLD:
            current_time = time.time()
            
            # Check if enough time has passed since last blink
            if current_time - self.last_blink_time >= self.min_blink_interval:
                self.blink_counter += 1
                self.last_blink_time = current_time
                
                if self.blink_counter >= self.blink_consecutive_frames:
                    self.blink_counter = 0  # Reset counter
                    return True, 1.0, "Blink detected"
        else:
            # Eyes are open, reset counter if it was incremented but not enough for a full blink
            if 0 < self.blink_counter < self.blink_consecutive_frames:
                self.blink_counter = 0
        
        # Return intermediate result
        return False, ear, "No blink detected yet"
    
    def texture_analysis(self, image):
        """Passive liveness detection using texture analysis"""
        faces = self.detector(image)
        if len(faces) == 0:
            return False, 0.0, "No face detected"
        
        face = faces[0]
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        face_region = image[y:y+h, x:x+w]
        
        # Get grid LBP features
        lbp_features = self._get_grid_lbp_features(face_region)
        
        # Analyze texture patterns
        # In a real implementation, you would use a trained classifier
        # Here we use a simplified heuristic based on feature statistics
        
        # Calculate feature statistics
        feature_mean = np.mean(lbp_features)
        feature_std = np.std(lbp_features)
        feature_entropy = -np.sum(lbp_features * np.log2(lbp_features + 1e-10))
        
        # Real faces tend to have higher entropy and lower standard deviation
        # This is a simplified heuristic and should be replaced with a proper classifier
        liveness_score = (feature_entropy / 10.0) * (1.0 - feature_std)
        
        # Normalize score to 0-1 range
        liveness_score = max(0.0, min(1.0, liveness_score))
        
        if liveness_score > self.spoof_threshold:
            return True, liveness_score, "Texture analysis passed"
        else:
            return False, liveness_score, "Texture analysis failed"
    
    def check_liveness(self, image):
        """Combined liveness detection"""
        # Passive check first (less intrusive)
        passive_result, passive_score, passive_message = self.texture_analysis(image)
        
        # If passive check fails, try active check
        if not passive_result:
            print("Passive check failed. Checking for blink for active verification.")
            active_result, active_score, active_message = self.detect_blink(image)
            
            if active_result:
                # If active check passes, we're good
                final_score = (passive_score + active_score) / 2
                return True, final_score, "Active liveness check passed"
            else:
                # Both checks failed
                final_score = (passive_score + active_score) / 2
                return False, final_score, "Please blink naturally and ensure good lighting"
        
        # Passive check passed
        return True, passive_score, "Passive liveness check passed"

