from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt
from flask_bcrypt import Bcrypt 

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt_new = Bcrypt(app) 

# Configure MySQL
app.config['MYSQL_HOST'] = 'tci-dev-db.c7bvdckv2va3.ap-south-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'tcidevdb'
app.config['MYSQL_PASSWORD'] = 'tcidevfabricpass'
app.config['MYSQL_DB'] = 'Swagger'

mysql = MySQL(app)

@app.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        print(type(hashed_password))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        my_str_as_bytes = str.encode(user[3])
        if user and bcrypt.checkpw(password=password , hashed_password=my_str_as_bytes) :
            session['user_id'] = user[0]
            print(session['user_id'])
            return redirect(url_for('home'))

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Courses CRUD
@app.route('/courses')
def courses():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses")
        courses = cur.fetchall()
        cur.close()
        return render_template('courses.html', courses=courses)
    return redirect(url_for('login'))

@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if 'user_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            instructor = request.form['instructor']
            credits = request.form['credits']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO courses (title, description, instructor, credits) VALUES (%s, %s, %s, %s)",
                        (title, description, instructor, credits))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('courses'))

        return render_template('add_course.html')
    return redirect(url_for('login'))

@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
        course = cur.fetchone()
        cur.close()

        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            instructor = request.form['instructor']
            credits = request.form['credits']

            cur = mysql.connection.cursor()
            cur.execute("UPDATE courses SET title = %s, description = %s, instructor = %s, credits = %s WHERE id = %s",
                        (title, description, instructor, credits, course_id))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('courses'))

        return render_template('edit_course.html', course=course)
    return redirect(url_for('login'))

@app.route('/courses/delete/<int:course_id>')
def delete_course(course_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('courses'))
    return redirect(url_for('login'))

@app.route('/courses/view', methods=['GET'])
def viewCourse():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Swagger.courses")
        courses = cur.fetchall()
        cur.close()
        return render_template('view_courses.html', courses=courses)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
