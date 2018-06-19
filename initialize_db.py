import boto3
from config import config
import time
import json
import aws_utils


kms_client = boto3.client('kms')
db_client = boto3.client("dynamodb")
iam = boto3.resource('iam')
def key_alias_exists(key_alias):
    return len([alias for alias in kms_client.list_aliases()['Aliases'] if alias['AliasName'] == key_alias])

# Acquire encryption key for encrypting wallets 

if not key_alias_exists(config.DB_ENCRYPTION_KEY_ALIAS):
    principals = [ iam.CurrentUser().arn, aws_utils.get_zappa_role_arn() ]
    ps = aws_utils.generate_kms_policy_string(principals)
    createkey_request = kms_client.create_key(Policy=ps)
    keyid = createkey_request['KeyMetadata']['KeyId']
    kms_client.create_alias(AliasName=config.DB_ENCRYPTION_KEY_ALIAS, TargetKeyId=keyid)
else:
    print("Encryption Key already exists, using existing key")

# Set up Database tables

try:
    response = db_client.create_table(
        TableName=config.DB_TABLE_NAME,
        KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 1},
    )
except:
    print("Couldnt create database for some reason")
else:
    print(response)

try:
    response = db_client.create_table(
        TableName=config.SECRETS_TABLE_NAME,
        KeySchema=[{"AttributeName": "guid", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "guid", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 1},
    )
except:
    print("Couldn't create secrets table for some reason")
else:
    print(response)
