#!/usr/bin/env python3
"""
Quick Evaluation Runner

This script provides a simple interface to run the enhanced evaluation system
with common configurations and options.
"""

import os
import sys
from enhanced_evaluation import EnhancedEvaluationSystem

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if test_data directory exists
    if not os.path.exists('test_data'):
        print("❌ test_data directory not found!")
        print("Please create the test_data directory with the following structure:")
        print("test_data/")
        print("├── student_id_1/")
        print("│   ├── genuine_image_1.jpg")
        print("│   └── genuine_image_2.jpg")
        print("├── student_id_2/")
        print("│   └── genuine_image_1.jpg")
        print("└── impostors/")
        print("    ├── impostor_1.jpg")
        print("    └── impostor_2.jpg")
        return False
    
    # Check if there are any test images
    test_dirs = [d for d in os.listdir('test_data') if os.path.isdir(os.path.join('test_data', d))]
    if not test_dirs:
        print("❌ No test directories found in test_data/")
        return False
    
    print(f"✅ Found test directories: {test_dirs}")
    
    # Check if database has registered students
    try:
        from database_manager import DatabaseManager
        db_manager = DatabaseManager()
        students = db_manager.get_all_students()
        if not students:
            print("❌ No students registered in database!")
            print("Please register students first using the registration scripts.")
            return False
        print(f"✅ Found {len(students)} registered students")
    except Exception as e:
        print(f"⚠️  Warning: Could not check database: {e}")
    
    return True

def run_quick_evaluation():
    """Run a quick evaluation with default settings"""
    print("🚀 Starting Quick Evaluation...")
    print("=" * 50)
    
    if not check_prerequisites():
        return False
    
    try:
        evaluator = EnhancedEvaluationSystem()
        results = evaluator.run_comprehensive_evaluation()
        
        if results:
            print("\n✅ Quick evaluation completed successfully!")
            return True
        else:
            print("\n❌ Quick evaluation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        return False

def run_comparison_evaluation(baseline_file):
    """Run evaluation and compare with baseline"""
    print(f"🔄 Running Comparison Evaluation with baseline: {baseline_file}")
    print("=" * 60)
    
    if not os.path.exists(baseline_file):
        print(f"❌ Baseline file not found: {baseline_file}")
        return False
    
    if not check_prerequisites():
        return False
    
    try:
        evaluator = EnhancedEvaluationSystem()
        results = evaluator.run_comprehensive_evaluation()
        
        if results:
            evaluator.compare_with_baseline(baseline_file)
            print("\n✅ Comparison evaluation completed successfully!")
            return True
        else:
            print("\n❌ Comparison evaluation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during comparison evaluation: {e}")
        return False

def main():
    """Main function with menu interface"""
    print("🎯 Face Recognition System - Evaluation Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == 'quick':
            success = run_quick_evaluation()
        elif sys.argv[1] == 'compare' and len(sys.argv) > 2:
            success = run_comparison_evaluation(sys.argv[2])
        else:
            print("Usage:")
            print("  python run_evaluation.py quick")
            print("  python run_evaluation.py compare <baseline_file.json>")
            return
    else:
        # Interactive mode
        print("Select evaluation mode:")
        print("1. Quick Evaluation (default settings)")
        print("2. Compare with Baseline")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1' or choice == '':
            success = run_quick_evaluation()
        elif choice == '2':
            baseline_file = input("Enter baseline JSON file path: ").strip()
            if baseline_file:
                success = run_comparison_evaluation(baseline_file)
            else:
                print("❌ No baseline file specified")
                return
        elif choice == '3':
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice")
            return
    
    if success:
        print("\n📁 Check the following output files:")
        print("   - enhanced_evaluation_*.json (comprehensive results)")
        print("   - evaluation_detailed_results.csv (detailed per-attempt results)")
        print("   - evaluation_plots/ (visualization charts)")

if __name__ == "__main__":
    main()
