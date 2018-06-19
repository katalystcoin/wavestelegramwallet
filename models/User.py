import pywaves
import boto3
import uuid
from config import config
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider

class User:
    db = boto3.resource("dynamodb").Table(config.DB_TABLE_NAME)
    secrets_table_name = boto3.resource("dynamodb").Table(config.SECRETS_TABLE_NAME)
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(config.DB_ENCRYPTION_KEY_ALIAS)


    secrets_table = EncryptedTable(
        table=secrets_table_name,
        materials_provider=aws_kms_cmp
    )

    pywaves.setNode(config.NODE_URL, config.NET_ID)

    def __init__(self, user_id, seed=""):
        self.user_id = user_id
        if seed:
            self.seed = seed
            self.create_wallet(seed)
        else:
            self.initialise_wallet()

    @classmethod
    def retrieve(cls, user_id):
        """
        Creates a new User object by retrieving the user_id from database
        If the user_id does not exist in the database then this method
        will throw a KeyError
        """
        user = cls.db.get_item(Key={"user_id": str(user_id)})["Item"]
        seed = cls.retrieve_wallet(str(user["wallet_guid"]))
        return User(user_id=user["user_id"], seed=seed)

    def initialise_wallet(self):
        self.wallet_guid = str(uuid.uuid4())

        self.seed = pywaves.Address().seed 
        self.create_wallet(self.seed)
        self.secrets_table.put_item(
            Item={ "guid": self.wallet_guid, 
                   "seed": self.seed }
        )
        self.db.put_item(
            Item={"user_id": str(self.user_id), "wallet_guid": self.wallet_guid }
        )

    def create_wallet(self, seed=""):
        """
        Initializes the pywaves wallet for the User object.
        If seed is provided, the wallet is initialized from the seed,
        otherwise a wallet is generated from a new seed.
        """
        self.wallet = pywaves.Address(seed=seed)

    @classmethod 
    def retrieve_wallet(cls, wallet_guid):
        """
        Retrieves the wallet seed for the user from the encrypted secrets table
        """
        return cls.secrets_table.get_item(
           Key={"guid": wallet_guid} 
        )["Item"]["seed"]
