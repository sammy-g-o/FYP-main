# Slide: Project Methodology

---

### **System Architecture & Design**

*   **Modular Design**: The system is built on a modular architecture to ensure scalability and maintainability.
    *   **Core Components**: `main.py` (Orchestrator), `face_recognition_system.py` (Proctoring Logic), `database_manager.py` (Data Persistence).
    *   **Specialized Modules**: `face_recognition_module.py`, `liveness_detection.py`, `alert_manager.py`.
*   **Data Storage**: A **SQLite** database (`students.db`) is used to store student profiles and facial embeddings.

---

### **Core Technologies**

*   **Computer Vision**: **OpenCV** for image processing and **dlib** for facial landmark detection.
*   **Face Recognition**: **DeepFace** framework utilizing the **Facenet** model to generate 128-dimension facial embeddings.
*   **Numerical Operations**: **NumPy** for efficient manipulation of embedding vectors.

---

### **Authentication & Proctoring Pipeline**

A two-stage process ensures robust identity verification:

**1. Liveness Detection (Anti-Spoofing):**
*   **Passive Check**: Texture analysis using **Local Binary Patterns (LBP)** to distinguish live skin from a photo or screen.
*   **Active Challenge**: If the passive check is inconclusive, the system requires a blink, verified by calculating the **Eye Aspect Ratio (EAR)** in real-time.

**2. Face Recognition:**
*   **Embedding Generation**: The live camera feed is used to generate a 128-D facial embedding with the Facenet model.
*   **Embedding Comparison**: The live embedding is compared against the registered student's embedding using **Cosine Similarity**.
*   **Verification**: A match is confirmed only if the similarity score is above a strict threshold of **0.85**.

---

### **Performance Evaluation**

*   **Framework**: A dedicated script (`comprehensive_performance.py`) was developed to measure system accuracy.
*   **Key Metrics**:
    *   **Classification**: Accuracy, Precision, Recall, F1-Score.
    *   **Biometric**: False Acceptance Rate (FAR), False Rejection Rate (FRR), and Equal Error Rate (EER).
