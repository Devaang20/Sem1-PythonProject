import mysql.connector
import csv

#---------Pause Function---------
def pause():
    input("\nPress Enter to continue...")


# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # change if different
        password="manager",           # your MySQL password
        database="pythpro"
    )

# ---------- LOGIN SYSTEM ----------
def login():
    while True :   
        print("\n===== UNIVERSITY EXAM PORTAL LOGIN =====")
        print("1. Student Login")
        print("2. Admin Login")
        choice = input("Enter choice: ")
        
        if choice == '1':
            reg_no = input("Enter Registration No: ")
            password = input("Enter Password: ")
            conn = connect_db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM student WHERE reg_no=%s AND password=%s", (reg_no, password))
            student = cur.fetchone()
            conn.close()

            if student:
                print(f"\nWelcome, {student['name']}!")
                student_menu(student)
            else:
                print("Invalid registration number or password.")

        elif choice == '2':
            username = input("Enter Admin Username: ")
            password = input("Enter Admin Password: ")
            if username == "admin" and password == "admin123":
                print("\nWelcome, Admin!")
                admin_menu()
            else:
                print("Invalid admin credentials.")
        else:
            print("Invalid choice. Try again.")
            

# ---------- CHANGE PASSWORD ----------
def change_password(mode, reg_no=None):
    conn = connect_db()
    cur = conn.cursor()
    if mode == "student":
        print("Press ENTER to go back")
        current_pwd = input("Enter current password: ")
        if current_pwd=='':
            conn.close()
            return
        new_pwd = input("Enter new password: ")
        cur.execute("SELECT password FROM student WHERE reg_no=%s", (reg_no,))
        stored_pwd = cur.fetchone()
        if stored_pwd and stored_pwd[0] == current_pwd:
            cur.execute("UPDATE student SET password=%s WHERE reg_no=%s", (new_pwd, reg_no))
            conn.commit()
            print(" Password updated successfully.")
        else:
            print("Incorrect current password.")
    elif mode == "admin":
        current_pwd = input("Enter current admin password: ")
        if current_pwd == "admin123":
            print(" Admin password changed (demo only).")
        else:
            print(" Incorrect password.")
    conn.close()

# ---------- EXPORT DATA ----------
def export_data():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student")
    rows = cur.fetchall()
    conn.close()

    with open("students_export.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("Data exported successfully to 'students_export.csv'")
    pause()
# ---------- ANALYTICS SUMMARY ----------
def analytics_summary():
    conn = connect_db()
    cur = conn.cursor()

    print("\n===== ANALYTICS DASHBOARD =====")

    cur.execute("SELECT COUNT(*) FROM student")
    total = cur.fetchone()[0]
    print(f"Total Students: {total}")

    cur.execute("SELECT gender, COUNT(*) FROM student GROUP BY gender")
    print("\nGender Distribution:")
    for gender, count in cur.fetchall():
        print(f"  {gender}: {count}")

    cur.execute("SELECT coaching, COUNT(*) FROM student GROUP BY coaching")
    print("\nCoaching Type Distribution:")
    for ctype, count in cur.fetchall():
        print(f"  {ctype}: {count}")

    cur.execute("SELECT class_X_Percentage, COUNT(*) FROM student GROUP BY class_X_Percentage")
    print("\nClass X Performance:")
    for perf, count in cur.fetchall():
        print(f"  {perf}: {count}")

    cur.execute("SELECT class_XII_Percentage, COUNT(*) FROM student GROUP BY class_XII_Percentage")
    print("\nClass XII Performance:")
    for perf, count in cur.fetchall():
        print(f"  {perf}: {count}")


    conn.close()
    pause()

# ---------- ADMIN MENU ----------
def admin_menu():
    while True:
        print("\n===== ADMIN MENU =====")
        print("1. View All Students")
        print("2. Search Student")
        print("3. Add Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Export Data")
        print("7. Analytics Summary")
        print("8. Change Password")
        print("9. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_all_students()
        elif choice == '2':
            search_student()
        elif choice == '3':
            add_student()
        elif choice == '4':
            update_student()
        elif choice == '5':
            delete_student()
        elif choice == '6':
            export_data()
        elif choice == '7':
            analytics_summary()
        elif choice == '8':
            change_password("admin")
        elif choice == '9':
            print("Logging out...")
            break
        else:
            print("Invalid choice!")
#==============Mock Test Menu=============
import threading
import time
import sys

def exam(reg_no):
    conn = connect_db()
    cur = conn.cursor()
    questions = {
        # Physics
        "What is the unit of force?": (["Joule", "Newton", "Watt", "Pascal"], 2),
        "Speed of light in vacuum is:": (["3×10^8 m/s", "1.5×10^8 m/s", "3×10^6 m/s", "1×10^8 m/s"], 1),
        "Who gave the laws of motion?": (["Einstein", "Newton", "Galileo", "Bohr"], 2),
        "Which quantity is a vector?": (["Speed", "Time", "Force", "Mass"], 3),
        "SI unit of electric charge is:": (["Coulomb", "Ampere", "Volt", "Ohm"], 1),

        # Chemistry
        "Atomic number of oxygen is:": (["6", "7", "8", "9"], 3),
        "pH of neutral solution is:": (["0", "7", "14", "1"], 2),
        "Who proposed the atomic theory?": (["Rutherford", "Dalton", "Bohr", "Thomson"], 2),
        "HCl is a:": (["Base", "Acid", "Salt", "Indicator"], 2),
        "Chemical symbol of sodium is:": (["S", "Sn", "Na", "N"], 3),

        # Mathematics
        "Derivative of x² is:": (["x", "2x", "x²", "2"], 2),
        "Value of sin(90°) is:": (["0", "1", "0.5", "√3/2"], 2),
        "The roots of x² - 4 = 0 are:": (["2, -2", "4, -4", "0, 4", "1, -1"], 1),
        "Area of a circle is:": (["πr²", "2πr", "πd²", "r²"], 1),
        "Integral of 1/x dx is:": (["x²/2", "1/x", "ln|x|", "e^x"], 3)
    }

    score = 0
    total_time = 30 * 60  # 30 minutes in seconds
    time_up = threading.Event()

    def timer():
        remaining = total_time
        while remaining > 0 and not time_up.is_set():
            mins, secs = divmod(remaining, 60)
            sys.stdout.write(f"\r⏳ Time Remaining: {mins:02d}:{secs:02d}  Ans: ")
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1
        if not time_up.is_set():
            time_up.set()
            print("\n\n⏰ Time's up! The exam has ended.")
            print(f"Your final score: {score} / {len(questions) * 4}")
            sys.exit()

    # Start timer thread
    threading.Thread(target=timer, daemon=True).start()
    print("\n")
    print("=== Welcome to the PCM Exam ===")
    print("You have 30 minutes to complete this test.\n")

    for q, (options, correct) in questions.items():
        if time_up.is_set():
            break
        print(f"\n{q}")
        for i, opt in enumerate(options, start=1):
            print(f"{i}. {opt}")
        try:
            ans = int(input("Your answer (1-4): "))
            if time_up.is_set():
                break
            if ans == correct:
                score += 4
            elif ans not in [1,2,3,4]:
                
                print("Invalid input! -1 mark deducted.\n")
                score -= 1
            else:
                score -= 1
        except ValueError:
            print("Invalid input! -1 mark deducted.\n")
            score -= 1

    time_up.set()
    print("\n Test completed.")
    print(f"Your final score: {score} / {len(questions) * 4}")

    
    # --- Update marks in database ---
    cur.execute("UPDATE student SET marks = %s WHERE reg_no = %s", (score, reg_no))
    conn.commit()
    conn.close()
    print(f"✅ Your score ({score}) has been saved successfully!")



# ---------- STUDENT MENU ----------
def student_menu(student):
    while True:
        print("\n===== STUDENT MENU =====")
        print("1. View Profile")
        print("2. Mock Test")
        print("3. Change Password")
        print("4. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            print("\n--- Your Profile ---")
            for key, value in student.items():
                print(f"{key}: {value}")
            pause()
        elif choice == '2':
            exam(student['reg_no'])
        elif choice == '3':
            change_password("student", student['reg_no'])
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice!")


#==========BASIC CRUD FUNCTIONS=========

#-------View All Students Function-------
def view_all_students():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student")
    rows = cur.fetchall()
    conn.close()

    print("\n--- All Students ---")
    if not rows:
        print("No student records found.")
    else:
        # Display column headers
        print(" | ".join(rows[0].keys()))
        print("-" * 100)
        # Display each student's data
        for r in rows:
            print(" | ".join(str(v) for v in r.values()))
    pause()

#-------Search Student Function-------
def search_student():
    reg_no = input("Enter reg_no or name to search: ")
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student WHERE reg_no LIKE %s OR name LIKE %s", (f"%{reg_no}%", f"%{reg_no}%"))
    rows = cur.fetchall()
    conn.close()
    if rows:
        for r in rows:
            print(r)
    else:
        print("No records found.")
    pause()
#-------Add Student Function-------
def add_student():
    conn = connect_db()
    cur = conn.cursor()
    reg_no = input("Reg No: ")
    name = input("Name: ")
    password = input("Password: ")
    domicile = input("Domicile: ")
    gender = input("Gender (male/female): ")
    caste = input("Caste: ")
    coaching = input("Coaching (NO/WA/OA): ")
    class_ten = input("Class X Board (SEBA/CBSE/OTHERS/AHSEC): ")
    class_twelve = input("Class XII Board (SEBA/CBSE/AHSEC/OTHERS): ")
    medium = input("Medium (ENGLISH/ASSAMESE/OTHERS): ")
    ten_perc = input("Class X Performance (Excellent/Good/Vg): ")
    twelve_perc = input("Class XII Performance (Excellent/Good/Vg): ")
    father = input("Father Occupation: ")
    mother = input("Mother Occupation: ")
    attempt = input("Attempt (ONE/TWO): ")

    cur.execute("""
        INSERT INTO student VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (reg_no, name, password, domicile, gender, caste, coaching,
          class_ten, class_twelve, medium, ten_perc, twelve_perc, father, mother, attempt))
    conn.commit()
    conn.close()
    print("Student added successfully.")
    pause()
#-------Update Student Function-------
def update_student():
    reg_no = input("Enter reg_no to update: ")
    field = input("Enter field name to update (e.g., domicile, caste, etc.): ")
    value = input(f"Enter new value for {field}: ")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE student SET {field}=%s WHERE reg_no=%s", (value, reg_no))
    conn.commit()
    conn.close()
    print("Record updated successfully.")
    pause()
#-------Delete Student Function-------
def delete_student():
    reg_no = input("Enter reg_no to delete: ")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM student WHERE reg_no=%s", (reg_no,))
    conn.commit()
    conn.close()
    print("Student deleted successfully.")
    pause()
#==============Support Menu==========
def support_menu():
    while True:
        print("\n--- Support ---")
        print("1. Contact Us")
        print("2. Feedback")
        print("3. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("Contact: support@universityexam.edu | +91 98765 43210")
            pause()
        elif choice == '2':
            
        #----------Feedback Analyser-------------------    
            # Feedback Sentiment Analyzer
            # Define positive and negative word lists
            positive_words = [
                "good", "great", "excellent", "amazing", "wonderful", "nice",
                "awesome", "fantastic", "love", "satisfied", "happy", "best",
                "perfect", "enjoyed", "superb", "positive"
            ]

            negative_words = [
                "bad", "poor", "terrible", "awful", "worst", "hate", "disappointed",
                "unsatisfied", "boring", "horrible", "negative", "slow",
                "problem", "issue", "dull", "waste"
            ]

            # Take feedback from the user
            feedback = input("Please enter your feedback: ").lower()

            # Split feedback into individual words
            words = feedback.split()

            # Check for positive or negative sentiment
            positive_found = any(word in positive_words for word in words)
            negative_found = any(word in negative_words for word in words)

            # Give response
            if positive_found and not negative_found:
                print("😊 Thank you for your positive feedback! We're glad you liked it!")
            elif negative_found and not positive_found:
                print("😔 We're sorry to hear that. We’ll work to improve our service.")
            elif positive_found and negative_found:
                print("😐 Thanks for the balanced feedback! We'll improve while keeping the good parts.")
            else:
                print("🙂 Thanks for your feedback! We'll take it into consideration.")

            print("Thank you for your valuable feedback!")
            pause()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")
#====================================
#-----------Resources Menu-------------
def resources_menu():
    while True:
        print("\n--- Resources ---")
        print("1. Study Materials")
        print("2. Previous Year Papers")
        print("3. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("Access study materials at:\n \n Physics: https://byjus.com/physics/ \n Chemistry: https://byjus.com/chemistry/ \n Maths: https://byjus.com/maths/")
            pause()
        elif choice == '2':
            print("Access previous year papers at: \n PYQ: https://www.scribd.com/document/487883485/X-PRACTICE-PAPER-PCM-pdf")
            pause()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")


# ---------- LOGIN SYSTEM ----------
def login():
    while True:    
        print("\n===== UNIVERSITY EXAM PORTAL LOGIN =====")
        print("1. Student Login")
        print("2. Admin Login")
        print("3. Back to Main Menu")
        choice = input("Enter choice: ")

        if choice == '1':
            while True:   
                print("Press ENTER to go back to Login") 
                reg_no = input("Enter Registration No: ")
                if reg_no=='':
                    break
                password = input("Enter Password: ")
                conn = connect_db()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM student WHERE reg_no=%s AND password=%s", (reg_no, password))
                student = cur.fetchone()
                conn.close()

                if student:
                    print(f"\nWelcome, {student['name']}!")
                    student_menu(student)
                    break
                else:
                    print("Invalid registration number or password.")
        elif choice == '2':
            while True:
                print("Press ENTER to go back to Login")
                username = input("Enter Admin Username: ")
                if username=='':
                    break
                password = input("Enter Admin Password: ")
                if username == "admin" and password == "admin123":
                    print("\nWelcome, Admin!")
                    admin_menu()
                    break
                else:
                    print("Invalid admin credentials.")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")



# ========== MAIN MENU ==========
def main_menu():
    while True:
        print("\n========== UNIVERSITY PORTAL ==========")
        print("1. Login")
        print("2. Support")
        print("3. Resources")
        print("4. Exit")
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            login()
        elif choice == '2':
            support_menu()
        elif choice == '3':
            resources_menu()   
        elif choice == '4':
            print("Thank you for using the University Exam Portal. Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

# Run the portal
main_menu()