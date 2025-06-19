import logging
from shared.db.db import get_table
from kgs.utils.generator import generate_key
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)

# Basic in-memory metrics
metrics = {
    "keys_generated": 0,
    "keys_reserved": 0,
    "reservation_failures": 0
}

table = get_table("ShortKeys")  # Add this line

def batch_generate_keys(count=10000):
    """
    Generate a batch of unique short keys and insert them into DynamoDB.
    Keys that already exist are skipped due to conditional writes.
    """
    logger.info(f"Starting batch generation of {count} keys...")
    for _ in range(count):
        key = generate_key()
        try:
            table.put_item(
                Item={'shortKey': key, 'isUsed': False},
                ConditionExpression='attribute_not_exists(shortKey)'  # Prevent overwrite
            )
            metrics["keys_generated"] += 1
        except ClientError as e:
            logger.debug(f"Key collision or write error for '{key}': {e}")
            continue
    logger.info(f"Generated {metrics['keys_generated']} keys.")


def fetch_and_reserve_key():
    """
    Fetch one unused key from DynamoDB and mark it as used atomically.
    
    Returns:
        short_key (str) if available, else None
    """
    logger.info("Fetching and reserving an unused key...")

    try:
        # Scan for an unused key
        response = table.scan(
            FilterExpression=Attr('isUsed').eq(False),
            Limit=1
        )
        items = response.get('Items', [])

        # Paginate if no keys returned
        while 'LastEvaluatedKey' in response and not items:
            response = table.scan(
                FilterExpression=Attr('isUsed').eq(False),
                Limit=1,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items = response.get('Items', [])

        if not items:
            logger.warning("No available unused keys found.")
            return None

        key_item = items[0]
        short_key = key_item['shortKey']

        # Atomically reserve it
        table.update_item(
            Key={'shortKey': short_key},
            UpdateExpression="SET isUsed = :true",
            ConditionExpression=Attr('isUsed').eq(False),
            ExpressionAttributeValues={':true': True}
        )
        metrics["keys_reserved"] += 1
        logger.info(f"Reserved key: {short_key}")
        return short_key

    except ClientError as e:
        logger.error(f"DynamoDB error during key reservation: {e}")
        metrics["reservation_failures"] += 1
        return None


def get_metrics():
    """
    Return current in-memory metrics.
    Useful for debugging or exposing via a route.
    """
    return metrics