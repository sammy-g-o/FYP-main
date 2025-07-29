#!/usr/bin/env python3
"""
Simple Performance Measurement Script
Analyzes existing data and measures basic operations
"""

import sqlite3
import os
import time
import json
from datetime import datetime

class SimplePerformanceMeasurer:
    def __init__(self):
        self.db_path = "students.db"
        self.results = {}
    
    def analyze_database_performance(self):
        """Measure database operation performance"""
        print("Analyzing Database Performance...")
        
        if not os.path.exists(self.db_path):
            print("Database not found!")
            return
        
        # Test database operations
        student_lookup_times = []
        embedding_retrieval_times = []
        log_query_times = []
        
        # Test student lookup (100 iterations)
        for i in range(100):
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            results = cursor.fetchall()
            conn.close()
            end_time = time.time()
            student_lookup_times.append(end_time - start_time)
        
        # Test embedding retrieval (100 iterations)
        for i in range(100):
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM face_embeddings")
            results = cursor.fetchall()
            conn.close()
            end_time = time.time()
            embedding_retrieval_times.append(end_time - start_time)
        
        # Test auth log queries (100 iterations)
        for i in range(100):
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM auth_logs ORDER BY timestamp DESC LIMIT 10")
            results = cursor.fetchall()
            conn.close()
            end_time = time.time()
            log_query_times.append(end_time - start_time)
        
        # Calculate averages
        avg_student_lookup = sum(student_lookup_times) / len(student_lookup_times)
        avg_embedding_retrieval = sum(embedding_retrieval_times) / len(embedding_retrieval_times)
        avg_log_query = sum(log_query_times) / len(log_query_times)
        
        self.results['database_performance'] = {
            'avg_student_lookup_time': avg_student_lookup,
            'avg_embedding_retrieval_time': avg_embedding_retrieval,
            'avg_log_query_time': avg_log_query,
            'max_student_lookup_time': max(student_lookup_times),
            'min_student_lookup_time': min(student_lookup_times),
            'max_embedding_retrieval_time': max(embedding_retrieval_times),
            'min_embedding_retrieval_time': min(embedding_retrieval_times)
        }
        
        print(f"Database Performance Results:")
        print(f"  Average Student Lookup Time: {avg_student_lookup:.6f} seconds")
        print(f"  Average Embedding Retrieval Time: {avg_embedding_retrieval:.6f} seconds")
        print(f"  Average Log Query Time: {avg_log_query:.6f} seconds")
        print(f"  Max Student Lookup Time: {max(student_lookup_times):.6f} seconds")
        print(f"  Min Student Lookup Time: {min(student_lookup_times):.6f} seconds")
    
    def analyze_existing_data(self):
        """Analyze existing authentication data"""
        print("Analyzing Existing Authentication Data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        embedding_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM auth_logs")
        log_count = cursor.fetchone()[0]
        
        # Analyze authentication results
        cursor.execute("SELECT auth_result, COUNT(*) FROM auth_logs GROUP BY auth_result")
        auth_results = cursor.fetchall()
        
        # Calculate success rate
        success_count = 0
        total_count = 0
        for result, count in auth_results:
            total_count += count
            if result == "SUCCESS":
                success_count += count
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        # Get confidence scores for successful authentications
        cursor.execute("SELECT confidence_score FROM auth_logs WHERE auth_result = 'SUCCESS' AND confidence_score IS NOT NULL")
        confidence_scores = [row[0] for row in cursor.fetchall()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Get liveness scores
        cursor.execute("SELECT liveness_score FROM auth_logs WHERE liveness_score IS NOT NULL")
        liveness_scores = [row[0] for row in cursor.fetchall()]
        avg_liveness_score = sum(liveness_scores) / len(liveness_scores) if liveness_scores else 0
        
        # Analyze by student
        cursor.execute("SELECT student_id, COUNT(*) FROM auth_logs GROUP BY student_id")
        student_attempts = cursor.fetchall()
        
        conn.close()
        
        self.results['authentication_analysis'] = {
            'total_students': student_count,
            'total_embeddings': embedding_count,
            'total_auth_attempts': log_count,
            'success_rate_percent': success_rate,
            'successful_attempts': success_count,
            'failed_attempts': total_count - success_count,
            'average_confidence_score': avg_confidence,
            'average_liveness_score': avg_liveness_score,
            'embeddings_per_student': embedding_count / student_count if student_count > 0 else 0,
            'auth_results_breakdown': dict(auth_results),
            'student_attempts': dict(student_attempts)
        }
        
        print(f"Authentication Data Analysis:")
        print(f"  Total Students: {student_count}")
        print(f"  Total Face Embeddings: {embedding_count}")
        print(f"  Total Authentication Attempts: {log_count}")
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Successful Attempts: {success_count}")
        print(f"  Failed Attempts: {total_count - success_count}")
        print(f"  Average Confidence Score: {avg_confidence:.4f}")
        print(f"  Average Liveness Score: {avg_liveness_score:.4f}")
        print(f"  Embeddings per Student: {embedding_count / student_count:.1f}")
        
        print(f"  Authentication Results Breakdown:")
        for result, count in auth_results:
            percentage = (count / total_count * 100) if total_count > 0 else 0
            print(f"    {result}: {count} ({percentage:.1f}%)")
    
    def generate_chapter4_metrics(self):
        """Generate metrics formatted for Chapter 4"""
        print("\n" + "="*60)
        print("CHAPTER 4 PERFORMANCE METRICS")
        print("="*60)
        
        if 'database_performance' in self.results:
            db_perf = self.results['database_performance']
            print(f"\n4.8.1 Database Performance (Measured Results):")
            print(f"  • Student lookup time: {db_perf['avg_student_lookup_time']*1000:.3f} milliseconds")
            print(f"  • Embedding retrieval time: {db_perf['avg_embedding_retrieval_time']*1000:.3f} milliseconds")
            print(f"  • Authentication logging time: {db_perf['avg_log_query_time']*1000:.3f} milliseconds")
            print(f"  • Database query performance: {'Sub-millisecond' if db_perf['avg_embedding_retrieval_time'] < 0.001 else 'Fast'}")
        
        if 'authentication_analysis' in self.results:
            auth_data = self.results['authentication_analysis']
            print(f"\n4.8.2 System Performance Results (Actual Data):")
            print(f"  • Total registered students: {auth_data['total_students']}")
            print(f"  • Total face embeddings stored: {auth_data['total_embeddings']}")
            print(f"  • Total authentication attempts: {auth_data['total_auth_attempts']}")
            print(f"  • Authentication success rate: {auth_data['success_rate_percent']:.2f}%")
            print(f"  • Average embeddings per student: {auth_data['embeddings_per_student']:.1f}")
            
            print(f"\n4.8.3 Accuracy Results (Based on Actual Testing):")
            print(f"  • Average confidence score: {auth_data['average_confidence_score']:.4f}")
            print(f"  • Average liveness score: {auth_data['average_liveness_score']:.4f}")
            print(f"  • Successful authentications: {auth_data['successful_attempts']}")
            print(f"  • Failed authentications: {auth_data['failed_attempts']}")
    
    def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_metrics_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        return filename
    
    def run_full_analysis(self):
        """Run complete performance analysis"""
        print("Starting Performance Analysis...")
        print("="*50)
        
        self.analyze_database_performance()
        print()
        self.analyze_existing_data()
        
        self.generate_chapter4_metrics()
        
        filename = self.save_results()
        return filename

def main():
    measurer = SimplePerformanceMeasurer()
    measurer.run_full_analysis()

if __name__ == "__main__":
    main()
