import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from PIL import Image, ImageTk
import cv2
import numpy as np
from database import FaceRecognitionDB
from time import time
import os
from spoofing_detection import SpoofingDetector

class AdminPanel(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Admin Panel")
        self.db = db
        self.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)
        
        # Create tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        
        # Users tab
        self.users_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.users_tab, text='Users')
        
        # Login history tab
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text='Login History')
        
        # Stats tab
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text='Statistics')
        
        self.setup_users_tab()
        self.setup_history_tab()
        self.setup_stats_tab()
    
    def setup_users_tab(self):
        # Treeview for users
        self.users_tree = ttk.Treeview(self.users_tab, columns=('ID', 'Username', 'Admin', 'Created', 'Last Login'), show='headings')
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Username', text='Username')
        self.users_tree.heading('Admin', text='Admin')
        self.users_tree.heading('Created', text='Created')
        self.users_tree.heading('Last Login', text='Last Login')
        
        # Configure columns
        self.users_tree.column('ID', width=50, anchor='center')
        self.users_tree.column('Username', width=150)
        self.users_tree.column('Admin', width=80, anchor='center')
        self.users_tree.column('Created', width=150)
        self.users_tree.column('Last Login', width=150)
        
        self.users_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(self.users_tab)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(btn_frame, text="Refresh", command=self.load_users).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_user, bg='#ff9999').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Toggle Admin", command=self.toggle_admin).pack(side='left', padx=5)
        
        self.load_users()
    
    def setup_history_tab(self):
        # Treeview for login history
        self.history_tree = ttk.Treeview(self.history_tab, 
                                       columns=('Username', 'Time', 'Success', 'Spoofing', 'IP', 'Agent'), 
                                       show='headings')
        self.history_tree.heading('Username', text='Username')
        self.history_tree.heading('Time', text='Time')
        self.history_tree.heading('Success', text='Success')
        self.history_tree.heading('Spoofing', text='Spoofing')
        self.history_tree.heading('IP', text='IP Address')
        self.history_tree.heading('Agent', text='User Agent')
        
        # Configure columns
        self.history_tree.column('Username', width=150)
        self.history_tree.column('Time', width=150)
        self.history_tree.column('Success', width=80, anchor='center')
        self.history_tree.column('Spoofing', width=80, anchor='center')
        self.history_tree.column('IP', width=150)
        self.history_tree.column('Agent', width=300)
        
        self.history_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(self.history_tab)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(btn_frame, text="Refresh", command=self.load_history).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear History", command=self.clear_history, bg='#ff9999').pack(side='right', padx=5)
        
        self.load_history()
    
    def setup_stats_tab(self):
        # Stats display
        stats_frame = tk.Frame(self.stats_tab)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System stats
        tk.Label(stats_frame, text="System Statistics", font=('Helvetica', 14, 'bold')).pack(anchor='w')
        
        self.stats_text = tk.Text(stats_frame, height=10, wrap='word')
        self.stats_text.pack(fill='both', expand=True, pady=5)
        
        # User image counts
        tk.Label(stats_frame, text="User Image Counts", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(10,0))
        
        self.user_stats_tree = ttk.Treeview(stats_frame, columns=('Username', 'Image Count', 'Last Trained'), show='headings')
        self.user_stats_tree.heading('Username', text='Username')
        self.user_stats_tree.heading('Image Count', text='Image Count')
        self.user_stats_tree.heading('Last Trained', text='Last Trained')
        self.user_stats_tree.pack(fill='both', expand=True, pady=5)
        
        self.load_stats()
    
    def load_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        users = self.db.get_all_users()
        for user in users:
            self.users_tree.insert('', 'end', values=(
                user['id'],
                user['username'],
                'Yes' if user['is_admin'] else 'No',
                user['date_created'],
                user['last_login'] or 'Never'
            ))
    
    def load_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        history = self.db.get_login_history(limit=100)
        for record in history:
            self.history_tree.insert('', 'end', values=(
                record['username'],
                record['login_time'],
                'Yes' if record['success'] else 'No',
                'Yes' if record.get('spoofing_attempt', False) else 'No',
                record['ip_address'] or '',
                record['user_agent'] or ''
            ))
    
    def load_stats(self):
        # Load system stats
        stats = self.db.get_system_stats()
        stats_text = f"""
        Total Users: {stats['total_users']}
        Admin Users: {stats['admin_users']}
        Total Face Images: {stats['total_images']}
        Successful Logins: {stats['successful_logins']}
        Failed Logins: {stats['failed_logins']}
        Spoofing Attempts: {stats.get('spoofing_attempts', 0)}
        
        Recent Logins:
        """
        
        for login in stats['recent_logins']:
            status = "Success" if login['success'] else "Fail"
            if login.get('spoofing_attempt', False):
                status += " (Spoofing)"
            stats_text += f"\n{login['login_time']} - {login['username']} ({status})"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        
        # Load user image counts
        for item in self.user_stats_tree.get_children():
            self.user_stats_tree.delete(item)
            
        users = self.db.get_all_users()
        for user in users:
            classifier_info = self.db.get_classifier_info(user['id'])
            self.user_stats_tree.insert('', 'end', values=(
                user['username'],
                self.db.get_face_image_count(user['id']),
                classifier_info['train_time'] if classifier_info else 'Not trained'
            ))
    
    def delete_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        username = self.users_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete user '{username}' and all their data?"):
            if self.db.delete_user(user_id):
                messagebox.showinfo("Success", "User deleted successfully")
                self.load_users()
                self.load_stats()
            else:
                messagebox.showerror("Error", "Failed to delete user")
    
    def toggle_admin(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        username = self.users_tree.item(selected[0])['values'][1]
        current_status = self.users_tree.item(selected[0])['values'][2] == 'Yes'
        
        if username == 'admin':
            messagebox.showwarning("Warning", "Cannot modify the main admin account")
            return
            
        if messagebox.askyesno("Confirm", 
                             f"{'Remove' if current_status else 'Grant'} admin privileges for '{username}'?"):
            self.cursor = self.db.conn.cursor()
            self.cursor.execute(
                "UPDATE users SET is_admin = ? WHERE id = ?",
                (not current_status, user_id)
            )
            self.db.conn.commit()
            self.load_users()
    
    def clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all login history?"):
            self.cursor = self.db.conn.cursor()
            self.cursor.execute("DELETE FROM login_history")
            self.db.conn.commit()
            self.load_history()

class FaceRecognitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition System")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Initialize database
        self.db = FaceRecognitionDB()
        self.current_user = None
        self.spoofing_detector = SpoofingDetector()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        
        # Container for all pages
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Page dictionary
        self.pages = {}
        
        # Create all pages
        for PageClass in (StartPage, LoginPage, RegisterPage, CapturePage, TrainPage, RecognizePage):
            page_name = PageClass.__name__
            page = PageClass(parent=container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")
        
        self.show_page("StartPage")
    
    def show_page(self, page_name):
        """Show the specified page"""
        page = self.pages[page_name]
        page.tkraise()
        
        # Update admin button visibility
        if hasattr(page, 'update_admin_button'):
            page.update_admin_button()
    
    def open_admin_panel(self):
        """Open the admin panel"""
        if self.current_user and self.current_user.get('is_admin'):
            AdminPanel(self, self.db)
        else:
            messagebox.showerror("Access Denied", "Admin privileges required")
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Main content
        content = ttk.Frame(self)
        content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        ttk.Label(content, text="Face Recognition System", style='Title.TLabel').pack(pady=20)
        
        # Image display
        try:
            img = Image.open("homepagepic.png")
            img = img.resize((300, 300), Image.ANTIALIAS)
            self.render = ImageTk.PhotoImage(img)
            img_label = tk.Label(content, image=self.render)
            img_label.pack(pady=20)
        except Exception as e:
            print(f"Image error: {e}")
            tk.Label(content, text="Application Logo", font=("Arial", 24)).pack(pady=20)
        
        # Buttons frame
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Register", 
                  command=lambda: controller.show_page("RegisterPage")).pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Login", 
                  command=lambda: controller.show_page("LoginPage")).pack(side='left', padx=10)
        
        # Admin button (only shown for admin users)
        self.admin_btn = ttk.Button(content, text="Admin Panel", 
                                   command=controller.open_admin_panel)
        
        # Quit button
        ttk.Button(content, text="Quit", command=controller.destroy).pack(pady=10)
    
    def update_admin_button(self):
        """Show/hide admin button based on current user"""
        if self.controller.current_user and self.controller.current_user.get('is_admin'):
            self.admin_btn.pack(pady=10)
        else:
            self.admin_btn.pack_forget()

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Main form
        form = ttk.Frame(self)
        form.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Title
        ttk.Label(form, text="Login", style='Title.TLabel').grid(row=0, columnspan=2, pady=10)
        
        # Username
        ttk.Label(form, text="Username:").grid(row=1, column=0, sticky='e', pady=5)
        self.username = ttk.Entry(form)
        self.username.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        # Password
        ttk.Label(form, text="Password:").grid(row=2, column=0, sticky='e', pady=5)
        self.password = ttk.Entry(form, show="*")
        self.password.grid(row=2, column=1, pady=5, padx=5, sticky='ew')
        
        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Login", command=self.attempt_login).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Back", 
                  command=lambda: controller.show_page("StartPage")).pack(side='left', padx=10)
        
        # Configure column weights
        form.columnconfigure(1, weight=1)
    
    def attempt_login(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        # Verify credentials
        user_info = self.controller.db.verify_user(username, password)
        if not user_info:
            self.controller.db.log_login_attempt(
                self.controller.db.get_user_id(username), 
                False
            )
            messagebox.showerror("Error", "Invalid username or password!")
            return
        
        # Store current user info
        self.controller.current_user = user_info  
        
        # Then verify face matches with delay and spoofing detection
        if self.verify_face_with_delay(username, user_info['id']):
            self.controller.db.update_last_login(user_info['id'])
            self.controller.db.log_login_attempt(user_info['id'], True)
            messagebox.showinfo("Success", "Login successful!")
            self.controller.show_page("RecognizePage")
        else:
            self.controller.db.log_login_attempt(user_info['id'], False)
            messagebox.showerror("Error", "Face verification failed!")
    

    def verify_face_with_delay(self, username, user_id):
        """Face verification function with delay and spoofing detection"""
        classifier = self.controller.db.get_classifier(user_id)
        if not classifier:
            messagebox.showerror("Error", "No trained model found. Please register first.")
            return False
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        start_time = time()
        verified = False
        spoofing_detected = False
        verification_start_time = 0
        spoofing_start_time = 0
        
        # Timing parameters
        min_verification_time = 12  # Minimum seconds to show verification
        min_spoofing_time = 12      # Minimum seconds to show spoofing warning
        max_timeout = 30           # Maximum time to attempt verification
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            current_time = time()
            elapsed_time = current_time - start_time
            
            # Perform spoofing detection on the frame
            is_spoofing, spoofing_confidence, _ = self.controller.spoofing_detector.detect_spoofing(frame)
            
            if is_spoofing and not spoofing_detected:
                spoofing_detected = True
                spoofing_start_time = current_time
            
            # If spoofing was detected but now it's gone, reset
            if spoofing_detected and not is_spoofing:
                spoofing_detected = False
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                
                if spoofing_detected:
                    # Draw spoofing warning
                    cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 10)
                    cv2.putText(frame, "SPOOFING DETECTED!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "FAKE FACE", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    # Only proceed with verification if no spoofing detected
                    roi_gray = gray[y:y+h, x:x+w]
                    id, confidence = classifier.predict(roi_gray)
                    confidence = 100 - confidence
                    
                    if confidence > 60:  # Verification threshold
                        if not verified:
                            verification_start_time = current_time
                        verified = True
                        text = f'Hi: {username}'
                        color = (0, 255, 0)
                    else:
                        verified = False
                        text = "Unkown User"
                        color = (0, 0, 255)
                        
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    
                    # Add border color based on verification status
                    border_color = (0, 255, 0) if verified else (0, 0, 255)
                    cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), border_color, 10)
            
            # Show the frame
            cv2.imshow("Face Verification", frame)
            
            # Check conditions to end verification
            if spoofing_detected:
                # Require spoofing to persist for minimum time
                if (current_time - spoofing_start_time) >= min_spoofing_time:
                    break
            elif verified:
                # Require verification to persist for minimum time
                if (current_time - verification_start_time) >= min_verification_time:
                    break
                    
            # Timeout after max_timeout seconds
            if elapsed_time >= max_timeout:
                break
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if spoofing_detected:
            # Show spoofing warning for an additional 2 seconds before closing
            warning_end_time = time() + 2
            cap = cv2.VideoCapture(0)
            while time() < warning_end_time:
                ret, frame = cap.read()
                if ret:
                    cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 10)
                    cv2.putText(frame, "SPOOFING DETECTED!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow("Face Verification", frame)
                    cv2.waitKey(30)
            cap.release()
            cv2.destroyAllWindows()
            return False
        
        return verified

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Main form
        form = ttk.Frame(self)
        form.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Title
        ttk.Label(form, text="Register", style='Title.TLabel').grid(row=0, columnspan=2, pady=10)
        
        # Username
        ttk.Label(form, text="Username:").grid(row=1, column=0, sticky='e', pady=5)
        self.username = ttk.Entry(form)
        self.username.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        # Password
        ttk.Label(form, text="Password:").grid(row=2, column=0, sticky='e', pady=5)
        self.password = ttk.Entry(form, show="*")
        self.password.grid(row=2, column=1, pady=5, padx=5, sticky='ew')
        
        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Register", command=self.register_user).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Back", 
                  command=lambda: controller.show_page("StartPage")).pack(side='left', padx=10)
        
        # Configure column weights
        form.columnconfigure(1, weight=1)
    
    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        # Check if username exists
        if self.controller.db.user_exists(username):
            messagebox.showerror("Error", "Username already exists!")
            return
            
        # Add user to database
        user_id = self.controller.db.add_user(username, password)
        if not user_id:
            messagebox.showerror("Error", "Registration failed!")
            return
        
        # Store current user info
        self.controller.current_user = {'id': user_id, 'is_admin': False}
        
        # Proceed to face capture
        messagebox.showinfo("Success", "Account created! Now capture your face images.")
        self.controller.show_page("CapturePage")

class CapturePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Setup UI
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to capture images")
        
        # Main content
        content = ttk.Frame(self)
        content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        ttk.Label(content, text="Face Capture", style='Title.TLabel').pack(pady=10)
        
        # Status label
        ttk.Label(content, textvariable=self.status_var).pack(pady=10)
        
        # Button frame
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=20)
        
        self.capture_btn = ttk.Button(btn_frame, text="Start Capture", command=self.start_capture)
        self.capture_btn.pack(side='left', padx=10)
        
        self.train_btn = ttk.Button(btn_frame, text="Train Model", 
                                   command=lambda: controller.show_page("TrainPage"),
                                   state='disabled')
        self.train_btn.pack(side='left', padx=10)
        
        ttk.Button(content, text="Back", 
                  command=lambda: controller.show_page("StartPage")).pack(pady=10)
    
    def start_capture(self):
        self.status_var.set("Starting face capture...")
        self.update()
        
        user_id = self.controller.current_user['id']
        num_images = 300  # Target number of images
        
        # Start capture process
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        count = 0
        
        while count < num_images:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                face_img = frame[y:y+h, x:x+w]
                
                # Save to database
                if self.controller.db.save_face_image(user_id, face_img):
                    count += 1
                    self.status_var.set(f"Captured {count}/{num_images} images")
                    self.update()
                    cv2.putText(frame, f"Captured: {count}/{num_images}", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow("Face Capture", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if count >= 50:  # Minimum number of images to enable training
            self.train_btn.config(state='normal')
        
        self.status_var.set(f"Capture complete. {count} images captured.")

class TrainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Setup UI
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to train model")
        
        # Main content
        content = ttk.Frame(self)
        content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        ttk.Label(content, text="Train Model", style='Title.TLabel').pack(pady=10)
        
        # Status label
        ttk.Label(content, textvariable=self.status_var).pack(pady=10)
        
        # Button frame
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Train Now", command=self.train_model).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Back", 
                  command=lambda: controller.show_page("StartPage")).pack(side='left', padx=10)
        
        ttk.Button(content, text="Continue to Recognition", 
                  command=lambda: controller.show_page("RecognizePage")).pack(pady=10)
    
    def train_model(self):
        self.status_var.set("Training model...")
        self.update()
        
        user_id = self.controller.current_user['id']
        image_count = self.controller.db.get_face_image_count(user_id)
        
        if image_count < 50:
            messagebox.showerror("Error", "Need at least 50 images to train!")
            self.status_var.set("Training failed - not enough images")
            return
        
        # Get face images from database
        face_images = self.controller.db.get_face_images(user_id)
        if not face_images:
            messagebox.showerror("Error", "No face images found!")
            self.status_var.set("Training failed - no images")
            return
        
        # Prepare training data
        faces = []
        ids = []
        
        for img_data in face_images:
            gray = cv2.cvtColor(img_data['image'], cv2.COLOR_BGR2GRAY)
            faces.append(gray)
            ids.append(0)  # All images belong to user_id 0 (the current user)
        
        ids = np.array(ids)
        
        # Train the classifier
        try:
            classifier = cv2.face.LBPHFaceRecognizer_create()
            classifier.train(faces, ids)
            
            # Save to database
            if self.controller.db.save_classifier(user_id, classifier, image_count):
                self.status_var.set("Training completed successfully!")
                messagebox.showinfo("Success", "Model trained successfully!")
            else:
                self.status_var.set("Training failed - database error")
                messagebox.showerror("Error", "Failed to save classifier")
        except Exception as e:
            self.status_var.set(f"Training failed - {str(e)}")
            messagebox.showerror("Error", f"Training failed: {str(e)}")

class RecognizePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style='TFrame')
        
        # Main content
        content = ttk.Frame(self)
        content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        ttk.Label(content, text="Face Recognition", style='Title.TLabel').pack(pady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start recognition")
        ttk.Label(content, textvariable=self.status_var).pack(pady=10)
        
        # Button frame
        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Start Recognition", command=self.start_recognition).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Back", 
                  command=lambda: controller.show_page("StartPage")).pack(side='left', padx=10)
    
    def start_recognition(self):
        user_id = self.controller.current_user['id']
        classifier = self.controller.db.get_classifier(user_id)
        
        if not classifier:
            messagebox.showerror("Error", "No trained model found. Please train first.")
            return
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        start_time = time()
        recognized = False
        confidence_level = 0
        last_face_time = time()
        spoofing_detected = False
        spoofing_start_time = 0
        
        # Minimum durations
        min_recognition_time = 3  # seconds to show recognition
        min_spoofing_time = 3     # seconds to show spoofing warning
        max_timeout = 30          # total timeout
        
        self.status_var.set("Looking for face...")
        self.update()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            current_time = time()
            elapsed_time = current_time - start_time
            
            # Perform spoofing detection on the frame
            spoofing_result, spoofing_confidence, spoofing_frame = self.controller.spoofing_detector.detect_spoofing(frame)
            
            if len(faces) > 0:
                last_face_time = current_time
                (x, y, w, h) = faces[0]
                roi_gray = gray[y:y+h, x:x+w]
                
                # Track when spoofing is first detected
                if spoofing_result and not spoofing_detected:
                    spoofing_detected = True
                    spoofing_start_time = current_time
                
                # If spoofing was detected but now it's gone, reset
                if spoofing_detected and not spoofing_result:
                    spoofing_detected = False
                
                # Only proceed with recognition if no spoofing detected for at least 1 second
                if not spoofing_detected or (current_time - spoofing_start_time < 1):
                    try:
                        id, confidence = classifier.predict(roi_gray)
                        confidence_level = 100 - confidence
                        
                        if confidence_level > 50:  # Recognition threshold
                            if not recognized:
                                recognition_start_time = current_time
                            recognized = True
                            text = f'Recognized'
                            color = (0, 255, 0)
                            #self.status_var.set(f"Recognized! Confidence: {confidence_level:.1f}%")
                        else:
                            recognized = False
                            text = "Unknown User"
                            color = (0, 0, 255)
                            self.status_var.set("Verification failed")
                        
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        
                        # Add additional visual feedback
                        if recognized:
                            # Draw a green border around the entire frame when recognized
                            cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 255, 0), 10)
                        else:
                            # Draw a red border when not recognized
                            cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 10)
                        
                    except Exception as e:
                        print(f"Recognition error: {e}")
                        recognized = False
                else:
                    # Spoofing detected for more than 1 second - show warning
                    recognized = False
                    self.status_var.set(f"Spoofing detected!")
                    
                    # Draw spoofing warning on frame
                    cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 10)
                    cv2.putText(frame, "SPOOFING ATTACK DETECTED!", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    
                    # Draw the face rectangle in red
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, f"FAKE FACE", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                # No face detected
                if current_time - last_face_time > 2:  # 2 seconds without face
                    self.status_var.set("No face detected")
                recognized = False
                spoofing_detected = False
            
            # Show the frame
            cv2.imshow("Face Recognition", frame)
            self.update()
            
            # Check conditions to end recognition
            if recognized and (current_time - recognition_start_time) >= min_recognition_time:
                break
                
            if spoofing_detected and (current_time - spoofing_start_time) >= min_spoofing_time:
                break
                
            # Timeout after max_timeout seconds
            if elapsed_time >= max_timeout:
                break
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if spoofing_detected:
            # Show spoofing warning for an additional 2 seconds before closing
            warning_end_time = time() + 2
            cap = cv2.VideoCapture(0)
            while time() < warning_end_time:
                ret, frame = cap.read()
                if ret:
                    cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 10)
                    cv2.putText(frame, "SPOOFING ATTACK DETECTED!", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow("Face Recognition", frame)
                    cv2.waitKey(30)
            cap.release()
            cv2.destroyAllWindows()
            
            messagebox.showerror("Security Alert", "Spoofing attack detected! Photo/video presentation detected.")
            self.controller.db.log_spoofing_attempt(user_id)
        elif recognized:
            messagebox.showinfo("Success", f"Face recognized successfully!")
        else:
            messagebox.showinfo("Result", "Face not recognized or verification failed")

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.mainloop()