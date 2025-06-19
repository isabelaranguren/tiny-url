import boto3
import os
from botocore.exceptions import ClientError

def test_dynamodb_connection():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        table_name = 'ShortKeys'
        table = dynamodb.Table(table_name)
        
        table.load() 
        print(f"Table '{table_name}' found. Status: {table.table_status}")
        
        test_key = 'test-key-123'
        table.put_item(
            Item={'shortKey': test_key, 'isUsed': False},
            ConditionExpression='attribute_not_exists(shortKey)'
        )
        print(f"Inserted test item with key: {test_key}")
        
        response = table.get_item(Key={'shortKey': test_key})
        item = response.get('Item')
        print(f"Fetched item: {item}")
        
        table.delete_item(Key={'shortKey': test_key})
        print("Test item deleted successfully.")
        
        print("DynamoDB connection test completed successfully.")

    except ClientError as e:
        print(f"AWS ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_dynamodb_connection()