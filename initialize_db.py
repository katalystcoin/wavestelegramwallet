import boto3
from config import config
import time
import json
import slugify

def insert_principal(key_policy, new_principal):
    principal_list = get_principals(key_policy)['AWS']
    # new_policy = key_policy.deepcopy
    if new_principal not in principal_list:
        principal_list.append(new_principal)
    key_policy['Statement'][0]['Principal']['AWS'] = principal_list
    return key_policy

def get_principals(key_policy):
    return key_policy['Statement'][0]['Principal']

def get_key_policy(key_id):
    return json.loads(
        kms_client.get_key_policy(KeyId=key_id, PolicyName='default')['Policy']
    )

def get_key_id(key_alias):
    return [alias for alias in kms_client.list_aliases()['Aliases'] if alias['AliasName'] == key_alias][0]['TargetKeyId']


def get_key_policy_with_alias(key_alias):
    return get_key_policy(get_key_id(key_alias))


def fetch_principal_arn(role_name):
    return [x for x in iam_client.list_roles()['Roles'] if x['RoleName'] == role_name][0]['Arn']


def generate_kms_policy_string(principals, key_id_string = 'key-default-1'):
    policy_string = json.dumps({
        'Id': key_id_string,
        'Statement': [{
            'Action': 'kms:*',
            'Effect': 'Allow',
            'Principal': {'AWS': principals},
            'Resource': '*',
            'Sid': 'Enable IAM User Permissions'}],
    'Version': '2012-10-17'}
    )
    return policy_string

def get_zappa_role_arn(settings_file = 'zappa_settings.json'):
    with open(settings_file) as settings:
        settings_dict = json.load(settings)
        env = list(settings_dict.keys())[0]
        project_name = settings_dict[env]['project_name']
        role = slugify.slugify(project_name + '-' + env) + '-ZappaLambdaExecutionRole'
    return iam.Role(role).arn 


kms_client = boto3.client('kms')
db_client = boto3.client("dynamodb")
iam = boto3.resource('iam')
def key_alias_exists(key_alias):
    return len([alias for alias in kms_client.list_aliases()['Aliases'] if alias['AliasName'] == key_alias])

# Acquire encryption key for encrypting wallets 

if not key_alias_exists(config.DB_ENCRYPTION_KEY_ALIAS):
    principals = [ iam.CurrentUser().arn, get_zappa_role_arn() ]
    print(principals)
    ps = generate_kms_policy_string(principals)
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

# response = db_client.create_table(
#     TableName="test",
#     KeySchema=[{"AttributeName": "guid", "KeyType": "HASH"}],
#     AttributeDefinitions=[{"AttributeName": "guid", "AttributeType": "N"}],
#     ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 1},
# )
