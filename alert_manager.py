import logging
from datetime import datetime

class ProctorAlerter:
    def __init__(self, log_file='proctor_alerts.log'):
        """
        Initializes the alerter to log critical events to a file.
        """
        self.log_file = log_file
        # Set up a dedicated logger for proctor alerts
        self.logger = logging.getLogger('ProctorAlerts')
        self.logger.setLevel(logging.INFO)
        
        # Prevent logs from propagating to the root logger
        self.logger.propagate = False
        
        # Create a file handler
        handler = logging.FileHandler(self.log_file)
        
        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add the handler to the logger if it doesn't have one already
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_alert(self, alert_type, student_id, session_id, score, message):
        """
        Logs a formatted alert to the proctor log file.

        Args:
            alert_type (str): The type of alert (e.g., 'LIVENESS_FAILURE', 'RECOGNITION_FAILURE').
            student_id (str): The ID of the student involved.
            session_id (str): The current exam session ID.
            score (float): The relevant score (liveness or confidence).
            message (str): A descriptive message about the alert.
        """
        log_message = (
            f"Type: {alert_type}, "
            f"StudentID: {student_id or 'N/A'}, "
            f"SessionID: {session_id or 'N/A'}, "
            f"Score: {score:.4f}, "
            f"Details: {message}"
        )
        self.logger.warning(log_message)
        print(f"ALERT LOGGED: {log_message}")
