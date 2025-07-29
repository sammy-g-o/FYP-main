#!/usr/bin/env python3
"""
Enhanced Evaluation Script for Face Recognition System

This script provides comprehensive evaluation capabilities for the exam proctoring
face recognition system, including detailed metrics analysis, visualization,
and comparison with baseline performance.

Based on the metrics structure from comprehensive_performance_20250725_182524.json
"""

import os
import cv2
import json
import numpy as np
from datetime import datetime
from sklearn.metrics import confusion_matrix, roc_curve, auc
from face_recognition_module import FaceRecognizer
from database_manager import DatabaseManager

# Optional imports for enhanced features
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️  Warning: matplotlib/seaborn not available. Plotting features disabled.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Warning: pandas not available. Some analysis features disabled.")

class EnhancedEvaluationSystem:
    def __init__(self, db_manager=None, face_recognizer=None):
        self.db_manager = db_manager or DatabaseManager()
        self.face_recognizer = face_recognizer or FaceRecognizer(model_name="Facenet")
        self.results = {}
        self.detailed_results = []
        
    def run_comprehensive_evaluation(self, test_dataset_path="test_data", save_plots=True):
        """Run complete evaluation suite"""
        print("=" * 60)
        print("ENHANCED FACE RECOGNITION SYSTEM EVALUATION")
        print("=" * 60)
        
        # 1. System Information
        self._log_system_info()
        
        # 2. Data Preparation
        genuine_attempts, impostor_attempts = self._prepare_test_data(test_dataset_path)
        
        if not genuine_attempts and not impostor_attempts:
            print("❌ No test data found. Please check test_data directory structure.")
            return None
            
        # 3. Run Evaluations
        y_true, y_pred, y_scores, detailed_results = self._evaluate_attempts(
            genuine_attempts, impostor_attempts
        )
        
        # 4. Calculate All Metrics
        self._calculate_comprehensive_metrics(y_true, y_pred, y_scores)
        
        # 5. Generate Visualizations
        if save_plots:
            self._generate_visualizations(y_true, y_pred, y_scores)
        
        # 6. Generate Detailed Report
        self._generate_detailed_report(detailed_results)
        
        # 7. Save Results
        self._save_results()
        
        # 8. Print Summary
        self._print_evaluation_summary()
        
        return self.results
    
    def _log_system_info(self):
        """Log system configuration information"""
        print(f"📊 Evaluation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Face Recognition Model: {self.face_recognizer.model_name}")
        print(f"📏 Embedding Size: {self.face_recognizer.embedding_size}")
        print(f"🎯 Recognition Threshold: {self.face_recognizer.threshold}")
        
        # Check registered students
        try:
            students = self.db_manager.get_all_students()
            print(f"👥 Registered Students: {len(students)}")
            for student_id, name in students:
                embeddings = self.db_manager.get_student_embeddings(student_id)
                print(f"   - {student_id} ({name}): {len(embeddings)} embeddings")
        except Exception as e:
            print(f"⚠️  Warning: Could not retrieve student information: {e}")
        
        print("-" * 60)
    
    def _prepare_test_data(self, test_dataset_path):
        """Prepare test data with enhanced logging"""
        print(f"📁 Preparing test data from: {test_dataset_path}")
        
        if not os.path.exists(test_dataset_path):
            print(f"❌ Test dataset path does not exist: {test_dataset_path}")
            return [], []
        
        genuine_attempts = []
        impostor_attempts = []
        
        try:
            registered_students = {student[0] for student in self.db_manager.get_all_students()}
            print(f"🔍 Looking for test data for students: {registered_students}")
            
            for item in os.listdir(test_dataset_path):
                item_path = os.path.join(test_dataset_path, item)
                if not os.path.isdir(item_path):
                    continue
                
                if item == "impostors":
                    impostor_images = [f for f in os.listdir(item_path) 
                                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    print(f"👤 Found {len(impostor_images)} impostor images")
                    
                    for image_name in impostor_images:
                        image_path = os.path.join(item_path, image_name)
                        # Test each impostor against all registered students
                        for reg_student_id in registered_students:
                            impostor_attempts.append({
                                "image_path": image_path,
                                "image_name": image_name,
                                "expected_student_id": None,
                                "claimed_student_id": reg_student_id,
                                "attempt_type": "impostor"
                            })
                
                elif item in registered_students:
                    genuine_images = [f for f in os.listdir(item_path) 
                                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    print(f"✅ Found {len(genuine_images)} genuine images for {item}")
                    
                    for image_name in genuine_images:
                        image_path = os.path.join(item_path, image_name)
                        genuine_attempts.append({
                            "image_path": image_path,
                            "image_name": image_name,
                            "expected_student_id": item,
                            "attempt_type": "genuine"
                        })
                else:
                    print(f"⚠️  Skipping unregistered student directory: {item}")
            
            print(f"📈 Total test cases prepared:")
            print(f"   - Genuine attempts: {len(genuine_attempts)}")
            print(f"   - Impostor attempts: {len(impostor_attempts)}")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Error preparing test data: {e}")
            return [], []
        
        return genuine_attempts, impostor_attempts
    
    def _evaluate_attempts(self, genuine_attempts, impostor_attempts):
        """Evaluate all attempts with detailed logging"""
        print("🔄 Running face recognition evaluations...")
        
        y_true = []
        y_pred = []
        y_scores = []
        detailed_results = []
        
        try:
            registered_embeddings = self.db_manager.get_all_embeddings()
            print(f"📊 Using {len(registered_embeddings)} registered embeddings")
        except Exception as e:
            print(f"❌ Error getting registered embeddings: {e}")
            return np.array([]), np.array([]), np.array([]), []
        
        # Evaluate genuine attempts
        print(f"🔍 Evaluating {len(genuine_attempts)} genuine attempts...")
        for i, attempt in enumerate(genuine_attempts):
            try:
                image = cv2.imread(attempt["image_path"])
                if image is None:
                    print(f"⚠️  Could not load image: {attempt['image_path']}")
                    continue
                
                match, score, confidence = self.face_recognizer.recognize_face(image, registered_embeddings)
                
                is_correct = (match is not None and match[0] == attempt["expected_student_id"])
                
                y_true.append(1)  # Genuine
                y_pred.append(1 if is_correct else 0)
                y_scores.append(score if score is not None else 0.0)
                
                detailed_results.append({
                    "attempt_type": "genuine",
                    "image_path": attempt["image_path"],
                    "image_name": attempt["image_name"],
                    "expected_student_id": attempt["expected_student_id"],
                    "predicted_student_id": match[0] if match else None,
                    "predicted_name": match[1] if match else None,
                    "score": score,
                    "confidence": confidence,
                    "is_correct": is_correct,
                    "ground_truth": 1,
                    "prediction": 1 if is_correct else 0
                })
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(genuine_attempts)} genuine attempts")
                    
            except Exception as e:
                print(f"❌ Error processing genuine attempt {attempt['image_path']}: {e}")
                continue
        
        # Evaluate impostor attempts
        print(f"🔍 Evaluating {len(impostor_attempts)} impostor attempts...")
        for i, attempt in enumerate(impostor_attempts):
            try:
                image = cv2.imread(attempt["image_path"])
                if image is None:
                    continue
                
                match, score, confidence = self.face_recognizer.recognize_face(image, registered_embeddings)
                
                # Impostor is correctly rejected if no match found
                is_accepted = (match is not None)
                
                y_true.append(0)  # Impostor
                y_pred.append(1 if is_accepted else 0)
                y_scores.append(score if score is not None else 0.0)
                
                detailed_results.append({
                    "attempt_type": "impostor",
                    "image_path": attempt["image_path"],
                    "image_name": attempt["image_name"],
                    "expected_student_id": None,
                    "claimed_student_id": attempt["claimed_student_id"],
                    "predicted_student_id": match[0] if match else None,
                    "predicted_name": match[1] if match else None,
                    "score": score,
                    "confidence": confidence,
                    "is_accepted": is_accepted,
                    "ground_truth": 0,
                    "prediction": 1 if is_accepted else 0
                })
                
                if (i + 1) % 20 == 0:
                    print(f"   Processed {i + 1}/{len(impostor_attempts)} impostor attempts")
                    
            except Exception as e:
                print(f"❌ Error processing impostor attempt {attempt['image_path']}: {e}")
                continue
        
        print(f"✅ Evaluation completed: {len(y_true)} total attempts processed")
        print("-" * 60)
        
        return np.array(y_true), np.array(y_pred), np.array(y_scores), detailed_results

    def _calculate_comprehensive_metrics(self, y_true, y_pred, y_scores):
        """Calculate all performance metrics matching the JSON structure"""
        print("📊 Calculating comprehensive performance metrics...")

        if len(y_true) == 0:
            print("❌ No data available for metrics calculation")
            return

        # Confusion Matrix
        try:
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
            self.results['confusion_matrix'] = {
                'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)
            }
        except Exception as e:
            print(f"⚠️  Error calculating confusion matrix: {e}")
            self.results['confusion_matrix'] = {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0}
            return

        # Classification Metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0  # Also TPR/Sensitivity
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # Also TNR

        self.results['classification_metrics'] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall_sensitivity_tpr': recall,
            'f1_score': f1_score,
            'specificity_tnr': specificity
        }

        # Biometric Error Rates
        far = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Acceptance Rate (FPR)
        frr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Rejection Rate (FNR)
        hter = (far + frr) / 2  # Half Total Error Rate

        self.results['biometric_error_rates'] = {
            'false_acceptance_rate_far': far,
            'false_rejection_rate_frr': frr,
            'half_total_error_rate_hter': hter
        }

        # ROC Analysis
        try:
            fpr, tpr, thresholds = roc_curve(y_true, y_scores)
            roc_auc = auc(fpr, tpr)

            self.results['roc_analysis'] = {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'thresholds': [float(t) if not np.isinf(t) else float('inf') for t in thresholds],
                'auc': roc_auc
            }

            # Equal Error Rate (EER)
            fnr = 1 - tpr
            eer_index = np.nanargmin(np.abs(fnr - fpr))
            eer = (fpr[eer_index] + fnr[eer_index]) / 2
            eer_threshold = thresholds[eer_index]

            self.results['biometric_error_rates']['equal_error_rate_eer'] = eer
            self.results['biometric_error_rates']['eer_threshold'] = float(eer_threshold) if not np.isinf(eer_threshold) else float('inf')

        except Exception as e:
            print(f"⚠️  Error calculating ROC metrics: {e}")
            self.results['roc_analysis'] = {'fpr': [], 'tpr': [], 'thresholds': [], 'auc': 0.0}
            self.results['biometric_error_rates']['equal_error_rate_eer'] = None
            self.results['biometric_error_rates']['eer_threshold'] = None

        # Additional Metrics
        self.results['additional_metrics'] = {
            'total_attempts': len(y_true),
            'genuine_attempts': int(np.sum(y_true == 1)),
            'impostor_attempts': int(np.sum(y_true == 0)),
            'correct_predictions': int(np.sum(y_pred == y_true)),
            'incorrect_predictions': int(np.sum(y_pred != y_true))
        }

        print("✅ Metrics calculation completed")

    def _generate_visualizations(self, y_true, y_pred, y_scores):
        """Generate comprehensive visualization plots"""
        if not PLOTTING_AVAILABLE:
            print("⚠️  Skipping visualizations - plotting libraries not available")
            return

        print("📈 Generating performance visualizations...")

        # Create output directory
        os.makedirs("evaluation_plots", exist_ok=True)

        # Set up the plotting style
        plt.style.use('default')
        if 'sns' in globals():
            sns.set_palette("husl")

        # 1. Confusion Matrix Heatmap
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

        if 'sns' in globals():
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Rejected', 'Accepted'],
                       yticklabels=['Impostor', 'Genuine'])
        else:
            # Simple matplotlib heatmap
            im = plt.imshow(cm, interpolation='nearest', cmap='Blues')
            plt.colorbar(im)
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    plt.text(j, i, str(cm[i, j]), ha='center', va='center')
            plt.xticks([0, 1], ['Rejected', 'Accepted'])
            plt.yticks([0, 1], ['Impostor', 'Genuine'])

        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('evaluation_plots/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 2. ROC Curve
        plt.figure(figsize=(8, 6))
        fpr = self.results['roc_analysis']['fpr']
        tpr = self.results['roc_analysis']['tpr']
        auc_score = self.results['roc_analysis']['auc']

        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {auc_score:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (FAR)')
        plt.ylabel('True Positive Rate (1-FRR)')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('evaluation_plots/roc_curve.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 3. Score Distribution
        plt.figure(figsize=(10, 6))
        genuine_scores = y_scores[y_true == 1]
        impostor_scores = y_scores[y_true == 0]

        plt.hist(genuine_scores, bins=20, alpha=0.7, label='Genuine', color='green', density=True)
        plt.hist(impostor_scores, bins=20, alpha=0.7, label='Impostor', color='red', density=True)
        plt.axvline(x=self.face_recognizer.threshold, color='black', linestyle='--',
                   label=f'Threshold ({self.face_recognizer.threshold})')

        if self.results['biometric_error_rates']['eer_threshold']:
            plt.axvline(x=self.results['biometric_error_rates']['eer_threshold'],
                       color='blue', linestyle=':', label='EER Threshold')

        plt.xlabel('Recognition Score')
        plt.ylabel('Density')
        plt.title('Score Distribution for Genuine vs Impostor Attempts')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('evaluation_plots/score_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("✅ Visualizations saved to evaluation_plots/ directory")

    def _generate_detailed_report(self, detailed_results):
        """Generate detailed analysis report"""
        print("📝 Generating detailed analysis report...")

        if not detailed_results:
            print("⚠️  No detailed results available for report generation")
            return

        # Save detailed results to CSV (with or without pandas)
        if PANDAS_AVAILABLE:
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(detailed_results)
            df.to_csv('evaluation_detailed_results.csv', index=False)
        else:
            # Manual CSV writing
            import csv
            with open('evaluation_detailed_results.csv', 'w', newline='') as csvfile:
                if detailed_results:
                    fieldnames = detailed_results[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(detailed_results)

        # Generate summary statistics
        self.results['detailed_analysis'] = {
            'per_student_performance': {},
            'error_analysis': {},
            'score_statistics': {}
        }

        if PANDAS_AVAILABLE:
            # Use pandas for analysis
            genuine_df = df[df['attempt_type'] == 'genuine']
            if not genuine_df.empty:
                for student_id in genuine_df['expected_student_id'].unique():
                    student_data = genuine_df[genuine_df['expected_student_id'] == student_id]
                    correct = student_data['is_correct'].sum()
                    total = len(student_data)

                    self.results['detailed_analysis']['per_student_performance'][student_id] = {
                        'correct_recognitions': int(correct),
                        'total_attempts': int(total),
                        'accuracy': correct / total if total > 0 else 0,
                        'avg_score': float(student_data['score'].mean()) if not student_data['score'].isna().all() else 0,
                        'min_score': float(student_data['score'].min()) if not student_data['score'].isna().all() else 0,
                        'max_score': float(student_data['score'].max()) if not student_data['score'].isna().all() else 0
                    }

            # Score statistics
            if 'score' in df.columns and not df['score'].isna().all():
                self.results['detailed_analysis']['score_statistics'] = {
                    'overall_mean': float(df['score'].mean()),
                    'overall_std': float(df['score'].std()),
                    'genuine_mean': float(genuine_df['score'].mean()) if not genuine_df.empty else 0,
                    'impostor_mean': float(df[df['attempt_type'] == 'impostor']['score'].mean()) if not df[df['attempt_type'] == 'impostor'].empty else 0
                }
        else:
            # Manual analysis without pandas
            genuine_attempts = [r for r in detailed_results if r['attempt_type'] == 'genuine']
            impostor_attempts = [r for r in detailed_results if r['attempt_type'] == 'impostor']

            # Per-student performance
            student_stats = {}
            for attempt in genuine_attempts:
                student_id = attempt['expected_student_id']
                if student_id not in student_stats:
                    student_stats[student_id] = {'correct': 0, 'total': 0, 'scores': []}

                student_stats[student_id]['total'] += 1
                if attempt.get('is_correct', False):
                    student_stats[student_id]['correct'] += 1
                if attempt.get('score') is not None:
                    student_stats[student_id]['scores'].append(attempt['score'])

            for student_id, stats in student_stats.items():
                scores = stats['scores']
                self.results['detailed_analysis']['per_student_performance'][student_id] = {
                    'correct_recognitions': stats['correct'],
                    'total_attempts': stats['total'],
                    'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                    'avg_score': sum(scores) / len(scores) if scores else 0,
                    'min_score': min(scores) if scores else 0,
                    'max_score': max(scores) if scores else 0
                }

            # Overall score statistics
            all_scores = [r.get('score', 0) for r in detailed_results if r.get('score') is not None]
            genuine_scores = [r.get('score', 0) for r in genuine_attempts if r.get('score') is not None]
            impostor_scores = [r.get('score', 0) for r in impostor_attempts if r.get('score') is not None]

            if all_scores:
                mean_score = sum(all_scores) / len(all_scores)
                variance = sum((x - mean_score) ** 2 for x in all_scores) / len(all_scores)
                std_score = variance ** 0.5

                self.results['detailed_analysis']['score_statistics'] = {
                    'overall_mean': mean_score,
                    'overall_std': std_score,
                    'genuine_mean': sum(genuine_scores) / len(genuine_scores) if genuine_scores else 0,
                    'impostor_mean': sum(impostor_scores) / len(impostor_scores) if impostor_scores else 0
                }

        print("✅ Detailed report generated")
        print(f"   - Detailed results saved to: evaluation_detailed_results.csv")
        print(f"   - Analyzed {len(detailed_results)} total attempts")

    def _save_results(self):
        """Save comprehensive results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_evaluation_{timestamp}.json"

        # Add metadata
        self.results['metadata'] = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'model_name': self.face_recognizer.model_name,
            'embedding_size': self.face_recognizer.embedding_size,
            'recognition_threshold': self.face_recognizer.threshold,
            'evaluation_version': '2.0'
        }

        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)

        print(f"💾 Comprehensive results saved to: {filename}")
        return filename

    def _print_evaluation_summary(self):
        """Print a comprehensive evaluation summary"""
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)

        # Basic metrics
        cm = self.results['confusion_matrix']
        metrics = self.results['classification_metrics']
        bio_metrics = self.results['biometric_error_rates']

        print(f"📈 CLASSIFICATION PERFORMANCE:")
        print(f"   Accuracy:     {metrics['accuracy']:.3f} ({metrics['accuracy']*100:.1f}%)")
        print(f"   Precision:    {metrics['precision']:.3f}")
        print(f"   Recall (TPR): {metrics['recall_sensitivity_tpr']:.3f}")
        print(f"   F1-Score:     {metrics['f1_score']:.3f}")
        print(f"   Specificity:  {metrics['specificity_tnr']:.3f}")

        print(f"\n🔒 BIOMETRIC ERROR RATES:")
        print(f"   FAR (False Accept):  {bio_metrics['false_acceptance_rate_far']:.3f} ({bio_metrics['false_acceptance_rate_far']*100:.1f}%)")
        print(f"   FRR (False Reject):  {bio_metrics['false_rejection_rate_frr']:.3f} ({bio_metrics['false_rejection_rate_frr']*100:.1f}%)")
        print(f"   HTER:               {bio_metrics['half_total_error_rate_hter']:.3f} ({bio_metrics['half_total_error_rate_hter']*100:.1f}%)")
        if bio_metrics['equal_error_rate_eer']:
            print(f"   EER:                {bio_metrics['equal_error_rate_eer']:.3f} ({bio_metrics['equal_error_rate_eer']*100:.1f}%)")
            print(f"   EER Threshold:      {bio_metrics['eer_threshold']:.3f}")

        print(f"\n📊 CONFUSION MATRIX:")
        print(f"                    Predicted")
        print(f"                 Reject  Accept")
        print(f"   Actual Impostor  {cm['tn']:4d}    {cm['fp']:4d}")
        print(f"          Genuine   {cm['fn']:4d}    {cm['tp']:4d}")

        print(f"\n🎯 ROC ANALYSIS:")
        print(f"   AUC Score: {self.results['roc_analysis']['auc']:.3f}")

        if 'additional_metrics' in self.results:
            add_metrics = self.results['additional_metrics']
            print(f"\n📋 TEST SUMMARY:")
            print(f"   Total Attempts:     {add_metrics['total_attempts']}")
            print(f"   Genuine Attempts:   {add_metrics['genuine_attempts']}")
            print(f"   Impostor Attempts:  {add_metrics['impostor_attempts']}")
            print(f"   Correct Predictions: {add_metrics['correct_predictions']}")
            print(f"   Wrong Predictions:   {add_metrics['incorrect_predictions']}")

        # Performance interpretation
        print(f"\n🎯 PERFORMANCE INTERPRETATION:")
        if metrics['accuracy'] >= 0.9:
            print("   ✅ Excellent performance (≥90% accuracy)")
        elif metrics['accuracy'] >= 0.8:
            print("   ✅ Good performance (80-89% accuracy)")
        elif metrics['accuracy'] >= 0.7:
            print("   ⚠️  Fair performance (70-79% accuracy)")
        else:
            print("   ❌ Poor performance (<70% accuracy)")

        if bio_metrics['false_acceptance_rate_far'] <= 0.01:
            print("   🔒 Excellent security (FAR ≤ 1%)")
        elif bio_metrics['false_acceptance_rate_far'] <= 0.05:
            print("   🔒 Good security (FAR ≤ 5%)")
        else:
            print("   ⚠️  Security concerns (FAR > 5%)")

        print("\n📁 OUTPUT FILES:")
        print("   - Enhanced evaluation JSON: enhanced_evaluation_*.json")
        print("   - Detailed results CSV: evaluation_detailed_results.csv")
        print("   - Visualization plots: evaluation_plots/")

        print("=" * 60)

    def compare_with_baseline(self, baseline_file):
        """Compare current results with baseline performance"""
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)

            print(f"\n📊 COMPARISON WITH BASELINE ({baseline_file}):")
            print("-" * 50)

            current_acc = self.results['classification_metrics']['accuracy']
            baseline_acc = baseline['classification_metrics']['accuracy']
            acc_diff = current_acc - baseline_acc

            print(f"Accuracy:    {baseline_acc:.3f} → {current_acc:.3f} ({acc_diff:+.3f})")

            current_far = self.results['biometric_error_rates']['false_acceptance_rate_far']
            baseline_far = baseline['biometric_error_rates']['false_acceptance_rate_far']
            far_diff = current_far - baseline_far

            print(f"FAR:         {baseline_far:.3f} → {current_far:.3f} ({far_diff:+.3f})")

            current_frr = self.results['biometric_error_rates']['false_rejection_rate_frr']
            baseline_frr = baseline['biometric_error_rates']['false_rejection_rate_frr']
            frr_diff = current_frr - baseline_frr

            print(f"FRR:         {baseline_frr:.3f} → {current_frr:.3f} ({frr_diff:+.3f})")

            if acc_diff > 0.01:
                print("✅ Accuracy improved!")
            elif acc_diff < -0.01:
                print("❌ Accuracy decreased!")
            else:
                print("➡️  Accuracy similar")

        except Exception as e:
            print(f"⚠️  Could not compare with baseline: {e}")

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Face Recognition System Evaluation')
    parser.add_argument('--test-data', default='test_data',
                       help='Path to test dataset directory (default: test_data)')
    parser.add_argument('--no-plots', action='store_true',
                       help='Skip generating visualization plots')
    parser.add_argument('--baseline', type=str,
                       help='Baseline JSON file for comparison')

    args = parser.parse_args()

    try:
        # Initialize evaluation system
        evaluator = EnhancedEvaluationSystem()

        # Run comprehensive evaluation
        results = evaluator.run_comprehensive_evaluation(
            test_dataset_path=args.test_data,
            save_plots=not args.no_plots
        )

        if results is None:
            print("❌ Evaluation failed. Please check your test data setup.")
            return

        # Compare with baseline if provided
        if args.baseline:
            evaluator.compare_with_baseline(args.baseline)

        print("\n🎉 Evaluation completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
    except Exception as e:
        print(f"❌ Evaluation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
