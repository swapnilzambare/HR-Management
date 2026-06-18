from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import mysql.connector
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '7569'),
    'database': os.getenv('MYSQL_DATABASE', 'hr_management')
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def mysql_identifier(name):
    return f"`{name.replace('`', '``')}`"


def get_server_connection():
    return mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password']
    )


def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def init_db():
    database_name = mysql_identifier(MYSQL_CONFIG['database'])

    server_conn = get_server_connection()
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    server_conn.commit()
    server_cursor.close()
    server_conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            department VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            resume_filename VARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL database initialized successfully.")


@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, department, position, resume_filename FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', employees=employees)


@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        position = request.form['position']
        resume_filename = None

        if 'resume' in request.files:
            file = request.files['resume']
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resume_filename = filename

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, department, position, resume_filename) VALUES (%s, %s, %s, %s)",
            (name, department, position, resume_filename)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    return render_template('add_employee.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        position = request.form['position']

        cursor.execute("SELECT resume_filename FROM employees WHERE id = %s", (id,))
        current_resume_row = cursor.fetchone()
        resume_filename = current_resume_row[0] if current_resume_row else None

        if 'resume' in request.files:
            file = request.files['resume']
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resume_filename = filename

        cursor.execute(
            "UPDATE employees SET name = %s, department = %s, position = %s, resume_filename = %s WHERE id = %s",
            (name, department, position, resume_filename, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    cursor.execute("SELECT id, name, department, position, resume_filename FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_employee.html', employee=employee)


@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT resume_filename FROM employees WHERE id = %s", (id,))
    resume_file = cursor.fetchone()

    if resume_file and resume_file[0]:
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file[0])
        if os.path.exists(resume_path):
            os.remove(resume_path)

    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('home'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename_for_download = os.path.basename(filename)

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=filename_for_download
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
