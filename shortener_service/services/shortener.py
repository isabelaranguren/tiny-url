from fastapi import logger
from shared.db.db import get_table
from botocore.exceptions import ClientError

class URLShortenerService:
    def __init__(self, table_name: str):
        self.table = get_table(table_name)

    def shorten_url(self, short_key: str, long_url: str) -> bool:
        try:
            self.table.put_item(
                Item={'shortKey': short_key, 'longUrl': long_url},
                ConditionExpression='attribute_not_exists(shortKey)'
            )
            return True
        except ClientError as e:
            logger.warning(f"Failed to insert short URL: {e}")
            return False

    def get_long_url(self, short_key: str) -> str | None:
        try:
            response = self.table.get_item(Key={'shortKey': short_key})
            return response.get("Item", {}).get("longUrl")
        except ClientError as e:
            logger.error(f"Failed to retrieve long URL: {e}")
            return None