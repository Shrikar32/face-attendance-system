import cv2
import sqlite3
from deepface import DeepFace
from datetime import datetime
import os
import threading

# Global variables for the background thread to communicate with the webcam
display_msg = "Scanning..."
is_recognizing = False

def mark_attendance(roll_number):
    # SQLite connection is created per-thread, so it is safe
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM students WHERE roll_number=?", (roll_number,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return "Unknown Student"
        
    student_id, name = student
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    try:
        cursor.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
                       (student_id, today, current_time, "Present"))
        conn.commit()
        msg = f"Attendance Marked: {name}"
    except sqlite3.IntegrityError:
        msg = f"Already Marked: {name}"
        
    conn.close()
    return msg

def recognize_face_background(frame_path):
    global display_msg, is_recognizing
    try:
        # Using retinaface since we already downloaded it!
        dfs = DeepFace.find(img_path=frame_path, db_path="data/faces", detector_backend="retinaface", enforce_detection=False, silent=True)
        if len(dfs) > 0 and not dfs[0].empty:
            matched_file = dfs[0].iloc[0]['identity'].replace("\\", "/")
            filename = matched_file.split("/")[-1]
            roll_number = filename.split(".")[0]
            display_msg = mark_attendance(roll_number)
        else:
            display_msg = "Scanning..."
    except Exception as e:
        print(f"DeepFace Background Error: {e}")
        display_msg = "Scanning..."
    finally:
        # Unlock the thread so it can scan the next frame
        is_recognizing = False

def start_recognition():
    global display_msg, is_recognizing
    print("\n--- STARTING ATTENDANCE SYSTEM ---")
    print("Press 'q' to QUIT.")
    
    os.makedirs("data", exist_ok=True)
    temp_path = "data/temp.jpg"
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Draw status text on screen
        cv2.putText(frame, display_msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Attendance Camera", frame)
        
        # If the AI is not currently busy, send it a new frame to process
        if not is_recognizing:
            cv2.imwrite(temp_path, frame)
            is_recognizing = True
            threading.Thread(target=recognize_face_background, args=(temp_path,)).start()
                
        # Fast UI refresh
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_recognition()