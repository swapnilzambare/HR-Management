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

## Docker Run Commands

Build the Docker image:

```bash
docker build -t hr-management .
```

Run the Docker container:

```bash
docker run -p 5000:5000 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=your_mysql_password \
  -e MYSQL_DATABASE=hr_management \
  hr-management
```

Then open:

```text
http://localhost:5000
```

## Database

The project uses MySQL. When `app.py` runs directly, it calls `init_db()` and creates the configured database and `employees` table if they do not already exist.

## Uploads

Resume files are saved in the `uploads/` folder. Supported file types are:

- `.pdf`
- `.doc`
- `.docx`
