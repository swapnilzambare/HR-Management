FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code after
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
