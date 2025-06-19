import logging
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from shared.db.db import get_table
from kgs.utils.generator import generate_key

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s"
)

class KeyPoolService:
    def __init__(self, table_name="KeyPool"):
        self.table = get_table(table_name)
        self.metrics = {
            "keys_generated": 0,
            "keys_reserved": 0,
            "reservation_failures": 0
        }

    def generate_key_pool(self, count=10000):
        """
        Generate a batch of unique short keys and insert them into DynamoDB.
        Keys that already exist are skipped.
        """
        logger.info(f"Generating {count} keys...")
        for _ in range(count):
            key = generate_key()
            try:
                self.table.put_item(
                    Item={'shortKey': key, 'isUsed': False},
                    ConditionExpression='attribute_not_exists(shortKey)'
                )
                self.metrics["keys_generated"] += 1
            except ClientError as e:
                logger.debug(f"Skipped existing key '{key}': {e}")
                continue
        logger.info(f"Successfully generated {self.metrics['keys_generated']} keys.")

    def reserve_available_key(self):
        """
        Fetch an unused key and mark it as used.
        """
        logger.info("Looking for an available key...")
        try:
            response = self.table.scan(
                FilterExpression=Attr('isUsed').eq(False),
                Limit=1
            )
            items = response.get('Items', [])
            while 'LastEvaluatedKey' in response and not items:
                response = self.table.scan(
                    FilterExpression=Attr('isUsed').eq(False),
                    Limit=1,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items = response.get('Items', [])

            if not items:
                logger.warning("No available keys.")
                return None

            short_key = items[0]['shortKey']
            self.table.update_item(
                Key={'shortKey': short_key},
                UpdateExpression="SET isUsed = :true",
                ConditionExpression=Attr('isUsed').eq(False),
                ExpressionAttributeValues={':true': True}
            )
            self.metrics["keys_reserved"] += 1
            logger.info(f"Reserved key: {short_key}")
            return short_key

        except ClientError as e:
            logger.error(f"DynamoDB reservation failed: {e}")
            self.metrics["reservation_failures"] += 1
            return None

    def get_usage_metrics(self):
        """
        Return internal usage stats for monitoring.
        """
        return self.metrics