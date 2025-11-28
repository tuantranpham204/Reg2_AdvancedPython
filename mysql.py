import tkinter as tk
import mysql.connector as connector

print("Setting up database...")
setup_conn = connector.connect(
    user='root',
    password='12345678',
    host='localhost',
    port=3306
)
setup_cursor = setup_conn.cursor()
try:
    setup_cursor.execute("DROP DATABASE IF EXISTS students_db")
    setup_cursor.execute("CREATE DATABASE IF NOT EXISTS students_db")
    setup_conn.commit()
    print("Database 'students_db' created/reset.")
finally:
    setup_cursor.close()
    setup_conn.close()

conn = connector.connect(
    user='root',
    password='12345678',
    host='localhost',
    port=3306,
    database='students_db'
)

def initialize():
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
            
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    city VARCHAR(100) NOT NULL
                )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                    course_id INT PRIMARY KEY,
                    course_name VARCHAR(100) NOT NULL,
                    credits INT NOT NULL
                )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INT PRIMARY KEY,
                    course_id INT NOT NULL,
                    student_id INT NOT NULL,
                    grade DECIMAL NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
                )
            """)
        conn.commit()
    except Exception as e:
        print(e)

def insert_students():
    students = [
        (1, 'Nguyen Van A', 21, 'Ha Noi'),
        (2, 'Tran Thi B', 19, 'TP HCM'),
        (3, 'Le Van C', 22, 'Da Nang'),
        (4, 'Pham Minh D', 20, 'Can Tho'),
        (5, 'Hoang Thi E', 23, 'Hue'),
    ]

    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "INSERT INTO students(student_id, name, age, city) VALUES (%s, %s, %s, %s)"
            cursor.executemany(query, students)
            conn.commit()
            return True
    except Exception as e:
        print(e)
        return False

def insert_courses():
    courses = [
        (201, 'Toan Cao Cap', 3),
        (202, 'Vat Ly Dai Cuong', 4),
        (203, 'Tin Hoc Co Ban', 3),
        (204, 'Hoa Hoc Dai Cuong', 2),
        (205, 'Van Hoc Viet Nam', 2),
    ]
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "INSERT INTO courses(course_id, course_name, credits) VALUES (%s ,%s, %s)"
            cursor.executemany(query, courses)
            conn.commit()
            return True
    except Exception as e:
        print(e)
        return False

def insert_enrollments():
    enrollments = [
        (1, 1, 201, 8.5),
        (2, 1, 202, 7),
        (3, 2, 203, 6.5),
        (4, 3, 201, 9),
        (5, 3, 204, 7.5),
        (6, 4, 205, 8),
        (7, 5, 203, 7.5),
        (8, 5, 202, 8),
        (9, 4, 204, 6),
        (10, 2, 205, 7),
    ]
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "INSERT INTO enrollments(enrollment_id, student_id, course_id, grade) VALUES (%s, %s, %s, %s)"
            cursor.executemany(query, enrollments)
            conn.commit()
            return True
    except Exception as e:
        print(e)
        return False

def select_courses_by_desc_credits():
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT course_name, credits FROM courses ORDER BY credits DESC LIMIT 5"
            cursor.execute(query)
            res = cursor.fetchall()
            return {
                'courses': res,
                'total credits': sum(course["credits"] for course in res),
            }
    except Exception as e:
        print(e)
        return

def student_number_per_course():
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT e.course_id, COUNT(s.student_id) AS total_students
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                GROUP BY e.course_id
                ORDER BY total_students DESC;
            """
            cursor.execute(query)
            res = cursor.fetchall()
            return {"number of student per courses": res}
    except Exception as e:
        print(e)
        return

def average_grade_per_course():
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT c.course_id, c.course_name, AVG(e.grade) AS average_grade 
                FROM enrollments e 
                JOIN courses c ON e.course_id = c.course_id
                GROUP BY c.course_id
                HAVING average_grade >= 7
            """
            cursor.execute(query)
            res = cursor.fetchall()
            for course in res:
                course["average_grade"] = float(course["average_grade"])
            return {"average grade per courses": res}
    except Exception as e:
        print(e)
        return

def get_all_students():
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM students"
            cursor.execute(query)
            res = cursor.fetchall()
            return {"students" : res}
    except Exception as e:
        print(e)
        return

def get_courses_from_student(student_id):
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = f"""
                SELECT c.course_name, c.credits, e.grade
                FROM enrollments e 
                JOIN courses c ON e.course_id = c.course_id 
                WHERE e.student_id = %s
            """
            cursor.execute(query, (student_id,))
            res = cursor.fetchall()
            for course in res:
                course["credits"] = float(course["credits"])
                course["grade"] = float(course["grade"])
            return {"courses" : res}
    except Exception as e:
        print(e)
        return

def get_courses_info_from_student(student_id):
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = f"""
                SELECT AVG(e.grade) as average_grade, SUM(c.credits) AS total_credits
                FROM enrollments e 
                JOIN courses c ON e.course_id = c.course_id
                GROUP BY e.student_id      
                HAVING e.student_id = %s
            """
            cursor.execute(query, (student_id,))
            course_info = cursor.fetchone()
            course_info["average_grade"] = float(course_info["average_grade"])
            course_info["total_credits"] = float(course_info["total_credits"])
            return {"course_info" : course_info}
    except Exception as e:
        print(e)
        return

class Application(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.widgets()
        self.columnconfigure(0, weight=1)  # Left side expands
        self.columnconfigure(1, weight=1)  # Right side expands
        self.rowconfigure(0, weight=1)  # Vertical expansion
        self.student_list = []
        self.course_list = []
        self.load_students()


    def widgets(self):
        self.fr_left = tk.Frame(self)
        self.fr_left.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.fr_left.columnconfigure(0, weight=1)  # Make content inside frame center/expand
        self.fr_left.rowconfigure(1, weight=1)  # Make Listbox expand vertically

        self.fr_right = tk.Frame(self)
        self.fr_right.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.fr_right.columnconfigure(0, weight=1)
        self.fr_right.rowconfigure(1, weight=1)

        self.lbl_students = tk.Label(self.fr_left, text="Danh sach sinh vien")
        self.lbl_students.grid(column=0, row=0, padx=10, pady=10)
        self.lst_students = tk.Listbox(self.fr_left, selectmode=tk.SINGLE, width=50)
        self.lst_students.grid(column=0, row=1, padx=10, pady=10, rowspan=5)

        self.lbl_courses = tk.Label(self.fr_right, text="Khoa hoc da dang ky")
        self.lbl_courses.grid(column=0, row=0, padx=10, pady=10)
        self.lst_courses = tk.Listbox(self.fr_right, selectmode=tk.SINGLE, width=50)
        self.lst_courses.grid(column=0, row=1, padx=10, pady=10, rowspan=3)
        self.lbl_total_credits = tk.Label(self.fr_right, text=self.text_total_credits())
        self.lbl_total_credits.grid(column=0, row=5, padx=10, pady=10)
        self.lbl_avg_grade = tk.Label(self.fr_right, text=self.text_avg_grade())
        self.lbl_avg_grade.grid(column=0, row=6, padx=10, pady=10)

        self.lst_students.bind('<<ListboxSelect>>', self.on_select)

    def text_total_credits(self, total_credits = 0.0):
        return f"Tong tin chi {total_credits}"
    def text_avg_grade(self, grade = 0.0):
        return f"Diem trung binh {grade}"

    def load_students(self):
        students = get_all_students()["students"]
        self.student_list = students
        for student in students:
            self.lst_students.insert(tk.END, f"{student['name']} - {student['city']}")



    def on_select(self, event):
        selection = self.lst_students.curselection()
        if not selection:
            return
        index = selection[0]
        student_id = self.student_list[index]["student_id"]
        self.course_list = get_courses_from_student(student_id)["courses"]
        course_info = get_courses_info_from_student(student_id)["course_info"]
        self.lst_courses.delete(0,tk.END)
        for course in self.course_list:
            self.lst_courses.insert(tk.END, f"{course['course_name']} - Tin chi: {course['credits']}, Diem {course['grade']}")
        self.lbl_total_credits.config(text=self.text_total_credits(total_credits=course_info["total_credits"]))
        self.lbl_avg_grade.config(text=self.text_avg_grade(grade=course_info["average_grade"]))


if __name__ == '__main__':
    initialize()
    print(insert_students())
    print(insert_courses())
    print(insert_enrollments())
    print(select_courses_by_desc_credits())
    print(student_number_per_course())
    print(average_grade_per_course())

    # print(get_all_students())
    # print(get_courses_from_student(1))
    print(get_courses_info_from_student(1))

    root = tk.Tk()
    root.geometry("700x400")
    app = Application(root)
    root.mainloop()
