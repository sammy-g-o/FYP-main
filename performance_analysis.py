#!/usr/bin/env python3
"""
Performance Analysis Script for Exam Proctoring System
This script analyzes system performance metrics for Chapter 4 documentation
"""

import time
import cv2
import numpy as np
import sqlite3
import os
import json
from datetime import datetime
# import matplotlib.pyplot as plt  # Commented out to avoid dependency issues
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer
from liveness_detection import LivenessDetector

class PerformanceAnalyzer:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.face_recognizer = FaceRecognizer()
        self.liveness_detector = LivenessDetector()
        self.results = {
            'face_recognition': {},
            'liveness_detection': {},
            'database_operations': {},
            'overall_system': {}
        }
    
    def analyze_face_recognition_performance(self, test_images_path="./images"):
        """Analyze face recognition performance metrics"""
        print("Analyzing Face Recognition Performance...")
        
        if not os.path.exists(test_images_path):
            print(f"Test images path {test_images_path} not found")
            return
        
        processing_times = []
        detection_success_rate = []
        recognition_accuracy = []
        
        image_files = [f for f in os.listdir(test_images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for image_file in image_files[:10]:  # Test with first 10 images
            image_path = os.path.join(test_images_path, image_file)
            image = cv2.imread(image_path)
            
            if image is None:
                continue
            
            # Measure face detection time
            start_time = time.time()
            embedding = self.face_recognizer.get_face_embedding(image)
            detection_time = time.time() - start_time
            
            processing_times.append(detection_time)
            detection_success_rate.append(1 if embedding is not None else 0)
            
            # Test recognition if embedding was extracted
            if embedding is not None:
                start_time = time.time()
                registered_embeddings = self.db_manager.get_all_embeddings()
                match, confidence, message = self.face_recognizer.recognize_face(image, registered_embeddings)
                recognition_time = time.time() - start_time
                
                recognition_accuracy.append(confidence if match else 0)
        
        # Calculate metrics
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        detection_rate = np.mean(detection_success_rate) if detection_success_rate else 0
        avg_recognition_accuracy = np.mean(recognition_accuracy) if recognition_accuracy else 0
        
        self.results['face_recognition'] = {
            'average_processing_time': avg_processing_time,
            'detection_success_rate': detection_rate,
            'average_recognition_accuracy': avg_recognition_accuracy,
            'total_images_tested': len(image_files),
            'processing_times': processing_times
        }
        
        print(f"Face Recognition Analysis Complete:")
        print(f"  Average Processing Time: {avg_processing_time:.4f} seconds")
        print(f"  Detection Success Rate: {detection_rate:.2%}")
        print(f"  Average Recognition Accuracy: {avg_recognition_accuracy:.4f}")
    
    def analyze_liveness_detection_performance(self, test_images_path="./images"):
        """Analyze liveness detection performance"""
        print("Analyzing Liveness Detection Performance...")
        
        if not os.path.exists(test_images_path):
            print(f"Test images path {test_images_path} not found")
            return
        
        liveness_times = []
        liveness_scores = []
        detection_results = []
        
        image_files = [f for f in os.listdir(test_images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for image_file in image_files[:10]:  # Test with first 10 images
            image_path = os.path.join(test_images_path, image_file)
            image = cv2.imread(image_path)
            
            if image is None:
                continue
            
            # Measure liveness detection time
            start_time = time.time()
            is_live, score, message = self.liveness_detector.check_liveness(image)
            liveness_time = time.time() - start_time
            
            liveness_times.append(liveness_time)
            liveness_scores.append(score)
            detection_results.append(1 if is_live else 0)
        
        # Calculate metrics
        avg_liveness_time = np.mean(liveness_times) if liveness_times else 0
        avg_liveness_score = np.mean(liveness_scores) if liveness_scores else 0
        liveness_detection_rate = np.mean(detection_results) if detection_results else 0
        
        self.results['liveness_detection'] = {
            'average_processing_time': avg_liveness_time,
            'average_liveness_score': avg_liveness_score,
            'liveness_detection_rate': liveness_detection_rate,
            'processing_times': liveness_times,
            'liveness_scores': liveness_scores
        }
        
        print(f"Liveness Detection Analysis Complete:")
        print(f"  Average Processing Time: {avg_liveness_time:.4f} seconds")
        print(f"  Average Liveness Score: {avg_liveness_score:.4f}")
        print(f"  Liveness Detection Rate: {liveness_detection_rate:.2%}")
    
    def analyze_database_performance(self):
        """Analyze database operation performance"""
        print("Analyzing Database Performance...")
        
        # Test database operations
        operations = {
            'student_lookup': [],
            'embedding_retrieval': [],
            'authentication_logging': []
        }
        
        # Test student lookup times
        for _ in range(100):
            start_time = time.time()
            students = self.db_manager.get_all_students()
            lookup_time = time.time() - start_time
            operations['student_lookup'].append(lookup_time)
        
        # Test embedding retrieval times
        for _ in range(100):
            start_time = time.time()
            embeddings = self.db_manager.get_all_embeddings()
            retrieval_time = time.time() - start_time
            operations['embedding_retrieval'].append(retrieval_time)
        
        # Test authentication logging times
        for _ in range(100):
            start_time = time.time()
            self.db_manager.log_authentication("TEST_ID", "TEST", 0.8, 0.9, "TEST_SESSION")
            log_time = time.time() - start_time
            operations['authentication_logging'].append(log_time)
        
        # Calculate averages
        db_metrics = {}
        for operation, times in operations.items():
            db_metrics[f'avg_{operation}_time'] = np.mean(times)
            db_metrics[f'max_{operation}_time'] = np.max(times)
            db_metrics[f'min_{operation}_time'] = np.min(times)
        
        self.results['database_operations'] = db_metrics
        
        print(f"Database Performance Analysis Complete:")
        for operation, times in operations.items():
            print(f"  {operation.replace('_', ' ').title()}: {np.mean(times):.6f}s avg")
    
    def analyze_system_resources(self):
        """Analyze system resource usage"""
        print("Analyzing System Resource Usage...")
        
        try:
            import psutil
            
            # Get current process
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=1)
            
            self.results['overall_system'] = {
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': memory_percent,
                'cpu_percent': cpu_percent,
                'num_threads': process.num_threads()
            }
            
            print(f"System Resource Analysis Complete:")
            print(f"  Memory Usage: {memory_info.rss / 1024 / 1024:.2f} MB ({memory_percent:.1f}%)")
            print(f"  CPU Usage: {cpu_percent:.1f}%")
            print(f"  Number of Threads: {process.num_threads()}")
            
        except ImportError:
            print("psutil not available for system resource analysis")
            self.results['overall_system'] = {
                'note': 'psutil not available for detailed system analysis'
            }
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE PERFORMANCE ANALYSIS REPORT")
        print("="*60)
        
        # Run all analyses
        self.analyze_face_recognition_performance()
        print()
        self.analyze_liveness_detection_performance()
        print()
        self.analyze_database_performance()
        print()
        self.analyze_system_resources()
        
        # Save results to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"performance_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {report_filename}")
        
        # Generate summary
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report for Chapter 4"""
        print("\n" + "="*60)
        print("SUMMARY FOR CHAPTER 4")
        print("="*60)
        
        fr_results = self.results.get('face_recognition', {})
        ld_results = self.results.get('liveness_detection', {})
        db_results = self.results.get('database_operations', {})
        sys_results = self.results.get('overall_system', {})
        
        print("4.8.1 Performance Metrics:")
        print(f"  • Face Recognition Processing Time: {fr_results.get('average_processing_time', 0):.4f} seconds")
        print(f"  • Face Detection Success Rate: {fr_results.get('detection_success_rate', 0):.2%}")
        print(f"  • Liveness Detection Processing Time: {ld_results.get('average_processing_time', 0):.4f} seconds")
        print(f"  • Database Query Response Time: {db_results.get('avg_embedding_retrieval_time', 0):.6f} seconds")
        
        print("\n4.8.2 System Resource Usage:")
        if 'memory_usage_mb' in sys_results:
            print(f"  • Memory Usage: {sys_results['memory_usage_mb']:.2f} MB")
            print(f"  • CPU Usage: {sys_results['cpu_percent']:.1f}%")
        
        print("\n4.8.3 Accuracy Metrics:")
        print(f"  • Average Recognition Confidence: {fr_results.get('average_recognition_accuracy', 0):.4f}")
        print(f"  • Average Liveness Score: {ld_results.get('average_liveness_score', 0):.4f}")
        
        print("\n4.8.4 Real-time Performance:")
        total_processing_time = (fr_results.get('average_processing_time', 0) + 
                               ld_results.get('average_processing_time', 0))
        fps_estimate = 1 / total_processing_time if total_processing_time > 0 else 0
        print(f"  • Estimated Processing FPS: {fps_estimate:.2f}")
        print(f"  • Real-time Capability: {'Yes' if fps_estimate >= 10 else 'Limited'}")

def main():
    """Main function to run performance analysis"""
    analyzer = PerformanceAnalyzer()
    analyzer.generate_performance_report()

if __name__ == "__main__":
    main()
