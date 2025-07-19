#!/usr/bin/env python3
"""
Results Analysis Script for Chapter 4
Analyzes system performance, accuracy, and generates comprehensive results
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import os
from database_manager import DatabaseManager

class ResultsAnalyzer:
    def __init__(self, db_path='students.db'):
        self.db_manager = DatabaseManager(db_path)
        self.db_path = db_path
        self.results = {}
    
    def analyze_registration_data(self):
        """Analyze student registration data"""
        print("Analyzing Registration Data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get student count
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        # Get embedding count
        cursor.execute("SELECT COUNT(*) FROM face_embeddings")
        total_embeddings = cursor.fetchone()[0]
        
        # Get embeddings per student
        cursor.execute("""
            SELECT student_id, COUNT(*) as embedding_count 
            FROM face_embeddings 
            GROUP BY student_id
        """)
        embeddings_per_student = cursor.fetchall()
        
        # Calculate statistics
        if embeddings_per_student:
            embedding_counts = [count for _, count in embeddings_per_student]
            avg_embeddings = np.mean(embedding_counts)
            max_embeddings = np.max(embedding_counts)
            min_embeddings = np.min(embedding_counts)
        else:
            avg_embeddings = max_embeddings = min_embeddings = 0
        
        self.results['registration'] = {
            'total_students': total_students,
            'total_embeddings': total_embeddings,
            'avg_embeddings_per_student': avg_embeddings,
            'max_embeddings_per_student': max_embeddings,
            'min_embeddings_per_student': min_embeddings,
            'embeddings_distribution': embedding_counts if embeddings_per_student else []
        }
        
        conn.close()
        
        print(f"Registration Analysis Complete:")
        print(f"  Total Students: {total_students}")
        print(f"  Total Embeddings: {total_embeddings}")
        print(f"  Average Embeddings per Student: {avg_embeddings:.2f}")
    
    def analyze_authentication_logs(self):
        """Analyze authentication attempt logs"""
        print("Analyzing Authentication Logs...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all authentication logs
        cursor.execute("""
            SELECT auth_result, liveness_score, confidence_score, timestamp 
            FROM auth_logs 
            ORDER BY timestamp DESC
        """)
        logs = cursor.fetchall()
        
        if not logs:
            print("No authentication logs found.")
            self.results['authentication'] = {
                'total_attempts': 0,
                'success_rate': 0,
                'avg_liveness_score': 0,
                'avg_confidence_score': 0
            }
            conn.close()
            return
        
        # Analyze results
        total_attempts = len(logs)
        successful_attempts = sum(1 for log in logs if log[0] == 'SUCCESS')
        success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0
        
        # Calculate average scores
        liveness_scores = [log[1] for log in logs if log[1] is not None]
        confidence_scores = [log[2] for log in logs if log[2] is not None]
        
        avg_liveness = np.mean(liveness_scores) if liveness_scores else 0
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        # Analyze by result type
        result_counts = {}
        for log in logs:
            result = log[0]
            result_counts[result] = result_counts.get(result, 0) + 1
        
        # Analyze temporal patterns (last 24 hours)
        recent_logs = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log[3])
                if log_time > cutoff_time:
                    recent_logs.append(log)
            except:
                continue
        
        self.results['authentication'] = {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'success_rate': success_rate,
            'avg_liveness_score': avg_liveness,
            'avg_confidence_score': avg_confidence,
            'result_breakdown': result_counts,
            'recent_attempts_24h': len(recent_logs),
            'liveness_scores': liveness_scores,
            'confidence_scores': confidence_scores
        }
        
        conn.close()
        
        print(f"Authentication Analysis Complete:")
        print(f"  Total Attempts: {total_attempts}")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Average Liveness Score: {avg_liveness:.4f}")
        print(f"  Average Confidence Score: {avg_confidence:.4f}")
    
    def analyze_system_accuracy(self):
        """Analyze system accuracy metrics"""
        print("Analyzing System Accuracy...")
        
        auth_data = self.results.get('authentication', {})
        
        # Calculate accuracy metrics
        success_rate = auth_data.get('success_rate', 0)
        liveness_scores = auth_data.get('liveness_scores', [])
        confidence_scores = auth_data.get('confidence_scores', [])
        
        # Calculate score distributions
        if liveness_scores:
            liveness_stats = {
                'mean': np.mean(liveness_scores),
                'std': np.std(liveness_scores),
                'min': np.min(liveness_scores),
                'max': np.max(liveness_scores),
                'median': np.median(liveness_scores)
            }
        else:
            liveness_stats = {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0}
        
        if confidence_scores:
            confidence_stats = {
                'mean': np.mean(confidence_scores),
                'std': np.std(confidence_scores),
                'min': np.min(confidence_scores),
                'max': np.max(confidence_scores),
                'median': np.median(confidence_scores)
            }
        else:
            confidence_stats = {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0}
        
        # Calculate quality metrics
        high_confidence_threshold = 0.8
        high_liveness_threshold = 0.7
        
        high_confidence_rate = sum(1 for score in confidence_scores if score >= high_confidence_threshold) / len(confidence_scores) if confidence_scores else 0
        high_liveness_rate = sum(1 for score in liveness_scores if score >= high_liveness_threshold) / len(liveness_scores) if liveness_scores else 0
        
        self.results['accuracy'] = {
            'overall_success_rate': success_rate,
            'liveness_statistics': liveness_stats,
            'confidence_statistics': confidence_stats,
            'high_confidence_rate': high_confidence_rate,
            'high_liveness_rate': high_liveness_rate,
            'quality_threshold_confidence': high_confidence_threshold,
            'quality_threshold_liveness': high_liveness_threshold
        }
        
        print(f"Accuracy Analysis Complete:")
        print(f"  Overall Success Rate: {success_rate:.2%}")
        print(f"  High Confidence Rate (>{high_confidence_threshold}): {high_confidence_rate:.2%}")
        print(f"  High Liveness Rate (>{high_liveness_threshold}): {high_liveness_rate:.2%}")
    
    def generate_performance_charts(self):
        """Generate performance visualization charts"""
        print("Generating Performance Charts...")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Chart 1: Success Rate
        auth_data = self.results.get('authentication', {})
        result_breakdown = auth_data.get('result_breakdown', {})
        
        if result_breakdown:
            labels = list(result_breakdown.keys())
            sizes = list(result_breakdown.values())
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)])
            ax1.set_title('Authentication Results Distribution')
        else:
            ax1.text(0.5, 0.5, 'No authentication data available', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Authentication Results Distribution')
        
        # Chart 2: Score Distributions
        liveness_scores = auth_data.get('liveness_scores', [])
        confidence_scores = auth_data.get('confidence_scores', [])
        
        if liveness_scores and confidence_scores:
            ax2.hist(liveness_scores, alpha=0.7, label='Liveness Scores', bins=20, color='#2E86AB')
            ax2.hist(confidence_scores, alpha=0.7, label='Confidence Scores', bins=20, color='#A23B72')
            ax2.set_xlabel('Score')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Score Distributions')
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, 'No score data available', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Score Distributions')
        
        # Chart 3: Registration Statistics
        reg_data = self.results.get('registration', {})
        embeddings_dist = reg_data.get('embeddings_distribution', [])
        
        if embeddings_dist:
            ax3.hist(embeddings_dist, bins=max(1, len(set(embeddings_dist))), 
                    color='#F18F01', alpha=0.7)
            ax3.set_xlabel('Number of Embeddings')
            ax3.set_ylabel('Number of Students')
            ax3.set_title('Embeddings per Student Distribution')
        else:
            ax3.text(0.5, 0.5, 'No registration data available', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Embeddings per Student Distribution')
        
        # Chart 4: System Performance Summary
        accuracy_data = self.results.get('accuracy', {})
        metrics = ['Success Rate', 'High Confidence', 'High Liveness']
        values = [
            accuracy_data.get('overall_success_rate', 0),
            accuracy_data.get('high_confidence_rate', 0),
            accuracy_data.get('high_liveness_rate', 0)
        ]
        
        bars = ax4.bar(metrics, values, color=['#2E86AB', '#A23B72', '#F18F01'])
        ax4.set_ylabel('Rate')
        ax4.set_title('System Performance Metrics')
        ax4.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2%}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('performance_charts.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Performance charts saved as 'performance_charts.png'")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive results report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE RESULTS ANALYSIS")
        print("="*60)
        
        # Run all analyses
        self.analyze_registration_data()
        print()
        self.analyze_authentication_logs()
        print()
        self.analyze_system_accuracy()
        print()
        self.generate_performance_charts()
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"results_analysis_{timestamp}.json"
        
        with open(results_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {results_filename}")
        
        # Generate Chapter 4 summary
        self.generate_chapter4_summary()
    
    def generate_chapter4_summary(self):
        """Generate summary specifically for Chapter 4"""
        print("\n" + "="*60)
        print("CHAPTER 4 RESULTS SUMMARY")
        print("="*60)
        
        reg_data = self.results.get('registration', {})
        auth_data = self.results.get('authentication', {})
        acc_data = self.results.get('accuracy', {})
        
        print("4.9.1 System Implementation Results:")
        print(f"  • Successfully registered {reg_data.get('total_students', 0)} students")
        print(f"  • Generated {reg_data.get('total_embeddings', 0)} face embeddings")
        print(f"  • Average {reg_data.get('avg_embeddings_per_student', 0):.1f} embeddings per student")
        
        print("\n4.9.2 Authentication Performance:")
        print(f"  • Total authentication attempts: {auth_data.get('total_attempts', 0)}")
        print(f"  • Overall success rate: {auth_data.get('success_rate', 0):.2%}")
        print(f"  • Average liveness detection score: {auth_data.get('avg_liveness_score', 0):.4f}")
        print(f"  • Average face recognition confidence: {auth_data.get('avg_confidence_score', 0):.4f}")
        
        print("\n4.9.3 Quality Metrics:")
        print(f"  • High confidence authentications: {acc_data.get('high_confidence_rate', 0):.2%}")
        print(f"  • High liveness detection rate: {acc_data.get('high_liveness_rate', 0):.2%}")
        
        liveness_stats = acc_data.get('liveness_statistics', {})
        confidence_stats = acc_data.get('confidence_statistics', {})
        
        print("\n4.9.4 Statistical Analysis:")
        print(f"  • Liveness Score Range: {liveness_stats.get('min', 0):.3f} - {liveness_stats.get('max', 0):.3f}")
        print(f"  • Confidence Score Range: {confidence_stats.get('min', 0):.3f} - {confidence_stats.get('max', 0):.3f}")
        print(f"  • Liveness Score Std Dev: {liveness_stats.get('std', 0):.3f}")
        print(f"  • Confidence Score Std Dev: {confidence_stats.get('std', 0):.3f}")
        
        print("\n4.9.5 System Reliability:")
        result_breakdown = auth_data.get('result_breakdown', {})
        if result_breakdown:
            for result, count in result_breakdown.items():
                percentage = (count / auth_data.get('total_attempts', 1)) * 100
                print(f"  • {result}: {count} attempts ({percentage:.1f}%)")

def main():
    """Main function to run results analysis"""
    analyzer = ResultsAnalyzer()
    analyzer.generate_comprehensive_report()

if __name__ == "__main__":
    main()
