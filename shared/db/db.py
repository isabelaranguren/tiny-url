import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
import logging

logger = logging.getLogger(__name__)

def get_table(table_name: str):
    """
    Establish a connection to the DynamoDB table.

    Args:
        table_name (str): The name of the DynamoDB table.

    Returns:
        boto3.resources.factory.dynamodb.Table: The DynamoDB table resource.
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        return dynamodb.Table(table_name)
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to connect to DynamoDB: {e}")
        raise RuntimeError("Could not establish connection to DynamoDB")