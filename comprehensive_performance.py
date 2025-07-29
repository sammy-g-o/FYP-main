import os
import cv2
import json
import numpy as np
from datetime import datetime
from sklearn.metrics import confusion_matrix, roc_curve, auc
from face_recognition_module import FaceRecognizer
from database_manager import DatabaseManager

class ComprehensivePerformanceTester:
    def __init__(self, db_manager, face_recognizer):
        self.db_manager = db_manager
        self.face_recognizer = face_recognizer
        self.results = {}

    def run_full_test(self, test_dataset_path):
        print("Starting comprehensive performance test...")
        
        # 1. Ground Truth Data Preparation
        genuine_attempts, impostor_attempts = self._prepare_test_data(test_dataset_path)
        
        if not genuine_attempts and not impostor_attempts:
            print("No test data found. Aborting.")
            return

        # 2. Run Evaluations
        y_true, y_pred, y_scores = self._evaluate_attempts(genuine_attempts, impostor_attempts)

        # 3. Calculate Metrics
        self._calculate_all_metrics(y_true, y_pred, y_scores)

        # 4. Save Results
        self.save_results()
        
        print("Comprehensive performance test finished.")

    def _prepare_test_data(self, test_dataset_path):
        """
        Prepares test data from a structured directory.
        The structure should be:
        - test_dataset_path/
          - student_id_1/
            - genuine_1.jpg
            - genuine_2.jpg
          - student_id_2/
            - genuine_1.jpg
          - impostors/
            - impostor_1.jpg
            - impostor_2.jpg
        """
        print(f"Preparing test data from: {test_dataset_path}")
        genuine_attempts = []
        impostor_attempts = []
        
        registered_students = {student[0] for student in self.db_manager.get_all_students()}
        
        for student_id in os.listdir(test_dataset_path):
            student_path = os.path.join(test_dataset_path, student_id)
            if not os.path.isdir(student_path):
                continue

            if student_id == "impostors":
                for image_name in os.listdir(student_path):
                    image_path = os.path.join(student_path, image_name)
                    # Impostor attempts are tested against all registered students
                    for reg_student_id in registered_students:
                        impostor_attempts.append({
                            "image_path": image_path,
                            "expected_student_id": None,
                            "claimed_student_id": reg_student_id 
                        })
            elif student_id in registered_students:
                for image_name in os.listdir(student_path):
                    image_path = os.path.join(student_path, image_name)
                    genuine_attempts.append({
                        "image_path": image_path,
                        "expected_student_id": student_id
                    })
        
        print(f"Found {len(genuine_attempts)} genuine attempts and {len(impostor_attempts)} impostor attempts.")
        return genuine_attempts, impostor_attempts

    def _evaluate_attempts(self, genuine_attempts, impostor_attempts):
        y_true = []
        y_pred = []
        y_scores = []

        registered_embeddings = self.db_manager.get_all_embeddings()

        # Evaluate genuine attempts
        for attempt in genuine_attempts:
            image = cv2.imread(attempt["image_path"])
            if image is None:
                continue
            
            match, score, _ = self.face_recognizer.recognize_face(image, registered_embeddings)
            
            is_correct = (match is not None and match[0] == attempt["expected_student_id"])
            
            y_true.append(1) # Genuine
            y_pred.append(1 if is_correct else 0)
            y_scores.append(score)

        # Evaluate impostor attempts
        for attempt in impostor_attempts:
            image = cv2.imread(attempt["image_path"])
            if image is None:
                continue

            match, score, _ = self.face_recognizer.recognize_face(image, registered_embeddings)

            # An impostor attempt is correctly rejected if no match is found,
            # or if a match is found but it's not for the claimed student.
            # For simplicity, we consider any match an acceptance.
            is_accepted = (match is not None)

            y_true.append(0) # Impostor
            y_pred.append(1 if is_accepted else 0)
            y_scores.append(score)
            
        return np.array(y_true), np.array(y_pred), np.array(y_scores)

    def _calculate_all_metrics(self, y_true, y_pred, y_scores):
        # Confusion Matrix based metrics
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0,1]).ravel()
        
        self.results['confusion_matrix'] = {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)}

        # Basic Classification Metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0 # Also TPR
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0 # Also TNR

        self.results['classification_metrics'] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall_sensitivity_tpr': recall,
            'f1_score': f1_score,
            'specificity_tnr': specificity
        }

        # Error Rates for Biometrics
        far = fp / (fp + tn) if (fp + tn) > 0 else 0 # False Acceptance Rate (FPR)
        frr = fn / (fn + tp) if (fn + tp) > 0 else 0 # False Rejection Rate (FNR)
        hter = (far + frr) / 2 # Half Total Error Rate

        self.results['biometric_error_rates'] = {
            'false_acceptance_rate_far': far,
            'false_rejection_rate_frr': frr,
            'half_total_error_rate_hter': hter
        }

        # ROC and AUC
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        roc_auc = auc(fpr, tpr)

        self.results['roc_analysis'] = {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'thresholds': thresholds.tolist(),
            'auc': roc_auc
        }

        # Equal Error Rate (EER)
        try:
            fnr = 1 - tpr
            eer_index = np.nanargmin(np.abs(fnr - fpr))
            eer = (fpr[eer_index] + fnr[eer_index]) / 2
            eer_threshold = thresholds[eer_index]
        except ValueError as e:
            print(f"Warning: Could not calculate EER. This is likely due to insufficient test data or lack of variance in scores. Error: {e}")
            eer = None
            eer_threshold = None

        self.results['biometric_error_rates']['equal_error_rate_eer'] = eer
        self.results['biometric_error_rates']['eer_threshold'] = float(eer_threshold) if eer_threshold is not None else None

    def save_results(self):
        """Save results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_performance_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        
        print(f"Comprehensive performance results saved to {filename}")

def main():
    # This assumes you have a 'test_data' directory with the structure described above.
    # You will need to create this directory and populate it with images.
    test_dataset_path = "test_data" 
    if not os.path.exists(test_dataset_path):
        print(f"Test data directory not found at '{test_dataset_path}'.")
        print("Please create it and populate it with test images.")
        # Create a placeholder structure
        os.makedirs(os.path.join(test_dataset_path, "student1"), exist_ok=True)
        os.makedirs(os.path.join(test_dataset_path, "impostors"), exist_ok=True)
        print("Created placeholder directories: 'test_data/student1' and 'test_data/impostors'")
        return

    db_manager = DatabaseManager()
    # Explicitly initialize with the correct model to ensure 128-dim embeddings
    face_recognizer = FaceRecognizer(model_name="Facenet")
    
    tester = ComprehensivePerformanceTester(db_manager, face_recognizer)
    tester.run_full_test(test_dataset_path)

if __name__ == "__main__":
    main()
