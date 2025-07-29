#!/usr/bin/env python3
"""
Evaluation Results Analyzer

This script analyzes and compares multiple evaluation results,
generates trend analysis, and provides insights into system performance.
"""

import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

class EvaluationAnalyzer:
    def __init__(self):
        self.results = []
        self.df = None
    
    def load_evaluation_results(self, pattern="*evaluation*.json"):
        """Load all evaluation result files matching the pattern"""
        files = glob.glob(pattern)
        
        if not files:
            print(f"❌ No evaluation files found matching pattern: {pattern}")
            return False
        
        print(f"📁 Found {len(files)} evaluation files:")
        
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                # Extract key metrics
                result = {
                    'filename': file,
                    'timestamp': data.get('metadata', {}).get('evaluation_timestamp', ''),
                    'model_name': data.get('metadata', {}).get('model_name', 'Unknown'),
                    'threshold': data.get('metadata', {}).get('recognition_threshold', 0),
                    'accuracy': data.get('classification_metrics', {}).get('accuracy', 0),
                    'precision': data.get('classification_metrics', {}).get('precision', 0),
                    'recall': data.get('classification_metrics', {}).get('recall_sensitivity_tpr', 0),
                    'f1_score': data.get('classification_metrics', {}).get('f1_score', 0),
                    'specificity': data.get('classification_metrics', {}).get('specificity_tnr', 0),
                    'far': data.get('biometric_error_rates', {}).get('false_acceptance_rate_far', 0),
                    'frr': data.get('biometric_error_rates', {}).get('false_rejection_rate_frr', 0),
                    'hter': data.get('biometric_error_rates', {}).get('half_total_error_rate_hter', 0),
                    'eer': data.get('biometric_error_rates', {}).get('equal_error_rate_eer', 0),
                    'auc': data.get('roc_analysis', {}).get('auc', 0),
                    'tp': data.get('confusion_matrix', {}).get('tp', 0),
                    'tn': data.get('confusion_matrix', {}).get('tn', 0),
                    'fp': data.get('confusion_matrix', {}).get('fp', 0),
                    'fn': data.get('confusion_matrix', {}).get('fn', 0),
                    'total_attempts': data.get('additional_metrics', {}).get('total_attempts', 0),
                    'genuine_attempts': data.get('additional_metrics', {}).get('genuine_attempts', 0),
                    'impostor_attempts': data.get('additional_metrics', {}).get('impostor_attempts', 0)
                }
                
                self.results.append(result)
                print(f"   ✅ {file}")
                
            except Exception as e:
                print(f"   ❌ {file}: {e}")
        
        if self.results:
            self.df = pd.DataFrame(self.results)
            # Sort by timestamp if available
            if 'timestamp' in self.df.columns:
                self.df = self.df.sort_values('timestamp')
            
            print(f"\n✅ Loaded {len(self.results)} evaluation results")
            return True
        
        return False
    
    def generate_comparison_report(self):
        """Generate a comprehensive comparison report"""
        if self.df is None or self.df.empty:
            print("❌ No data loaded for comparison")
            return
        
        print("\n" + "=" * 80)
        print("📊 EVALUATION RESULTS COMPARISON REPORT")
        print("=" * 80)
        
        # Summary statistics
        print("\n📈 PERFORMANCE SUMMARY:")
        print("-" * 50)
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'far', 'frr', 'hter', 'auc']
        summary_stats = self.df[metrics].describe()
        
        for metric in metrics:
            mean_val = summary_stats.loc['mean', metric]
            std_val = summary_stats.loc['std', metric]
            min_val = summary_stats.loc['min', metric]
            max_val = summary_stats.loc['max', metric]
            
            print(f"{metric.upper():12}: {mean_val:.3f} ± {std_val:.3f} (range: {min_val:.3f} - {max_val:.3f})")
        
        # Best and worst performing evaluations
        print(f"\n🏆 BEST PERFORMING EVALUATION:")
        print("-" * 50)
        best_idx = self.df['accuracy'].idxmax()
        best_result = self.df.iloc[best_idx]
        print(f"File: {best_result['filename']}")
        print(f"Accuracy: {best_result['accuracy']:.3f}")
        print(f"FAR: {best_result['far']:.3f}")
        print(f"FRR: {best_result['frr']:.3f}")
        print(f"AUC: {best_result['auc']:.3f}")
        
        print(f"\n📉 WORST PERFORMING EVALUATION:")
        print("-" * 50)
        worst_idx = self.df['accuracy'].idxmin()
        worst_result = self.df.iloc[worst_idx]
        print(f"File: {worst_result['filename']}")
        print(f"Accuracy: {worst_result['accuracy']:.3f}")
        print(f"FAR: {worst_result['far']:.3f}")
        print(f"FRR: {worst_result['frr']:.3f}")
        print(f"AUC: {worst_result['auc']:.3f}")
        
        # Threshold analysis
        if len(self.df['threshold'].unique()) > 1:
            print(f"\n🎯 THRESHOLD ANALYSIS:")
            print("-" * 50)
            threshold_analysis = self.df.groupby('threshold')[['accuracy', 'far', 'frr']].mean()
            print(threshold_analysis)
        
        print("=" * 80)
    
    def generate_trend_visualizations(self):
        """Generate trend analysis visualizations"""
        if self.df is None or self.df.empty:
            print("❌ No data loaded for visualization")
            return
        
        print("📈 Generating trend analysis visualizations...")
        
        # Create output directory
        import os
        os.makedirs("evaluation_analysis", exist_ok=True)
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Performance Metrics Comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy and F1-Score
        axes[0, 0].bar(range(len(self.df)), self.df['accuracy'], alpha=0.7, label='Accuracy')
        axes[0, 0].bar(range(len(self.df)), self.df['f1_score'], alpha=0.7, label='F1-Score')
        axes[0, 0].set_title('Accuracy and F1-Score Comparison')
        axes[0, 0].set_xlabel('Evaluation Run')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Error Rates
        axes[0, 1].bar(range(len(self.df)), self.df['far'], alpha=0.7, label='FAR')
        axes[0, 1].bar(range(len(self.df)), self.df['frr'], alpha=0.7, label='FRR')
        axes[0, 1].set_title('Error Rates Comparison')
        axes[0, 1].set_xlabel('Evaluation Run')
        axes[0, 1].set_ylabel('Error Rate')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Precision and Recall
        axes[1, 0].bar(range(len(self.df)), self.df['precision'], alpha=0.7, label='Precision')
        axes[1, 0].bar(range(len(self.df)), self.df['recall'], alpha=0.7, label='Recall')
        axes[1, 0].set_title('Precision and Recall Comparison')
        axes[1, 0].set_xlabel('Evaluation Run')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # AUC Scores
        axes[1, 1].bar(range(len(self.df)), self.df['auc'], alpha=0.7, color='orange')
        axes[1, 1].set_title('AUC Scores Comparison')
        axes[1, 1].set_xlabel('Evaluation Run')
        axes[1, 1].set_ylabel('AUC Score')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('evaluation_analysis/performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Correlation Matrix
        plt.figure(figsize=(10, 8))
        correlation_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'far', 'frr', 'auc']
        correlation_matrix = self.df[correlation_metrics].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Performance Metrics Correlation Matrix')
        plt.tight_layout()
        plt.savefig('evaluation_analysis/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Threshold vs Performance (if multiple thresholds)
        if len(self.df['threshold'].unique()) > 1:
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            plt.scatter(self.df['threshold'], self.df['accuracy'], alpha=0.7)
            plt.xlabel('Threshold')
            plt.ylabel('Accuracy')
            plt.title('Threshold vs Accuracy')
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 2, 2)
            plt.scatter(self.df['threshold'], self.df['far'], alpha=0.7, color='red')
            plt.xlabel('Threshold')
            plt.ylabel('FAR')
            plt.title('Threshold vs FAR')
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 2, 3)
            plt.scatter(self.df['threshold'], self.df['frr'], alpha=0.7, color='orange')
            plt.xlabel('Threshold')
            plt.ylabel('FRR')
            plt.title('Threshold vs FRR')
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 2, 4)
            plt.scatter(self.df['threshold'], self.df['auc'], alpha=0.7, color='green')
            plt.xlabel('Threshold')
            plt.ylabel('AUC')
            plt.title('Threshold vs AUC')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('evaluation_analysis/threshold_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print("✅ Visualizations saved to evaluation_analysis/ directory")
    
    def export_comparison_csv(self):
        """Export comparison data to CSV"""
        if self.df is None or self.df.empty:
            print("❌ No data loaded for export")
            return
        
        filename = f"evaluation_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.df.to_csv(filename, index=False)
        print(f"💾 Comparison data exported to: {filename}")
        return filename

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze and compare evaluation results')
    parser.add_argument('--pattern', default='*evaluation*.json',
                       help='File pattern to match evaluation JSON files')
    parser.add_argument('--no-plots', action='store_true',
                       help='Skip generating visualization plots')
    
    args = parser.parse_args()
    
    analyzer = EvaluationAnalyzer()
    
    # Load evaluation results
    if not analyzer.load_evaluation_results(args.pattern):
        print("❌ No evaluation results could be loaded")
        return
    
    # Generate comparison report
    analyzer.generate_comparison_report()
    
    # Generate visualizations
    if not args.no_plots:
        analyzer.generate_trend_visualizations()
    
    # Export to CSV
    analyzer.export_comparison_csv()
    
    print("\n🎉 Analysis completed successfully!")

if __name__ == "__main__":
    main()
