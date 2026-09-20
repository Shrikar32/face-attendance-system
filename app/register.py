import cv2
import os
import sqlite3

def register_student():
    print("\n--- NEW STUDENT REGISTRATION ---")
    roll_number = input("Enter PRN / Roll Number (e.g., 24070123103): ").strip()
    name = input("Enter Name: ").strip()

    if not roll_number or not name:
        print("Error: Roll Number and Name cannot be empty.")
        return

    # Check if student already exists
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
    if cursor.fetchone():
        print(f"Error: Student with Roll Number {roll_number} is already registered!")
        conn.close()
        return

    # Create folder for storing faces
    os.makedirs("data/faces", exist_ok=True)
    img_path = f"data/faces/{roll_number}.jpg"

    print("\nOpening webcam... Please look at the camera.")
    print("Press 'c' to CAPTURE your face.")
    print("Press 'q' to QUIT without saving.")

    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Is your webcam connected?")
            break

        # Draw a guide box
        height, width, _ = frame.shape
        start_point = (int(width/2 - 150), int(height/2 - 150))
        end_point = (int(width/2 + 150), int(height/2 + 150))
        cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
        cv2.putText(frame, "Align face inside box & press 'c'", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Face Registration", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            # Save the clean frame (without the green box) for better recognition
            clean_frame = frame.copy()
            cv2.imwrite(img_path, clean_frame)
            
            # Save to database
            cursor.execute("INSERT INTO students (roll_number, name, image_path) VALUES (?, ?, ?)", 
                           (roll_number, name, img_path))
            conn.commit()
            print(f"\nSUCCESS: {name} ({roll_number}) registered successfully!")
            break
        elif key == ord('q'):
            print("\nRegistration cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    register_student()