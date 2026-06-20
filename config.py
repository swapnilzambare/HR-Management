import os
from dotenv import load_dotenv
load_dotenv()


MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}
MYSQL_CONNECT_RETRIES = int(os.getenv('MYSQL_CONNECT_RETRIES', '30'))
MYSQL_CONNECT_DELAY = int(os.getenv('MYSQL_CONNECT_DELAY', '2'))

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET")
S3_PREFIX = os.getenv("S3_PREFIX")
S3_PRESIGNED_URL_EXPIRY = os.getenv("S3_PRESIGNED_URL_EXPIRY")
S3_REGION = os.getenv("S3_REGION")