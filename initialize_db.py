import boto3
import config_dev

client = boto3.client('dynamodb')

response = client.create_table(
    TableName=config_dev.db_table_name,
    KeySchema=[
        {
            'AttributeName': 'user_id',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'user_id',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 1
    }
)

print(response)
