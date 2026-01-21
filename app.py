from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'employees.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # FORCE recreate table with all columns
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            resume_filename TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database recreated with resume_filename column!")

@app.route('/')
def home():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (name, department, position, resume_filename) VALUES (?, ?, ?, ?)", 
                      (name, department, position, resume_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        position = request.form['position']
        
        # GET CURRENT RESUME FILENAME FIRST
        cursor.execute("SELECT resume_filename FROM employees WHERE id = ?", (id,))
        current_resume = cursor.fetchone()[0]
        
        resume_filename = current_resume  # Keep existing by default
        
        # Only update if NEW file is uploaded
        if 'resume' in request.files:
            file = request.files['resume']
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resume_filename = filename
            # If no file selected, file.filename == '', so keep current
        
        cursor.execute("UPDATE employees SET name = ?, department = ?, position = ?, resume_filename = ? WHERE id = ?", 
                      (name, department, position, resume_filename, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    
    cursor.execute("SELECT * FROM employees WHERE id = ?", (id,))
    employee = cursor.fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)


@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT resume_filename FROM employees WHERE id = ?", (id,))
    resume_file = cursor.fetchone()
    if resume_file and resume_file[0]:
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file[0])
        if os.path.exists(resume_path):
            os.remove(resume_path)
    cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Get full path and filename for download
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filename_for_download = os.path.basename(filename)
    
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True,  # Forces download dialog
        download_name=filename_for_download  # Sets download filename
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
