import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from botocore.exceptions import ClientError
import configparser

def get_config(ti):
    config = configparser.ConfigParser()
    config.read('config/aws.config')
    config = get_config()['bucket']

    aws_config = {
        "bucket_name": config['bucket_name'],
        "region": config['region'],
        "local_folder_path":  config['local_path_folder'],
        "s3_folder": config['s3_folder']
    }

    ti.xcom_push(key='aws_config', value=aws_config)
    return aws_config


def check_and_create_bucket(ti):
    aws_config = ti.xcom_pull(key='aws_config', task_ids='get_config')
    bucket_name = aws_config['bucket_name']
    region = aws_config['region']
    s3 = boto3.client('s3', region_name=region)
    
    try:
        # Check if the bucket exists
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{bucket_name}' does not exist. Creating the bucket at {region}...")
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Error occurred while checking or creating the bucket: {e}")
            raise

def upload_folder_to_s3(ti):
    """
    Uploads all files from a local folder to an S3 bucket.

    This function retrieves AWS configuration details such as the bucket name,
    local folder path, and S3 folder path from the XCom. It then iterates
    through all files in the specified local folder, uploading each file to the
    specified S3 bucket and folder.

    Args:
        ti: The task instance object, used to pull AWS configuration from XCom.

    Raises:
        NoCredentialsError: If the AWS credentials are not available.
        PartialCredentialsError: If the AWS credentials are incomplete.
        ClientError: If there is an error during the upload process.
    """
    aws_config = ti.xcom_pull(key='aws_config', task_ids='get_config')
    bucket_name = aws_config['bucket_name']
    folder_path = aws_config['local_folder_path']
    s3_folder = aws_config['s3_folder']


    s3 = boto3.client('s3')

    for root, _, files in os.walk(folder_path):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, folder_path)
            s3_path = os.path.join(s3_folder, relative_path).replace("\\", "/")

            try:
                print(f"Uploading {local_path} to s3://{bucket_name}/{s3_path}...")
                s3.upload_file(local_path, bucket_name, s3_path)
                print(f"Uploaded {file} to s3://{bucket_name}/{s3_path}")
            except (NoCredentialsError, PartialCredentialsError):
                print("Credentials not available.")
                raise
            except ClientError as e:
                print(f"Error uploading file {file}: {e}")
                raise
