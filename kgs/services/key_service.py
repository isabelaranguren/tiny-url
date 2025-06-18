from app.db.dynamodb import get_table
from boto3.dynamodb.conditions import Attr

def get_available_key():
    table = get_table()

    response = table.scan(
        FilterExpression=Attr("isUsed").eq(False),
        Limit=1
    )

    items = response.get("Items", [])
    if not items:
        return None

    key = items[0]["shortKey"]

    table.update_item(
        Key={"shortKey": key},
        UpdateExpression="SET isUsed = :val1",
        ExpressionAttributeValues={":val1": True}
    )

    return key