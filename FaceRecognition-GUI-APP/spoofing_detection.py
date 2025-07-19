import cv2
import numpy as np

class SpoofingDetector:
    def __init__(self):
        # Parameters for spoofing detection
        self.reflection_threshold = 0.2  # Threshold for reflection detection
        self.texture_threshold = 25      # Threshold for texture analysis
        self.face_area_min = 5000        # Minimum face area to consider valid
        
    def detect_spoofing(self, frame):
        """
        Detect potential spoofing attempts using reflection analysis and texture analysis
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (is_spoofing, confidence, analysis_image)
                   is_spoofing: True if spoofing detected
                   confidence: Confidence level (0-100)
                   analysis_image: Frame with detection annotations
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Create analysis image
        analysis_img = frame.copy()
        
        # 1. Reflection Analysis
        # Calculate reflection by looking for bright spots
        _, bright_spots = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
        reflection_area = cv2.countNonZero(bright_spots)
        total_area = gray.size
        reflection_ratio = reflection_area / total_area
        
        # 2. Texture Analysis
        # Use Laplacian variance to measure texture quality
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = np.var(laplacian)
        
        # 3. Face Area Check
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return True, 100, analysis_img  # No face detected - likely spoofing
        
        (x, y, w, h) = faces[0]
        face_area = w * h
        
        # Draw detection areas on analysis image
        cv2.rectangle(analysis_img, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(analysis_img, f"Reflection: {reflection_ratio:.2f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(analysis_img, f"Texture: {texture_score:.1f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Decision logic
        is_spoofing = False
        confidence = 0
        
        # High reflection ratio indicates possible photo with glass/reflection
        if reflection_ratio > self.reflection_threshold:
            is_spoofing = True
            confidence += 40
            cv2.putText(analysis_img, "High Reflection!", (x, y-40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Low texture score indicates possible printed photo
        if texture_score < self.texture_threshold:
            is_spoofing = True
            confidence += 40
            cv2.putText(analysis_img, "Low Texture!", (x, y-70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Small face area might indicate photo held at distance
        if face_area < self.face_area_min:
            is_spoofing = True
            confidence += 20
            cv2.putText(analysis_img, "Small Face Area!", (x, y-100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Cap confidence at 100
        confidence = min(100, confidence)
        
        return is_spoofing, confidence, analysis_img