# HR Management

A simple Flask-based HR Management application for managing employee records. The app stores employee details in a MySQL database and supports uploading employee resume files in PDF, DOC, or DOCX format.

## Features

- View all employees
- Add a new employee
- Edit employee details
- Delete employee records
- Upload and download employee resumes
- Store data using MySQL

## Project Structure

```text
HR-Management/
|-- app.py
|-- config.py
|-- requirements.txt
|-- Dockerfile
|-- README.md
|-- static/
|   `-- style.css
|-- templates/
|   |-- base.html
|   |-- home.html
|   |-- add_employee.html
|   `-- edit_employee.html
|-- uploads/
|   `-- uploaded resume files
`-- venv/
    `-- local virtual environment
```

## Prerequisites

Before running this project, make sure you have:

- Python 3.11 or newer
- pip
- MySQL Server
- Git, optional
- Docker, optional if you want to run the app in a container

## Installation

Clone or download the project, then open a terminal in the project folder.

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Activate the virtual environment on macOS or Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## MySQL Setup

Start your MySQL server and create a MySQL user that can create databases and tables.

The application reads MySQL settings from environment variables:

```text
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=hr_management
```

On Windows PowerShell, set them like this:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_DATABASE="hr_management"
```

On macOS or Linux, set them like this:

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=your_mysql_password
export MYSQL_DATABASE=hr_management
```

The app creates the `hr_management` database and `employees` table automatically when it starts.

## Run Commands

Run the Flask application:

```bash
python app.py
```

The app will start at:

```text
http://localhost:5000
```

## Docker Compose Run Commands

The recommended containerized setup starts both Flask and MySQL:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:5000
```

The Docker Compose setup uses these defaults:

```text
MYSQL_ROOT_PASSWORD=7569
MYSQL_DATABASE=hr_management
APP_PORT=5000
```

You can override them by creating a `.env` file in the project root.

Stop the containers:

```bash
docker compose down
```

Stop the containers and remove the MySQL data volume:

```bash
docker compose down -v
```

## Docker Run Commands With Host MySQL

Build the Docker image:

```bash
docker build -t hr-management .
```

If you want to run only the Flask container and connect it to MySQL installed on your computer, run:

```bash
docker run -p 5000:5000 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=7569 \
  -e MYSQL_DATABASE=hr_management \
  hr-management
```

Then open:

```text
http://localhost:5000
```

## Database

The project uses MySQL. When `app.py` runs directly, it calls `init_db()` and creates the configured database and `employees` table if they do not already exist.

## Resume Storage

By default, resume files are saved in the local `uploads/` folder. For AWS ECS/Fargate, configure S3 storage with environment variables:

```text
S3_BUCKET=your-s3-bucket-name
S3_PREFIX=resumes
AWS_REGION=your-aws-region
S3_PRESIGNED_URL_EXPIRY=300
```

When `S3_BUCKET` is set, uploaded resumes are stored in S3 and download links use short-lived presigned URLs.

Supported file types are:

- `.pdf`
- `.doc`
- `.docx`

## AWS ECS/Fargate Settings

For Fargate with RDS MySQL and S3, set these container environment variables:

```text
MYSQL_HOST=your-rds-endpoint.amazonaws.com
MYSQL_USER=your-rds-user
MYSQL_PASSWORD=your-rds-password
MYSQL_DATABASE=hr_management
MYSQL_CONNECT_RETRIES=30
MYSQL_CONNECT_DELAY=2
S3_BUCKET=your-s3-bucket-name
S3_PREFIX=resumes
AWS_REGION=your-aws-region
```

The ECS task role needs permission to access the S3 bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-s3-bucket-name/*"
    }
  ]
}
```
