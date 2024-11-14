from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from MySQLdb.cursors import DictCursor
import random
import string
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'dance'

mysql = MySQL(app)

# Home Page Route
@app.route('/')
def home():
    return render_template('home.html')
#----------------------STUDENT LOGIN-------------------------------------------------------------------------
# Student Login Route
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Student WHERE StudentID = %s AND Password = %s', (student_id, password))
        student = cursor.fetchone()
        if student:
            session['loggedin'] = True
            session['StudentID'] = student['StudentID']
            return redirect(url_for('student_dashboard'))
    return render_template('student_login.html')

@app.route('/student_dashboard')
def student_dashboard():
    flash_message = session.pop('flash_message', None)
    if 'loggedin' in session and 'StudentID' in session:
        student_id = session['StudentID']
        
        # Fetch student details (excluding password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT StudentID, First_Name, Last_Name, Email, Phone
            FROM Student
            WHERE StudentID = %s
        ''', (student_id,))
        student_details = cursor.fetchone()
        
        # Fetch emergency contact details
        cursor.execute('''
            SELECT Emergency_Contact
            FROM Student_EmergencyContact
            WHERE StudentID = %s
        ''', (student_id,))
        emergency_contacts = cursor.fetchall()
        
        # Fetch enrolled classes and prerequisite details
        cursor.execute('''
            SELECT c.ClassID, c.RoomNumber, c.Start_Time, c.End_Time, 
                   c.StudentCapacity, c.Enrollment_Status, c.InstructorID,
                   cp.PrereqID  
            FROM Class c
            JOIN Enrolls_In_R e ON c.ClassID = e.ClassID
            LEFT JOIN ClassPrereq cp ON c.ClassID = cp.ClassID
            WHERE e.StudentID = %s
        ''', (student_id,))
        enrolled_classes = cursor.fetchall()

        return render_template(
            'student_dashboard.html',
            student=student_details,
            emergency_contacts=emergency_contacts,
            classes=enrolled_classes,
            flash_message=flash_message
        )
    else:
        return redirect(url_for('student_login'))


    
@app.route('/edit_student_details', methods=['GET', 'POST'])
def edit_student_details():
    if 'loggedin' in session and 'StudentID' in session:
        student_id = session['StudentID']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Retrieve form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            contact_numbers = request.form.getlist('contact_number')

            # Update student details
            cursor.execute(''' 
                UPDATE Student
                SET First_Name = %s, Last_Name = %s, Email = %s, Phone = %s
                WHERE StudentID = %s
            ''', (first_name, last_name, email, phone, student_id))

            # Update emergency contacts
            cursor.execute('DELETE FROM Student_EmergencyContact WHERE StudentID = %s', (student_id,))
            for contact in contact_numbers:
                cursor.execute(''' 
                    INSERT INTO Student_EmergencyContact (StudentID, Emergency_Contact)
                    VALUES (%s, %s)
                ''', (student_id, contact))

            # Check for new class enrollment
            class_id = request.form.get('class_id')
            if class_id:
                try:
                    # Call stored procedure to check prerequisites and enroll the student
                    cursor.callproc('EnrollStudent', (student_id, class_id, datetime.date.today()))

                    # Retrieve the class fee from the Class table
                    cursor.execute(''' 
                        SELECT Fee FROM Class WHERE ClassID = %s
                    ''', (class_id,))
                    class_fee = cursor.fetchone()['Fee']

                    # Insert a new payment entry for the enrolled class
                    cursor.execute(''' 
                        INSERT INTO Payment (StudentID, ClassID, Amount, PaymentDate)
                        VALUES (%s, %s, %s, %s)
                    ''', (student_id, class_id, class_fee, datetime.date.today()))

                    # Flash success message
                    session['flash_message'] = f'Enrolled in class {class_id} successfully.'

                except MySQLdb._exceptions.OperationalError as e:
                    # Flash error message in case of failure
                    session['flash_message'] = f'Error enrolling in class: {e}'

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('student_dashboard'))

        # Fetch current student details and contact numbers
        cursor.execute('SELECT First_Name, Last_Name, Email, Phone FROM Student WHERE StudentID = %s', (student_id,))
        student_details = cursor.fetchone()

        cursor.execute('SELECT Emergency_Contact FROM Student_EmergencyContact WHERE StudentID = %s', (student_id,))
        contact_numbers = [contact['Emergency_Contact'] for contact in cursor.fetchall()]

        # Fetch completed classes
        cursor.execute('SELECT ClassID FROM Enrolls_In_R WHERE StudentID = %s', (student_id,))
        completed_classes = cursor.fetchall()

        # Fetch available classes
        cursor.execute('SELECT ClassID FROM Class')
        available_classes = cursor.fetchall()

        return render_template(
            'edit_student_details.html',
            student=student_details,
            contact_numbers=contact_numbers,
            available_classes=available_classes,
            completed_classes=completed_classes
        )
    else:
        return redirect(url_for('student_login'))


    
@app.route('/view_payment')
def view_payment():
    if 'loggedin' in session and 'StudentID' in session:
        student_id = session['StudentID']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch total payments using your MySQL function
        cursor.execute('SELECT GetTotalPayments(%s) AS TotalAmount', (student_id,))
        result = cursor.fetchone()
        total_amount = result['TotalAmount'] if result else 0
        
        return render_template('payment.html', total_amount=total_amount)
    else:
        return redirect(url_for('student_login'))


    
#---------------------------------------------INSTRUCTOR LOGIN ------------------------------------------------

@app.route('/instructor_login', methods=['GET', 'POST'])
def instructor_login():
    if request.method == 'POST':
        instructor_id = request.form['instructor_id']
        password = request.form['password']
        
        # Query database for instructor credentials
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Instructor WHERE InstructorID = %s AND Password = %s', (instructor_id, password))
        instructor = cursor.fetchone()
        
        if instructor:
            session['loggedin'] = True
            session['instructor_id'] = instructor['InstructorID']
            #flash('Login Successful!', 'success')
            return redirect(url_for('instructor_dashboard'))
    
    return render_template('instructor_login.html')

# Instructor Dashboard Route
@app.route('/instructor_dashboard')
def instructor_dashboard():
    if 'loggedin' in session and 'instructor_id' in session:
        instructor_id = session['instructor_id']
        
        # Fetch instructor details (excluding password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT InstructorID, First_Name, Last_Name, Email
            FROM Instructor
            WHERE InstructorID = %s
        ''', (instructor_id,))
        instructor_details = cursor.fetchone()
        
        # Fetch contact numbers for the instructor
        cursor.execute('''
            SELECT Contact_number
            FROM Instructor_ContactNumber
            WHERE InstructorID = %s
        ''', (instructor_id,))
        contact_numbers = cursor.fetchall()
        
        # Fetch classes taught by the instructor
        cursor.execute('''
            SELECT ClassID, RoomNumber, Start_Time, End_Time, StudentCapacity, Enrollment_Status
            FROM Class
            WHERE InstructorID = %s
        ''', (instructor_id,))
        classes = cursor.fetchall()
        
        # Fetch details of students enrolled in these classes
        enrolled_students = {}
        for class_info in classes:
            cursor.execute('''
                SELECT s.StudentID, s.First_Name, s.Last_Name, s.Email, s.Phone
                FROM Enrolls_In_R e
                JOIN Student s ON e.StudentID = s.StudentID
                WHERE e.ClassID = %s
            ''', (class_info['ClassID'],))
            enrolled_students[class_info['ClassID']] = cursor.fetchall()
        
        return render_template(
            'instructor_dashboard.html',
            instructor=instructor_details,
            contact_numbers=contact_numbers,
            classes=classes,
            enrolled_students=enrolled_students
        )
    else:
        return redirect(url_for('instructor_login'))
    
@app.route('/edit_instructor_details', methods=['GET', 'POST'])
def edit_instructor_details():
    if 'loggedin' in session and 'instructor_id' in session:
        instructor_id = session['instructor_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Update the instructor's details
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            contact_numbers = request.form.getlist('contact_number')  # Get all contact numbers

            # Update Instructor table
            cursor.execute('''
                UPDATE Instructor
                SET First_Name = %s, Last_Name = %s, Email = %s
                WHERE InstructorID = %s
            ''', (first_name, last_name, email, instructor_id))

            # Delete existing contact numbers
            cursor.execute('DELETE FROM Instructor_ContactNumber WHERE InstructorID = %s', (instructor_id,))

            # Insert updated contact numbers
            for contact in contact_numbers:
                cursor.execute('''
                    INSERT INTO Instructor_ContactNumber (InstructorID, Contact_number)
                    VALUES (%s, %s)
                ''', (instructor_id, contact))

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('instructor_dashboard'))

        # Fetch current instructor details and contact numbers
        cursor.execute('''
            SELECT First_Name, Last_Name, Email
            FROM Instructor
            WHERE InstructorID = %s
        ''', (instructor_id,))
        instructor_details = cursor.fetchone()

        cursor.execute('''
            SELECT Contact_number
            FROM Instructor_ContactNumber
            WHERE InstructorID = %s
        ''', (instructor_id,))
        contact_numbers = [contact['Contact_number'] for contact in cursor.fetchall()]

        return render_template(
            'edit_instructor_details.html',
            instructor=instructor_details,
            contact_numbers=contact_numbers
        )
    else:
        return redirect(url_for('instructor_login'))

    
#------------------------------------------ADMINISTRATOR LOGIN-------------------------------------------------

@app.route('/administrator_login', methods=['GET', 'POST'])
def administrator_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Administrator WHERE AdminID = %s AND Password = %s', (admin_id, password))
        admin = cursor.fetchone()
        if admin:
            session['loggedin'] = True
            session['AdminID'] = admin['AdminID']
            #flash('Login Successful!', 'success')
            return redirect(url_for('administrator_dashboard'))
    return render_template('administrator_login.html')


@app.route('/administrator_dashboard')
def administrator_dashboard():
    if 'loggedin' in session and 'AdminID' in session:
        admin_id = session['AdminID']
        
        # Fetch administrator details 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT AdminID, First_Name, Last_Name, Email FROM Administrator WHERE AdminID = %s''', (admin_id,))
        admin_details = cursor.fetchone()
        admin_id = request.args.get('admin_id')
        return render_template('administrator_dashboard.html', admin=admin_details)
    else:
        return redirect(url_for('administrator_login'))

#------------------------------------ADMINISTRATOR DASHBOARD---------------------------------------------------

@app.route('/class_details', methods=['GET', 'POST'])
def class_details():
    cursor = mysql.connection.cursor(DictCursor)

    
    cursor.execute(''' 
        SELECT c.ClassID, c.RoomNumber, c.Start_Time, c.End_Time, c.StudentCapacity,
               (SELECT COUNT(*) FROM Enrolls_In_R e WHERE e.ClassID = c.ClassID) AS CurrentEnrollment,
               IF((SELECT COUNT(*) FROM Enrolls_In_R e WHERE e.ClassID = c.ClassID) >= c.StudentCapacity, 'Full', 'Available for Enrollment') AS Enrollment_Status,
               i.InstructorID, i.First_Name AS Instructor_First, i.Last_Name AS Instructor_Last
        FROM Class c
        LEFT JOIN Instructor i ON c.InstructorID = i.InstructorID
    ''')
    class_data = cursor.fetchall()

    # Fetch prerequisites for each class
    cursor.execute('SELECT cp.ClassID, cp.PrereqID FROM ClassPrereq cp')
    prerequisites = cursor.fetchall()

    # Fetch students enrolled in each class with enrollment dates
    cursor.execute(''' 
        SELECT s.StudentID, s.First_Name AS Student_First, s.Last_Name AS Student_Last, 
               e.ClassID, e.Enrollment_date
        FROM Student s
        JOIN Enrolls_In_R e ON s.StudentID = e.StudentID
        JOIN Class c ON e.ClassID = c.ClassID
        ORDER BY e.Enrollment_date DESC
    ''')
    enrolled_students = cursor.fetchall()


    cursor.close()

    # Organize data for easy display in template
    class_details = {}
    for c in class_data:
        class_id = c['ClassID']
        if class_id not in class_details:
            class_details[class_id] = {
                'RoomNumber': c['RoomNumber'],
                'Start_Time': c['Start_Time'],
                'End_Time': c['End_Time'],
                'StudentCapacity': c['StudentCapacity'],
                'Enrollment_Status': c['Enrollment_Status'],
                'InstructorID': c['InstructorID'],
                'Instructor': f"{c['Instructor_First']} {c['Instructor_Last']}" if c['Instructor_First'] else "N/A",
                'Prerequisites': [],
                'Students': []
            }

    # Add prerequisites and enrolled students to each class
    for prereq in prerequisites:
        if prereq['ClassID'] in class_details:
            class_details[prereq['ClassID']]['Prerequisites'].append(prereq['PrereqID'])
    for student in enrolled_students:
        if student['ClassID'] in class_details:
            class_details[student['ClassID']]['Students'].append({
                'StudentID': student['StudentID'],
                'Name': f"{student['Student_First']} {student['Student_Last']}",
                'Enrollment_date': student['Enrollment_date']
            })

    return render_template('class_details.html', class_details=class_details)


@app.route('/update_instructor', methods=['POST'])
def update_instructor():
    class_id = request.form['class_id']
    instructor_id = request.form['instructor_id']
    
    cursor = mysql.connection.cursor()
    cursor.execute('''
        UPDATE Class 
        SET InstructorID = %s 
        WHERE ClassID = %s
    ''', (instructor_id, class_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('class_details'))


existing_stud_ids = set()  
def generate_unique_id_Stud(prefix="S"):
    while True:
        unique_id = f"{prefix}{''.join(random.choices(string.digits, k=5))}"
        if unique_id not in existing_stud_ids:
            existing_stud_ids.add(unique_id)  
            return unique_id  
        
existing_admin_ids = set()  
def generate_unique_id_Admin(prefix="A"):
    while True:
        unique_id = f"{prefix}{''.join(random.choices(string.digits, k=5))}"
        if unique_id not in existing_admin_ids:
            existing_admin_ids.add(unique_id)  
            return unique_id  

existing_inst_ids = set()
def generate_unique_id_Ins(prefix="I"):
    while True:
        unique_id = f"{prefix}{''.join(random.choices(string.digits, k=5))}"
        if unique_id not in existing_inst_ids:
            existing_inst_ids.add(unique_id)  
            return unique_id  
        
existing_class_ids = set()
def generate_unique_id_Class(prefix="C"):
    while True:
        unique_id = f"{prefix}{''.join(random.choices(string.digits, k=3))}"
        if unique_id not in existing_inst_ids:
            existing_inst_ids.add(unique_id)  
            return unique_id 
        


@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT ClassID FROM Class')
    available_classes = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return render_template('add_instructor.html', available_classes=available_classes)


@app.route('/create_instructor', methods=['POST'])
def create_instructor():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    phone_numbers = request.form.getlist('phone_numbers')

    new_instructor_id = generate_unique_id_Ins()

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO Instructor (InstructorID, First_Name, Last_Name, Email, Password) 
                      VALUES (%s, %s, %s, %s, %s)''', 
                   (new_instructor_id, first_name, last_name, email, password))
    mysql.connection.commit()

    # Insert phone numbers 
    for phone_number in phone_numbers:
        if phone_number:
            cursor.execute('''INSERT INTO Instructor_ContactNumber (InstructorID, Contact_number) 
                              VALUES (%s, %s)''', 
                           (new_instructor_id, phone_number))
    mysql.connection.commit()

    
    room_number = request.form['room_number']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    student_capacity = request.form['student_capacity']
    prereq_id = request.form.get('prereq_id') or None  # Optional prerequisite
    fee = request.form['fee']  # New fee input

    
    new_class_id = generate_unique_id_Class()

    
    cursor.execute('''INSERT INTO Class (ClassID, RoomNumber, Start_Time, End_Time, StudentCapacity, 
                     Enrollment_Status, InstructorID, PrereqID, Fee) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                   (new_class_id, room_number, start_time, end_time, student_capacity, 
                    'Open', new_instructor_id, prereq_id, fee))
    mysql.connection.commit()

    
    if prereq_id:
        cursor.execute('''INSERT INTO ClassPrereq (ClassID, PrereqID) 
                          VALUES (%s, %s)''', 
                       (new_class_id, prereq_id))
        mysql.connection.commit()

    cursor.close()

    flash(f'Your new Instructor ID: {new_instructor_id} and Class ID: {new_class_id} (Fee: ${fee})', 'success')
    return redirect(url_for('add_instructor'))

@app.route('/add_student', methods=['GET'])
def add_student():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT ClassID, StudentCapacity FROM Class")
    classes = cursor.fetchall()
    cursor.close()
    return render_template('add_student.html', classes=classes)

@app.route('/create_student', methods=['POST'])
def create_student():
    # Retrieve student details from the form
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    class_id = request.form['class_id']  # Get the selected ClassID from the dropdown

    # Generate a unique StudentID
    new_id = generate_unique_id_Stud()

    cursor = mysql.connection.cursor()

    # Get current enrollment count, class capacity, and fee
    cursor.execute('''SELECT StudentCapacity, 
                             (SELECT COUNT(*) FROM Enrolls_In_R WHERE ClassID = %s) AS CurrentEnrollment, 
                             Fee 
                      FROM Class WHERE ClassID = %s''', (class_id, class_id))
    class_info = cursor.fetchone()

    if class_info:
        class_capacity, current_enrollment, class_fee = class_info
        # Check if class capacity is exceeded
        if current_enrollment >= class_capacity:
            flash('Cannot create student: class capacity exceeded.', 'error')
            return redirect(url_for('add_student'))

        # Insert new student record into Student table
        cursor.execute('''INSERT INTO Student (StudentID, First_Name, Last_Name, Email, Phone, Password) 
                          VALUES (%s, %s, %s, %s, %s, %s)''', 
                       (new_id, first_name, last_name, email, phone, password))
        mysql.connection.commit()

        # Insert emergency contacts into Student_EmergencyContact table
        phone_numbers = request.form.getlist('phone_numbers')
        for phone_number in phone_numbers:
            if phone_number:
                cursor.execute('''INSERT INTO Student_EmergencyContact (StudentID, Emergency_Contact) 
                                  VALUES (%s, %s)''', 
                               (new_id, phone_number))
        mysql.connection.commit()

        # Insert enrollment record into Enrolls_In_R table
        try:
            cursor.execute('''INSERT INTO Enrolls_In_R (StudentID, ClassID, Enrollment_date) 
                              VALUES (%s, %s, CURDATE())''', 
                           (new_id, class_id))
            mysql.connection.commit()

            # Insert payment record into Payment table using the dynamic fee from the Class table
            cursor.execute('''INSERT INTO Payment (StudentID, ClassID, Amount, PaymentDate) 
                              VALUES (%s, %s, %s, CURDATE())''', 
                           (new_id, class_id, class_fee))
            mysql.connection.commit()

            flash(f'Student created successfully with Student ID: {new_id}. Payment record updated.', 'success')
        except Exception as err:
            # Handle the exception and show a message if any error occurs
            flash(f'An error occurred: {err}', 'error')
        finally:
            cursor.close()

    return redirect(url_for('add_student'))

@app.route('/check_prerequisite', methods=['GET'])
def check_prerequisite():
    class_id = request.args.get('class_id')
    completed_prereqs = request.args.get('completed_prereqs').split(',')

    cursor = mysql.connection.cursor()

    # Check if all prerequisites for the selected class are fulfilled by the student's completed classes
    cursor.execute("SELECT PrereqID FROM ClassPrereq WHERE ClassID = %s", (class_id,))
    required_prereqs = cursor.fetchall()

    prerequisites_met = all(str(prereq[0]) in completed_prereqs for prereq in required_prereqs)
    cursor.close()

    return jsonify({'prerequisites_met': prerequisites_met})



@app.route('/enroll_student', methods=['POST'])
def enroll_student():
    student_id = request.form['student_id']
    class_id = request.form['class_id']
    enrollment_date = request.form['enrollment_date']
    
    cursor = mysql.connection.cursor()
    try:
        # Call the EnrollStudent stored procedure
        cursor.callproc('EnrollStudent', (student_id, class_id, enrollment_date))
        mysql.connection.commit()
        
        # Return success response
        return jsonify({"success": True, "message": "Student enrolled successfully."})
    except Exception as e:
        # If an error occurs (e.g., prerequisites not met), send the error message back to the frontend
        return jsonify({"success": False, "message": str(e)})
    finally:
        cursor.close()


        
@app.route('/add_administrator', methods=['GET'])
def add_administrator():
    return render_template('add_administrator.html')

  
@app.route('/create_administrator', methods=['POST'])
def create_administrator():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    new_id = generate_unique_id_Admin()

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO Administrator (AdminID, First_Name, Last_Name, Email, Password) 
                      VALUES (%s, %s, %s, %s, %s)''', 
                   (new_id, first_name, last_name, email, password))
    mysql.connection.commit()  # Commit the transaction
    cursor.close()

    flash(f'Your new Administrator ID: {new_id}', 'success')
    return redirect(url_for('add_administrator'))

#----------------------------------DELETE INSTRUCTOR-----------------------------------------------------------

@app.route('/delete_instructor', methods=['GET', 'POST'])
def delete_instructor():
    if request.method == 'POST':
        instructor_id = request.form['instructor_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        cursor = mysql.connection.cursor()

        # Check if instructor exists
        cursor.execute('''SELECT * FROM Instructor WHERE InstructorID = %s AND First_Name = %s AND Last_Name = %s''',
                       (instructor_id, first_name, last_name))
        instructor = cursor.fetchone()

        if instructor:
            # Set InstructorID to NULL in the Class table
            cursor.execute('UPDATE Class SET InstructorID = NULL WHERE InstructorID = %s', (instructor_id,))
            
            # Delete from related tables
            cursor.execute('DELETE FROM Instructor_ContactNumber WHERE InstructorID = %s', (instructor_id,))
            cursor.execute('DELETE FROM Instructor WHERE InstructorID = %s', (instructor_id,))
            mysql.connection.commit()
            
            # Pass the success message as a variable to the template
            return render_template('delete_instructor.html', deleted_message="Instructor deleted successfully!")
        else:
            return render_template('delete_instructor.html', error="Instructor not found.")

        cursor.close()

    # Render the form page if method is GET
    return render_template('delete_instructor.html')


#-----------------------------------------DELETE STUDENT-------------------------------------------------------
@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        cursor = mysql.connection.cursor()

        # Check if student exists
        cursor.execute('''SELECT * FROM Student WHERE StudentID = %s AND First_Name = %s AND Last_Name = %s''',
                       (student_id, first_name, last_name))
        student = cursor.fetchone()

        if student:
            # Delete from related tables
            cursor.execute('DELETE FROM Student_EmergencyContact WHERE StudentID = %s', (student_id,))
            cursor.execute('DELETE FROM Enrolls_In_R WHERE StudentID = %s', (student_id,))
            cursor.execute('DELETE FROM Payment WHERE StudentID = %s', (student_id,))  # Delete from Payment first
            cursor.execute('DELETE FROM Student WHERE StudentID = %s', (student_id,))  # Then delete from Student
            mysql.connection.commit()
            
            # Pass the success message as a variable to the template
            return render_template('delete_student.html', deleted_message="Student deleted successfully!")
        else:
            return render_template('delete_student.html', error="Student not found.")

        cursor.close()
    
    # Render the form page if method is GET
    return render_template('delete_student.html')

#------------------------------------DELETE ADMIN--------------------------------------------------------------
@app.route('/delete_administrator', methods=['GET', 'POST'])
def delete_administrator():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        cursor = mysql.connection.cursor()

        # Check if student exists
        cursor.execute('''SELECT * FROM Administrator WHERE AdminID = %s AND First_Name = %s AND Last_Name = %s''',
                       (admin_id, first_name, last_name))
        student = cursor.fetchone()

        if student:
            # Delete from related tables
            cursor.execute('DELETE FROM Administrator WHERE AdminID = %s', (admin_id,))  # Then delete from Student
            mysql.connection.commit()
            
            # Pass the success message as a variable to the template
            return render_template('delete_administrator.html', deleted_message="Admin deleted successfully!")
        else:
            return render_template('delete_administrator.html', error="Admin not found.")

        cursor.close()
    
    # Render the form page if method is GET
    return render_template('delete_administrator.html')

#--------------------------------------------------------------------------------------------------------------

# Logout Route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('StudentID', None)
    #flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
