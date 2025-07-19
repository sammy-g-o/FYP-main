#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Exam Proctoring System
This script provides unit tests and integration tests for Chapter 4 documentation
"""

import unittest
import cv2
import numpy as np
import os
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock
import sys

# Import system modules
from database_manager import DatabaseManager
from face_recognition_module import FaceRecognizer
from liveness_detection import LivenessDetector
from face_recognition_system import ExamProctorSystem

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_manager = DatabaseManager(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.test_db.name)
    
    def test_database_initialization(self):
        """Test database initialization"""
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('students', tables)
        self.assertIn('face_embeddings', tables)
        self.assertIn('auth_logs', tables)
        
        conn.close()
    
    def test_student_registration(self):
        """Test student registration functionality"""
        # Create dummy embedding
        dummy_embedding = np.random.rand(128).astype(np.float32)
        
        # Test registration
        success, message = self.db_manager.register_student("TEST001", "Test Student", dummy_embedding)
        self.assertTrue(success)
        
        # Test duplicate registration
        success, message = self.db_manager.register_student("TEST001", "Test Student 2", dummy_embedding)
        self.assertTrue(success)  # Should add new embedding for existing student
    
    def test_embedding_retrieval(self):
        """Test embedding retrieval"""
        # Register test student
        dummy_embedding = np.random.rand(128).astype(np.float32)
        self.db_manager.register_student("TEST002", "Test Student 2", dummy_embedding)
        
        # Retrieve embeddings
        embeddings = self.db_manager.get_all_embeddings()
        self.assertGreater(len(embeddings), 0)
        
        # Check embedding format
        student_id, name, embedding = embeddings[0]
        self.assertEqual(student_id, "TEST002")
        self.assertEqual(name, "Test Student 2")
        self.assertEqual(len(embedding), 128)
    
    def test_authentication_logging(self):
        """Test authentication logging"""
        # Log authentication attempt
        success = self.db_manager.log_authentication(
            "TEST003", "SUCCESS", 0.85, 0.92, "SESSION001"
        )
        self.assertTrue(success)
        
        # Verify log entry
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auth_logs WHERE student_id = ?", ("TEST003",))
        log_entry = cursor.fetchone()
        
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry[1], "TEST003")  # student_id
        self.assertEqual(log_entry[3], "SUCCESS")  # auth_result
        
        conn.close()

class TestFaceRecognizer(unittest.TestCase):
    """Test cases for FaceRecognizer class"""
    
    def setUp(self):
        """Set up face recognizer"""
        self.face_recognizer = FaceRecognizer()
    
    def test_face_recognizer_initialization(self):
        """Test face recognizer initialization"""
        self.assertEqual(self.face_recognizer.model_name, "Facenet")
        self.assertEqual(self.face_recognizer.embedding_size, 128)
        self.assertEqual(self.face_recognizer.threshold, 0.5)
    
    def test_face_detection(self):
        """Test face detection functionality"""
        # Create test image with a simple face-like pattern
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(test_image, (100, 100), 80, (255, 255, 255), -1)  # Face
        cv2.circle(test_image, (80, 80), 10, (0, 0, 0), -1)   # Left eye
        cv2.circle(test_image, (120, 80), 10, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(test_image, (100, 120), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        # Test face detection
        faces = self.face_recognizer.detect_faces(test_image)
        # Note: This might not detect the simple pattern, but tests the method
        self.assertIsInstance(faces, list)
    
    def test_embedding_extraction(self):
        """Test face embedding extraction"""
        # Create test image
        test_image = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
        
        # Test embedding extraction (might return None for random image)
        embedding = self.face_recognizer.get_face_embedding(test_image)
        
        # If embedding is extracted, it should be the right size
        if embedding is not None:
            self.assertEqual(len(embedding), 128)

class TestLivenessDetector(unittest.TestCase):
    """Test cases for LivenessDetector class"""
    
    def setUp(self):
        """Set up liveness detector"""
        # Check if model file exists
        model_path = "./model/shape_predictor_68_face_landmarks.dat"
        if not os.path.exists(model_path):
            self.skipTest(f"Model file not found: {model_path}")
        
        self.liveness_detector = LivenessDetector()
    
    def test_liveness_detector_initialization(self):
        """Test liveness detector initialization"""
        self.assertIsNotNone(self.liveness_detector.detector)
        self.assertIsNotNone(self.liveness_detector.predictor)
        self.assertEqual(self.liveness_detector.EAR_THRESHOLD, 0.2)
    
    def test_texture_analysis(self):
        """Test texture analysis for liveness detection"""
        # Create test image
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # Test texture analysis
        is_live, score, message = self.liveness_detector.texture_analysis(test_image)
        
        self.assertIsInstance(is_live, bool)
        self.assertIsInstance(score, (int, float))
        self.assertIsInstance(message, str)
    
    def test_blink_detection(self):
        """Test blink detection functionality"""
        # Create test image
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # Test blink detection
        is_blink, score, message = self.liveness_detector.detect_blink(test_image)
        
        self.assertIsInstance(is_blink, bool)
        self.assertIsInstance(score, (int, float))
        self.assertIsInstance(message, str)

class TestExamProctorSystem(unittest.TestCase):
    """Test cases for ExamProctorSystem class"""
    
    def setUp(self):
        """Set up exam proctor system"""
        # Create temporary database
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        
        # Mock the components to avoid model loading issues
        with patch('face_recognition_system.DatabaseManager') as mock_db, \
             patch('face_recognition_system.FaceRecognizer') as mock_fr, \
             patch('face_recognition_system.LivenessDetector') as mock_ld:
            
            self.system = ExamProctorSystem()
            self.system.db_manager = mock_db.return_value
            self.system.face_recognizer = mock_fr.return_value
            self.system.liveness_detector = mock_ld.return_value
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.system.db_manager)
        self.assertIsNotNone(self.system.face_recognizer)
        self.assertIsNotNone(self.system.liveness_detector)
        self.assertEqual(self.system.monitoring_interval, 30)
    
    def test_exam_session_start(self):
        """Test exam session initialization"""
        session_id = self.system.start_exam_session()
        
        self.assertIsNotNone(session_id)
        self.assertEqual(self.system.current_session_id, session_id)
        self.assertGreater(self.system.last_check_time, 0)
    
    def test_authentication_flow(self):
        """Test authentication flow"""
        # Mock the components
        self.system.liveness_detector.check_liveness.return_value = (True, 0.85, "Live")
        self.system.db_manager.get_all_embeddings.return_value = [("TEST001", "Test User", np.random.rand(128))]
        self.system.face_recognizer.recognize_face.return_value = (("TEST001", "Test User"), 0.92, "Match found")
        self.system.db_manager.log_authentication.return_value = True
        
        # Create test image
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # Test authentication
        success, student_match, liveness_score, confidence_score, message = self.system.authenticate_student(test_image)
        
        self.assertTrue(success)
        self.assertIsNotNone(student_match)
        self.assertEqual(liveness_score, 0.85)
        self.assertEqual(confidence_score, 0.92)

class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
    
    def tearDown(self):
        """Clean up integration test environment"""
        os.unlink(self.test_db.name)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This test would require actual model files and images
        # For now, we'll test the workflow structure
        
        db_manager = DatabaseManager(self.test_db.name)
        
        # Test database setup
        self.assertIsNotNone(db_manager)
        
        # Test student registration
        dummy_embedding = np.random.rand(128).astype(np.float32)
        success, message = db_manager.register_student("INT001", "Integration Test", dummy_embedding)
        self.assertTrue(success)
        
        # Test data retrieval
        embeddings = db_manager.get_all_embeddings()
        self.assertEqual(len(embeddings), 1)

def run_test_suite():
    """Run the complete test suite and generate report"""
    print("="*60)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestDatabaseManager,
        TestFaceRecognizer,
        TestLivenessDetector,
        TestExamProctorSystem,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY FOR CHAPTER 4")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_msg}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  - {test}: {error_msg}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
