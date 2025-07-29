# Intelligent Exam Proctoring System

An advanced exam proctoring system that uses face recognition and liveness detection to ensure secure and automated student authentication during examinations.

## Features

- **Face Recognition**: DeepFace with Facenet model for accurate student identification
- **Liveness Detection**: Dual-approach anti-spoofing using texture analysis and blink detection
- **Multi-Registration**: Support for webcam, single image, and multiple image registration
- **Continuous Monitoring**: Periodic re-authentication during exam sessions
- **Local Processing**: Complete offline operation with SQLite database
- **Comprehensive Logging**: Detailed audit trail of all authentication attempts

## System Requirements

### Minimum Requirements
- Python 3.10+
- 4GB RAM
- 2GB disk space
- USB webcam (720p minimum)
- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- 8GB RAM
- 5GB disk space (SSD preferred)
- USB 3.0 webcam (1080p)
- CUDA-compatible GPU (optional, for acceleration)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sammy-g-o/FYP-main.git
   cd FYP-main
   ```

2. **Install dependencies using Pipenv**:
   ```bash
   pip install pipenv
   pipenv install
   pipenv shell
   ```

3. **Download required models**:
   - The system will automatically download DeepFace models on first run
   - Ensure `./model/shape_predictor_68_face_landmarks.dat` is present for liveness detection

## Usage

### Student Registration

**Single Image Registration**:
```bash
python student_registration.py --single --student-id "S12345" --name "John Doe" --image "path/to/image.jpg"
```

**Multiple Image Registration**:
```bash
python student_registration.py --multiple --student-id "S12345" --name "John Doe" --folder "path/to/images/"
```

**Webcam Registration**:
```bash
python student_registration.py --webcam --student-id "S12345" --name "John Doe"
```

### Running the System

**Start the main system**:
```bash
python main.py
```

**System Controls**:
- Press `a` to authenticate current frame
- Press `r` to register new student
- Press `q` to quit

## System Architecture

The system consists of four main components:

1. **ExamProctorSystem**: Main orchestrator managing authentication workflow
2. **FaceRecognizer**: Handles face detection and recognition using Facenet
3. **LivenessDetector**: Implements anti-spoofing with texture analysis and blink detection
4. **DatabaseManager**: Manages SQLite database operations and logging

## Database Schema

- **students**: Student identification and registration data
- **face_embeddings**: Multiple 128-dimensional face embeddings per student
- **auth_logs**: Complete authentication attempt audit trail

## Performance

- **Face Recognition**: ~0.82 seconds average processing time
- **Liveness Detection**: ~19 seconds comprehensive analysis
- **Database Queries**: Sub-millisecond response times
- **Detection Success Rate**: 88.9% with quality images

## Security Features

- **Local Processing**: No external API calls or data transmission
- **Offline Operation**: Complete functionality without internet connection
- **Audit Trail**: Comprehensive logging of all system activities
- **Session Management**: UUID-based session tracking

## Development

### Project Structure
```
FYP-main/
├── main.py                     # Main system entry point
├── face_recognition_system.py  # Core system orchestrator
├── face_recognition_module.py  # Face recognition implementation
├── liveness_detection.py       # Anti-spoofing implementation
├── database_manager.py         # Database operations
├── student_registration.py     # Registration system
├── model/                      # Model files
├── debug_images/              # Debug output images
└── students.db               # SQLite database
```

### Testing
The system includes comprehensive testing and analysis tools:
- `performance_analysis.py`: Performance benchmarking
- `results_analysis.py`: System usage analysis
- `test_system.py`: Component testing
- `create_indexes.py`: Database optimization

## Contributing

This is a Final Year Project (FYP) for academic purposes. The system demonstrates advanced computer vision and machine learning techniques for exam proctoring applications.

## License

Academic project - please contact the author for usage permissions.

## Author

Developed as part of a Final Year Project on Intelligent Exam Proctoring Systems.

## Acknowledgments

- DeepFace library for face recognition capabilities
- Dlib for facial landmark detection
- OpenCV for computer vision operations
- SQLite for reliable local database management