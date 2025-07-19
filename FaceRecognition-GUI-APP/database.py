import sqlite3
import os
from hashlib import sha256
import cv2
import numpy as np
from datetime import datetime

class FaceRecognitionDB:
    def __init__(self, db_name="face_recognition.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_db()
        self.create_admin_account()
    
    def initialize_db(self):
        """Initialize database and create tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        # Enable foreign key constraints
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create face_images table (stores actual face images)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image_data BLOB NOT NULL,
                capture_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create classifiers table (stores trained models)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                classifier_data BLOB NOT NULL,
                train_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_count INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create login_history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def create_admin_account(self):
        """Create default admin account if it doesn't exist"""
        admin_username = "admin"
        admin_password = "admin123"  # In production, change this!
        
        if not self.user_exists(admin_username):
            password_hash = sha256(admin_password.encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
                (admin_username, password_hash)
            )
            self.conn.commit()
    
    # ========== User Management Methods ==========
    def add_user(self, username, password, is_admin=False):
        """Add a new user to the database"""
        if self.user_exists(username):
            return None
            
        password_hash = sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, password_hash, int(is_admin))
            )
            user_id = self.cursor.lastrowid
            self.conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def verify_user(self, username, password):
        """Verify user credentials and return user info if valid"""
        password_hash = sha256(password.encode()).hexdigest()
        self.cursor.execute(
            "SELECT id, is_admin FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = self.cursor.fetchone()
        if result:
            return {'id': result[0], 'is_admin': bool(result[1])}
        return None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        self.cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        self.conn.commit()
    
    def get_user(self, user_id):
        """Get user details by ID"""
        self.cursor.execute(
            "SELECT id, username, is_admin, date_created, last_login FROM users WHERE id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'is_admin': bool(result[2]),
                'date_created': result[3],
                'last_login': result[4]
            }
        return None
    
    def get_all_users(self):
        """Get all registered users"""
        self.cursor.execute(
            "SELECT id, username, is_admin, date_created, last_login FROM users ORDER BY username"
        )
        return [
            {
                'id': row[0],
                'username': row[1],
                'is_admin': bool(row[2]),
                'date_created': row[3],
                'last_login': row[4]
            } for row in self.cursor.fetchall()
        ]
    
    def user_exists(self, username):
        """Check if a username exists"""
        self.cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        return self.cursor.fetchone() is not None
    
    def delete_user(self, user_id):
        """Delete a user and all their associated data"""
        try:
            # Cascading deletes will handle face_images, classifiers, and login_history
            self.cursor.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False
    
    # ========== Face Image Management ==========
    def save_face_image(self, user_id, image):
        """Save a face image to the database"""
        # Convert image to JPEG bytes
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success:
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO face_images (user_id, image_data) VALUES (?, ?)",
                (user_id, encoded_image.tobytes())
            )
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False
    
    def get_face_images(self, user_id, limit=None):
        """Retrieve face images for a user"""
        query = "SELECT image_data, capture_time FROM face_images WHERE user_id = ? ORDER BY capture_time DESC"
        params = (user_id,)
        
        if limit:
            query += " LIMIT ?"
            params = (user_id, limit)
            
        self.cursor.execute(query, params)
        results = []
        for row in self.cursor.fetchall():
            img_data = np.frombuffer(row[0], dtype=np.uint8)
            img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            results.append({
                'image': img,
                'capture_time': row[1]
            })
        return results
    
    def get_face_image_count(self, user_id):
        """Get count of face images for a user"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM face_images WHERE user_id = ?",
            (user_id,)
        )
        return self.cursor.fetchone()[0]
    
    # ========== Classifier Management ==========
    def save_classifier(self, user_id, classifier, image_count):
        """Save trained classifier to database"""

        
        try:
            # Save classifier to a temporary file
            temp_filename = f"temp_classifier_{user_id}.yml"
            classifier.save(temp_filename)
            # Read the file data
            with open(temp_filename, 'rb') as f:
                classifier_bytes = f.read()

            # Delete the temporary file
            os.remove(temp_filename)

             # Delete existing classifier if it exists
            self.cursor.execute(
            "DELETE FROM classifiers WHERE user_id = ?",
            (user_id,)
            )

             # Insert new classifier
            self.cursor.execute(
                """INSERT INTO classifiers 
                (user_id, classifier_data, image_count) 
                VALUES (?, ?, ?)""",
                (user_id, classifier_bytes, image_count)
            )

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving classifier: {e}")
            return False
    
    def get_classifier(self, user_id):
        """Retrieve classifier for a user"""
        self.cursor.execute(
            "SELECT classifier_data FROM classifiers WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        if result:
            temp_filename = f"temp_classifier_{user_id}.yml"
            with open(temp_filename, 'wb') as f:
                f.write(result[0])

            # Load the classifier
            classifier = cv2.face.LBPHFaceRecognizer_create()
            classifier.read(temp_filename)

            # Delete the temporary file
            os.remove(temp_filename)

            return classifier
        return None
    
    def get_classifier_info(self, user_id):
        """Get classifier metadata"""
        self.cursor.execute(
            "SELECT train_time, image_count FROM classifiers WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return {
                'train_time': result[0],
                'image_count': result[1]
            }
        return None
    
    # ========== Login History ==========
    def log_login_attempt(self, user_id, success, ip_address=None, user_agent=None):
        """Record a login attempt"""
        self.cursor.execute(
            """INSERT INTO login_history 
               (user_id, success, ip_address, user_agent) 
               VALUES (?, ?, ?, ?)""",
            (user_id, success, ip_address, user_agent)
        )
        self.conn.commit()
        return True
    
    def get_login_history(self, user_id=None, limit=100):
        """Get login history for all users or a specific user"""
        query = """
            SELECT u.username, l.login_time, l.success, l.ip_address, l.user_agent 
            FROM login_history l
            JOIN users u ON l.user_id = u.id
        """
        params = ()
        
        if user_id:
            query += " WHERE l.user_id = ?"
            params = (user_id,)
            
        query += " ORDER BY l.login_time DESC LIMIT ?"
        params += (limit,)
        
        self.cursor.execute(query, params)
        return [
            {
                'username': row[0],
                'login_time': row[1],
                'success': bool(row[2]),
                'ip_address': row[3],
                'user_agent': row[4]
            } for row in self.cursor.fetchall()
        ]
    
    # ========== Admin Statistics ==========
    def get_system_stats(self):
        """Get system statistics for admin dashboard"""
        stats = {}
        
        # User counts
        self.cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        stats['admin_users'] = self.cursor.fetchone()[0]
        
        # Image counts
        self.cursor.execute("SELECT COUNT(*) FROM face_images")
        stats['total_images'] = self.cursor.fetchone()[0]
        
        # Login stats
        self.cursor.execute("SELECT COUNT(*) FROM login_history WHERE success = 1")
        stats['successful_logins'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM login_history WHERE success = 0")
        stats['failed_logins'] = self.cursor.fetchone()[0]
        
        # Recent activity
        stats['recent_logins'] = self.get_login_history(limit=5)
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        self.close()