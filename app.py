from flask import (
    Flask,
    flash,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from config import (
    MYSQL_CONFIG,
    MYSQL_CONNECT_DELAY,
    MYSQL_CONNECT_RETRIES,
    S3_BUCKET,
    S3_KEY,
    S3_SECRET,
    S3_PREFIX,
    S3_PRESIGNED_URL_EXPIRY,
    S3_REGION,
)


if S3_BUCKET and S3_KEY and S3_SECRET:
    print("S3 configured")

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import mysql.connector
import os
import time
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#s3_client = boto3.client('s3', region_name=AWS_REGION) if S3_BUCKET else None

# Initialize the Boto3 S3 Client
s3_client = None

if S3_BUCKET and S3_KEY and S3_SECRET:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=S3_REGION
        )

        sts = boto3.client(
            "sts",
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=S3_REGION
        )

        print("AWS Identity:")
        print(sts.get_caller_identity())

        s3_client.head_bucket(Bucket=S3_BUCKET)

        print(f"✓ Connected to S3 bucket: {S3_BUCKET}")

    except Exception as e:
        print(f"✗ S3 Initialization Failed: {e}")
        s3_client = None

print("S3_BUCKET =", S3_BUCKET)
print("S3_REGION =", S3_REGION)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def build_resume_key(filename):
    safe_filename = secure_filename(filename)
    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"

    if S3_PREFIX:
        return f"{S3_PREFIX}/{unique_filename}"

    return unique_filename

def save_resume(file):
    if not file or not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)

    # Save locally
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(local_path)

    print(f"Local file saved: {local_path}")

    # Upload to S3
    if s3_client:
        try:
            s3_key = (
                f"{S3_PREFIX}/{filename}"
                if S3_PREFIX
                else filename
            )

            s3_client.upload_file(
                local_path,
                S3_BUCKET,
                s3_key
            )

            print(
                f"✓ Uploaded to "
                f"s3://{S3_BUCKET}/{s3_key}"
            )

            return s3_key

        except Exception as e:
            print(f"S3 Upload Error: {e}")
            raise RuntimeError(
                f"S3 upload failed: {e}"
            )

    return filename

# def save_resume(file):
#     if not file or not allowed_file(file.filename):
#         return None

#     filename = secure_filename(file.filename)

#     # Save locally
#     local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(local_path)

#     # Upload to S3
#     if s3_client:
#         resume_key = build_resume_key(filename)

#         try:
#             with open(local_path, "rb") as f:
#                 s3_client.upload_fileobj(
#                     f,
#                     S3_BUCKET,
#                     resume_key,
#                     ExtraArgs={
#                         "ContentType": file.content_type
#                     }
#                 )

#             return resume_key

#         except (BotoCoreError, ClientError) as e:
#             raise RuntimeError(f"S3 Upload Failed: {e}")

#     return filename

def delete_resume(resume_filename):
    if not resume_filename:
        return

    try:
        if s3_client:
            s3_client.delete_object(
                Bucket=S3_BUCKET,
                Key=resume_filename
            )

        local_file = os.path.join(
            app.config['UPLOAD_FOLDER'],
            os.path.basename(resume_filename)
        )

        if os.path.exists(local_file):
            os.remove(local_file)

    except Exception as e:
        print(f"Delete Error: {e}")

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


def connect_with_retry(connect_func):
    last_error = None

    for attempt in range(1, MYSQL_CONNECT_RETRIES + 1):
        try:
            return connect_func()
        except mysql.connector.Error as error:
            last_error = error
            print(
                f"MySQL connection failed "
                f"({attempt}/{MYSQL_CONNECT_RETRIES}): {error}"
            )
            time.sleep(MYSQL_CONNECT_DELAY)

    raise last_error


def init_db():
    database_name = mysql_identifier(MYSQL_CONFIG['database'])

    server_conn = connect_with_retry(get_server_connection)
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    server_conn.commit()
    server_cursor.close()
    server_conn.close()

    conn = connect_with_retry(get_db_connection)
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
            try:
                print("Uploading:", file.filename)
                resume_filename = save_resume(file)
                print("Stored as:", resume_filename)
            except RuntimeError as error:
                flash(str(error))
                return render_template('add_employee.html'), 500

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
            try:
                resume_filename = save_resume(file) or resume_filename
            except RuntimeError as error:
                flash(str(error))
                return render_template('edit_employee.html', employee=(
                    id,
                    name,
                    department,
                    position,
                    resume_filename,
                )), 500

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
        delete_resume(resume_file[0])

    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('home'))


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    filename_for_download = os.path.basename(filename)

    if s3_client:
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': filename,
                'ResponseContentDisposition': (
                    f'attachment; filename="{filename_for_download}"'
                )
            },
            ExpiresIn=S3_PRESIGNED_URL_EXPIRY
        )
        return redirect(download_url)

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=filename_for_download
    )


if __name__ == '__main__':
    init_db()
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, host='0.0.0.0', port=5000)
