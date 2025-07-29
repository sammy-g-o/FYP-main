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
        # ('User Interface\nLayer', 8.5, 4.5, 'UI Components\n• Registration Interface\n• Authentication UI\n• Monitoring Display')
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

def create_system_workflow_diagram():
    """Create three-phase system workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define colors for each phase
    colors = {
        'registration': '#2E86AB',
        'authentication': '#A23B72',
        'monitoring': '#F18F01'
    }

    # Registration Phase
    reg_steps = [
        ('Student Input', 2, 8.5),
        ('Image Capture', 2, 7.5),
        ('Face Detection', 2, 6.5),
        ('Embedding Generation', 2, 5.5),
        ('Database Storage', 2, 4.5)
    ]

    # Draw registration phase
    ax.text(2, 9.2, 'REGISTRATION PHASE', ha='center', va='center',
            fontsize=14, fontweight='bold', color=colors['registration'])

    for i, (step, x, y) in enumerate(reg_steps):
        rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=colors['registration'],
                             edgecolor='black', alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, y, step, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

        if i < len(reg_steps) - 1:
            arrow = ConnectionPatch((x, y-0.3), (x, reg_steps[i+1][2]+0.3), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=15, fc="black")
            ax.add_artist(arrow)

    # Authentication Phase
    auth_steps = [
        ('Image Capture', 7, 8.5),
        ('Liveness Detection', 7, 7.5),
        ('Face Recognition', 7, 6.5),
        ('Database Matching', 7, 5.5),
        ('Decision', 7, 4.5)
    ]

    # Draw authentication phase
    ax.text(7, 9.2, 'AUTHENTICATION PHASE', ha='center', va='center',
            fontsize=14, fontweight='bold', color=colors['authentication'])

    for i, (step, x, y) in enumerate(auth_steps):
        if step == 'Decision':
            # Diamond for decision
            diamond = patches.RegularPolygon((x, y), 4, radius=0.5,
                                           orientation=np.pi/4,
                                           facecolor=colors['authentication'],
                                           edgecolor='black', alpha=0.8)
            ax.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                 boxstyle="round,pad=0.05",
                                 facecolor=colors['authentication'],
                                 edgecolor='black', alpha=0.8)
            ax.add_patch(rect)

        ax.text(x, y, step, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

        if i < len(auth_steps) - 1:
            arrow = ConnectionPatch((x, y-0.3), (x, auth_steps[i+1][2]+0.3), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=15, fc="black")
            ax.add_artist(arrow)

    # Monitoring Phase
    mon_steps = [
        ('Continuous Capture', 12, 8.5),
        ('Periodic Check', 12, 7.5),
        ('Re-authentication', 12, 6.5),
        ('Alert Generation', 12, 5.5),
        ('Logging', 12, 4.5)
    ]

    # Draw monitoring phase
    ax.text(12, 9.2, 'MONITORING PHASE', ha='center', va='center',
            fontsize=14, fontweight='bold', color=colors['monitoring'])

    for i, (step, x, y) in enumerate(mon_steps):
        rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=colors['monitoring'],
                             edgecolor='black', alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, y, step, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

        if i < len(mon_steps) - 1:
            arrow = ConnectionPatch((x, y-0.3), (x, mon_steps[i+1][2]+0.3), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=15, fc="black")
            ax.add_artist(arrow)

    # Add phase transitions
    # Registration to Authentication
    trans1 = ConnectionPatch((3.5, 6.5), (5.5, 6.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="gray", linestyle='--')
    ax.add_artist(trans1)
    ax.text(4.5, 6.8, 'After Registration', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgray', alpha=0.7))

    # Authentication to Monitoring
    trans2 = ConnectionPatch((8.5, 6.5), (10.5, 6.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="gray", linestyle='--')
    ax.add_artist(trans2)
    ax.text(9.5, 6.8, 'If Successful', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgray', alpha=0.7))

    # Add loop back for monitoring
    loop_arrow = ConnectionPatch((12, 4.2), (12, 8.2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc="blue",
                               connectionstyle="arc3,rad=0.5")
    ax.add_artist(loop_arrow)
    ax.text(13.5, 6.5, 'Every 30s', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))

    plt.title('System Workflow Diagram - Three Phase Operation', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('system_workflow.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_data_flow_diagram():
    """Create layered data flow architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Define layer colors
    layer_colors = {
        'input': '#E8F4FD',
        'processing': '#B8E6B8',
        'decision': '#FFE4B5',
        'storage': '#FFB6C1',
        'output': '#DDA0DD'
    }

    # Define layers
    layers = [
        {
            'name': 'INPUT LAYER',
            'y': 10,
            'color': layer_colors['input'],
            'components': ['Camera Feed', 'User Interface', 'Student Data']
        },
        {
            'name': 'PROCESSING LAYER',
            'y': 8,
            'color': layer_colors['processing'],
            'components': ['Face Detection', 'Liveness Analysis', 'Feature Extraction']
        },
        {
            'name': 'DECISION LAYER',
            'y': 6,
            'color': layer_colors['decision'],
            'components': ['Threshold Matching', 'Authentication Logic', 'Alert Generation']
        },
        {
            'name': 'STORAGE LAYER',
            'y': 4,
            'color': layer_colors['storage'],
            'components': ['SQLite Database', 'Indexed Tables', 'Audit Logs']
        },
        {
            'name': 'OUTPUT LAYER',
            'y': 2,
            'color': layer_colors['output'],
            'components': ['Authentication Results', 'Alert Notifications', 'Session Data']
        }
    ]

    # Draw layers
    for layer in layers:
        # Layer background
        layer_box = FancyBboxPatch((1, layer['y']-0.8), 10, 1.6,
                                  boxstyle="round,pad=0.1",
                                  facecolor=layer['color'],
                                  edgecolor='black',
                                  alpha=0.7)
        ax.add_patch(layer_box)

        # Layer title
        ax.text(0.5, layer['y'], layer['name'], ha='center', va='center',
                fontsize=12, fontweight='bold', rotation=90)

        # Layer components
        comp_width = 8 / len(layer['components'])
        for i, component in enumerate(layer['components']):
            comp_x = 2 + i * comp_width + comp_width/2

            comp_box = FancyBboxPatch((comp_x-comp_width/2+0.1, layer['y']-0.4),
                                     comp_width-0.2, 0.8,
                                     boxstyle="round,pad=0.05",
                                     facecolor='white',
                                     edgecolor='black',
                                     alpha=0.9)
            ax.add_patch(comp_box)
            ax.text(comp_x, layer['y'], component, ha='center', va='center',
                    fontsize=9, fontweight='bold')

    # Add data flow arrows between layers
    for i in range(len(layers)-1):
        current_layer = layers[i]
        next_layer = layers[i+1]

        # Multiple arrows showing data flow
        for j in range(3):
            arrow_x = 3 + j * 2
            arrow = ConnectionPatch((arrow_x, current_layer['y']-0.8),
                                  (arrow_x, next_layer['y']+0.8),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="blue", ec="blue",
                                  alpha=0.7)
            ax.add_artist(arrow)

    # Add bidirectional arrow for storage layer
    storage_arrow = ConnectionPatch((9, 4.8), (9, 5.2), "data", "data",
                                  arrowstyle="<->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="red", ec="red")
    ax.add_artist(storage_arrow)
    ax.text(9.5, 5, 'R/W', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))

    # Add data flow labels
    ax.text(11.5, 9, 'Raw Data', ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    ax.text(11.5, 7, 'Processed\nFeatures', ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
    ax.text(11.5, 5, 'Decisions', ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
    ax.text(11.5, 3, 'Results', ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightpink', alpha=0.7))

    plt.title('Data Flow Architecture Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('data_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_image_processing_pipeline():
    """Create image processing pipeline diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Define pipeline steps
    pipeline_steps = [
        {
            'name': 'Raw Image\nCapture',
            'x': 1.5,
            'details': 'Camera Input\nVariable Size\nRGB Format',
            'color': '#FF6B6B'
        },
        {
            'name': 'Face\nDetection',
            'x': 4,
            'details': 'Haar Cascade\nOpenCV\nBounding Box',
            'color': '#4ECDC4'
        },
        {
            'name': 'Face\nExtraction',
            'x': 6.5,
            'details': 'ROI Extraction\nPadding Added\nCrop to Face',
            'color': '#45B7D1'
        },
        {
            'name': 'Resize\nNormalization',
            'x': 9,
            'details': '160×160 pixels\nFaceNet Input\nAspect Ratio',
            'color': '#96CEB4'
        },
        {
            'name': 'Quality\nValidation',
            'x': 11.5,
            'details': 'Size Check\nClarity Test\nAccept/Reject',
            'color': '#FFEAA7'
        },
        {
            'name': 'Processed\nFace',
            'x': 14,
            'details': 'Ready for Model\n160×160×3\nNormalized',
            'color': '#DDA0DD'
        }
    ]

    # Draw pipeline steps
    for i, step in enumerate(pipeline_steps):
        # Main process box
        main_box = FancyBboxPatch((step['x']-0.7, 5), 1.4, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor=step['color'],
                                 edgecolor='black',
                                 alpha=0.8)
        ax.add_patch(main_box)
        ax.text(step['x'], 5.75, step['name'], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

        # Details box
        detail_box = FancyBboxPatch((step['x']-0.7, 2.5), 1.4, 1.5,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white',
                                   edgecolor='gray',
                                   alpha=0.9)
        ax.add_patch(detail_box)
        ax.text(step['x'], 3.25, step['details'], ha='center', va='center',
                fontsize=8, color='black')

        # Connection between main and detail boxes
        connection = ConnectionPatch((step['x'], 5), (step['x'], 4), "data", "data",
                                   arrowstyle="-", shrinkA=5, shrinkB=5,
                                   mutation_scale=10, fc="gray", ec="gray",
                                   linestyle='--')
        ax.add_artist(connection)

        # Arrow to next step
        if i < len(pipeline_steps) - 1:
            next_step = pipeline_steps[i + 1]
            arrow = ConnectionPatch((step['x']+0.7, 5.75), (next_step['x']-0.7, 5.75),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="black", ec="black")
            ax.add_artist(arrow)

    # Add sample images representation
    # Raw image representation
    raw_img = patches.Rectangle((0.8, 6.8), 1.4, 1, facecolor='lightblue',
                               edgecolor='black', alpha=0.7)
    ax.add_patch(raw_img)
    ax.text(1.5, 7.3, 'Original\nImage', ha='center', va='center', fontsize=8)

    # Processed image representation
    proc_img = patches.Rectangle((13.3, 6.8), 1.4, 1, facecolor='lightgreen',
                                edgecolor='black', alpha=0.7)
    ax.add_patch(proc_img)
    ax.text(14, 7.3, '160×160\nFace', ha='center', va='center', fontsize=8)

    # Add quality check decision
    # Success path
    success_arrow = ConnectionPatch((11.5, 4.5), (13.3, 5.75), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=15, fc="green", ec="green")
    ax.add_artist(success_arrow)
    ax.text(12.4, 4.8, 'PASS', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))

    # Failure path
    fail_arrow = ConnectionPatch((11.5, 4.5), (11.5, 1.5), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc="red", ec="red")
    ax.add_artist(fail_arrow)
    ax.text(11.5, 1.2, 'REJECT', ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightcoral', alpha=0.7))

    # Add technical specifications
    ax.text(8, 0.5, 'Technical Specifications:', ha='center', va='center',
            fontsize=12, fontweight='bold')
    ax.text(8, 0.1, 'Input: Variable size RGB images • Processing: OpenCV Haar Cascades • Output: 160×160×3 normalized face images',
            ha='center', va='center', fontsize=10)

    plt.title('Image Processing Pipeline Diagram', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('image_processing_pipeline.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_all_diagrams():
    """Generate all diagrams for Chapter 4"""
    # print("Generating System Architecture Diagram...")
    # create_system_architecture_diagram()
    
    # print("Generating Authentication Workflow Diagram...")
    # create_authentication_workflow_diagram()
    
    # print("Generating Database Schema Diagram...")
    # create_database_schema_diagram()
    
    # print("Generating system workflow Diagram...")
    # create_system_workflow_diagram()

    # print("Generating create data flow diagram...")
    # create_data_flow_diagram()

    print("Generating create image processing pipeline...")
    create_image_processing_pipeline()
    
    print("All diagrams generated successfully!")
    print("Files created:")
    print("  - system_architecture.png")
    print("  - authentication_workflow.png")
    print("  - database_schema.png")

if __name__ == "__main__":
    generate_all_diagrams()
