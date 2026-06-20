import os


MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '7569'),
    'database': os.getenv('MYSQL_DATABASE', 'hr_management')
}
MYSQL_CONNECT_RETRIES = int(os.getenv('MYSQL_CONNECT_RETRIES', '30'))
MYSQL_CONNECT_DELAY = int(os.getenv('MYSQL_CONNECT_DELAY', '2'))
#ACCESS_KEY = "AKIAWQEU5BWGUIVIMUEN"
#SECRET_ACCESS_KEY = "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"
#S3_BUCKET = os.getenv('S3_BUCKET')
#S3_PREFIX = os.getenv('S3_PREFIX', 'uploads').strip('/')
#AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_PRESIGNED_URL_EXPIRY = int(os.getenv('S3_PRESIGNED_URL_EXPIRY', '300'))


# AWS Configurations - Best practice is to load these via environment variables
S3_KEY = "AKIAWQEU5BWGXGUULCTQ"
S3_SECRET = "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"
S3_BUCKET = "swap-aws-s3-bucket"
S3_PREFIX = "uploads"
S3_REGION = "ap-south-1"
#S3_BUCKET = os.environ.get("swap-aws-s3-bucket")
# S3_KEY = os.environ.get("AKIAWQEU5BWGXGUULCTQ")
# S3_SECRET = os.environ.get("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")
# S3_REGION = os.environ.get("AWS_REGION", "ap-south-1")
