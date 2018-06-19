import boto3
import json
import slugify

kms_client = boto3.client('kms')
iam = boto3.resource('iam')
api_client = boto3.client('apigateway')

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

def get_lambda_name(settings_file = 'zappa_settings.json'):
    settings_dict = get_settings()
    env = get_env(settings_dict)
    project_name = settings_dict[env]['project_name']
    return slugify.slugify(project_name + '-' + env)

def get_env(settings_dict):
    return list(settings_dict.keys())[0]

def get_zappa_role_arn(settings_file = 'zappa_settings.json'):
    role = get_lambda_name() + '-ZappaLambdaExecutionRole'
    return iam.Role(role).arn

def get_settings(settings_file = 'zappa_settings.json'):
    with open(settings_file) as settings:
        settings_dict = json.load(settings)
    return settings_dict

def get_api_url(settings_file = 'zappa_settings.json'):
    settings_dict = get_settings(settings_file)
    env = get_env(settings_dict)
    region = settings_dict[env]['aws_region']

    api_id = [x for x in api_client.get_rest_apis()['items'] if x['name'] == get_lambda_name()][0]['id']

    return "https://{}.execute-api.{}.amazonaws.com/{}".format(api_id, region, env)