#!/usr/bin/env python3
"""
Diagram Generator for Chapter 4 Documentation
Generates system architecture and workflow diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_system_architecture_diagram():
    """Create system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Define colors
    colors = {
        'main': '#2E86AB',
        'module': '#A23B72',
        'data': '#F18F01',
        'interface': '#C73E1D'
    }
    
    # Main System Box
    main_box = FancyBboxPatch((1, 6), 8, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['main'], 
                              edgecolor='black', 
                              alpha=0.8)
    ax.add_patch(main_box)
    ax.text(5, 6.75, 'Exam Proctoring System\n(ExamProctorSystem)', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    # Core Modules
    modules = [
        ('Face Recognition\nModule', 1.5, 4.5, 'FaceRecognizer\n• DeepFace/Facenet\n• 128D Embeddings\n• Cosine Similarity'),
        ('Liveness Detection\nModule', 4, 4.5, 'LivenessDetector\n• Texture Analysis (LBP)\n• Blink Detection\n• Anti-Spoofing'),
        ('Database\nManager', 6.5, 4.5, 'DatabaseManager\n• SQLite Database\n• Student Records\n• Authentication Logs'),
        ('User Interface\nLayer', 8.5, 4.5, 'UI Components\n• Registration Interface\n• Authentication UI\n• Monitoring Display')
    ]
    
    for title, x, y, details in modules:
        # Module box
        module_box = FancyBboxPatch((x-0.7, y-0.8), 1.4, 1.6, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=colors['module'], 
                                   edgecolor='black', 
                                   alpha=0.7)
        ax.add_patch(module_box)
        ax.text(x, y+0.3, title, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
        ax.text(x, y-0.3, details, ha='center', va='center', 
                fontsize=8, color='white')
        
        # Connection to main system
        connection = ConnectionPatch((x, y+0.8), (5, 6), "data", "data",
                                   arrowstyle="->", shrinkA=5, shrinkB=5,
                                   mutation_scale=20, fc="black")
        ax.add_artist(connection)
    
    # Data Storage
    data_box = FancyBboxPatch((2, 2), 6, 1.2, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['data'], 
                             edgecolor='black', 
                             alpha=0.8)
    ax.add_patch(data_box)
    ax.text(5, 2.6, 'SQLite Database', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    ax.text(5, 2.2, 'Students • Face Embeddings • Authentication Logs • Session Data', 
            ha='center', va='center', fontsize=9, color='white')
    
    # Connection from Database Manager to Data Storage
    db_connection = ConnectionPatch((6.5, 3.7), (5, 3.2), "data", "data",
                                  arrowstyle="<->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="black")
    ax.add_artist(db_connection)
    
    # External Components
    external_box = FancyBboxPatch((0.5, 0.2), 9, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=colors['interface'], 
                                 edgecolor='black', 
                                 alpha=0.6)
    ax.add_patch(external_box)
    ax.text(5, 0.6, 'External Dependencies: OpenCV • DeepFace • Dlib • TensorFlow • PyTorch', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    plt.title('System Architecture Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_authentication_workflow_diagram():
    """Create authentication workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Define workflow steps
    steps = [
        ('Start Exam Session', 5, 15, '#2E86AB'),
        ('Initialize Camera', 5, 14, '#2E86AB'),
        ('Capture Frame', 5, 13, '#A23B72'),
        ('Face Detection', 5, 12, '#A23B72'),
        ('Liveness Check', 3, 11, '#F18F01'),
        ('Face Recognition', 7, 11, '#F18F01'),
        ('Authentication Decision', 5, 10, '#C73E1D'),
        ('Log Result', 5, 9, '#2E86AB'),
        ('Grant/Deny Access', 5, 8, '#C73E1D'),
        ('Continuous Monitoring', 5, 7, '#A23B72'),
        ('Re-authentication', 5, 6, '#F18F01'),
        ('Session Management', 5, 5, '#2E86AB')
    ]
    
    # Draw workflow steps
    for i, (step, x, y, color) in enumerate(steps):
        if 'Check' in step or 'Recognition' in step:
            # Diamond shape for decision points
            diamond = patches.RegularPolygon((x, y), 4, radius=0.6, 
                                           orientation=np.pi/4, 
                                           facecolor=color, 
                                           edgecolor='black', 
                                           alpha=0.8)
            ax.add_patch(diamond)
        else:
            # Rectangle for process steps
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, 
                                 edgecolor='black', 
                                 alpha=0.8)
            ax.add_patch(rect)
        
        ax.text(x, y, step, ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Add arrows between steps
        if i < len(steps) - 1:
            next_step = steps[i + 1]
            if step == 'Face Detection':
                # Split to liveness and recognition
                arrow1 = ConnectionPatch((x-0.5, y-0.3), (3, 11.3), "data", "data",
                                       arrowstyle="->", shrinkA=5, shrinkB=5,
                                       mutation_scale=15, fc="black")
                ax.add_artist(arrow1)
                arrow2 = ConnectionPatch((x+0.5, y-0.3), (7, 11.3), "data", "data",
                                       arrowstyle="->", shrinkA=5, shrinkB=5,
                                       mutation_scale=15, fc="black")
                ax.add_artist(arrow2)
            elif step in ['Liveness Check', 'Face Recognition']:
                # Converge to authentication decision
                arrow = ConnectionPatch((x, y-0.6), (5, 10.6), "data", "data",
                                      arrowstyle="->", shrinkA=5, shrinkB=5,
                                      mutation_scale=15, fc="black")
                ax.add_artist(arrow)
            elif step != 'Face Detection':
                # Regular flow
                arrow = ConnectionPatch((x, y-0.3), (next_step[1], next_step[2]+0.3), "data", "data",
                                      arrowstyle="->", shrinkA=5, shrinkB=5,
                                      mutation_scale=15, fc="black")
                ax.add_artist(arrow)
    
    # Add decision outcomes
    ax.text(2, 10, 'PASS', ha='center', va='center', fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    ax.text(8, 10, 'PASS', ha='center', va='center', fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    ax.text(3.5, 8.5, 'SUCCESS', ha='center', va='center', fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    ax.text(6.5, 8.5, 'FAILURE', ha='center', va='center', fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
    
    # Add loop back arrow for continuous monitoring
    loop_arrow = ConnectionPatch((5, 4.7), (8.5, 7), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc="blue",
                               connectionstyle="arc3,rad=0.3")
    ax.add_artist(loop_arrow)
    ax.text(7.5, 5.5, 'Every 30s', ha='center', va='center', fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))
    
    plt.title('Authentication Workflow Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('authentication_workflow.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_database_schema_diagram():
    """Create database schema diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define table positions and content
    tables = [
        {
            'name': 'students',
            'pos': (2, 7),
            'fields': [
                'id (PK, INTEGER)',
                'student_id (UNIQUE, TEXT)',
                'name (TEXT)',
                'registration_date (TIMESTAMP)'
            ]
        },
        {
            'name': 'face_embeddings',
            'pos': (6, 7),
            'fields': [
                'id (PK, INTEGER)',
                'student_id (FK, TEXT)',
                'face_embedding (BLOB)',
                'description (TEXT)',
                'added_date (TIMESTAMP)'
            ]
        },
        {
            'name': 'auth_logs',
            'pos': (10, 7),
            'fields': [
                'id (PK, INTEGER)',
                'student_id (TEXT)',
                'timestamp (TIMESTAMP)',
                'auth_result (TEXT)',
                'liveness_score (REAL)',
                'confidence_score (REAL)',
                'exam_session_id (TEXT)'
            ]
        }
    ]
    
    # Draw tables
    for table in tables:
        x, y = table['pos']
        
        # Table header
        header_box = FancyBboxPatch((x-1.5, y+0.5), 3, 0.8, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='#2E86AB', 
                                   edgecolor='black')
        ax.add_patch(header_box)
        ax.text(x, y+0.9, table['name'].upper(), ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # Table fields
        field_height = len(table['fields']) * 0.4 + 0.2
        field_box = FancyBboxPatch((x-1.5, y-field_height), 3, field_height, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='lightgray', 
                                  edgecolor='black')
        ax.add_patch(field_box)
        
        for i, field in enumerate(table['fields']):
            ax.text(x, y-0.3-i*0.4, field, ha='center', va='center', 
                    fontsize=9, fontweight='normal')
    
    # Draw relationships
    # students -> face_embeddings
    rel1 = ConnectionPatch((3.5, 7), (4.5, 7), "data", "data",
                          arrowstyle="->", shrinkA=5, shrinkB=5,
                          mutation_scale=20, fc="red", ec="red")
    ax.add_artist(rel1)
    ax.text(4, 7.3, '1:N', ha='center', va='center', fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
    
    # Add relationship labels
    ax.text(6, 3, 'Relationships:', ha='left', va='top', fontsize=12, fontweight='bold')
    ax.text(6, 2.5, '• One student can have multiple face embeddings', ha='left', va='top', fontsize=10)
    ax.text(6, 2.1, '• Authentication logs reference student_id', ha='left', va='top', fontsize=10)
    ax.text(6, 1.7, '• Face embeddings are 128-dimensional vectors (BLOB)', ha='left', va='top', fontsize=10)
    ax.text(6, 1.3, '• All tables include timestamp fields for auditing', ha='left', va='top', fontsize=10)
    
    plt.title('Database Schema Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('database_schema.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_all_diagrams():
    """Generate all diagrams for Chapter 4"""
    print("Generating System Architecture Diagram...")
    create_system_architecture_diagram()
    
    print("Generating Authentication Workflow Diagram...")
    create_authentication_workflow_diagram()
    
    print("Generating Database Schema Diagram...")
    create_database_schema_diagram()
    
    print("All diagrams generated successfully!")
    print("Files created:")
    print("  - system_architecture.png")
    print("  - authentication_workflow.png")
    print("  - database_schema.png")

if __name__ == "__main__":
    generate_all_diagrams()
