import boto3
from config import config

client = boto3.client("dynamodb")

response = client.create_table(
    TableName=config.DB_TABLE_NAME,
    KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
    AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
    ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 1},
)

print(response)
