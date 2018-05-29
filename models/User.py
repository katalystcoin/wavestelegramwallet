import pywaves
import boto3
from config import config


class User:
    db = boto3.resource("dynamodb").Table(config.DB_TABLE_NAME)
    pywaves.setNode(config.NODE_URL, config.NET_ID)

    def __init__(self, user_id, seed=""):
        self.user_id = user_id
        self.seed = seed
        self.create_wallet(seed)

    @classmethod
    def retrieve(cls, user_id):
        """
        Creates a new User object by retrieving the user_id from database
        If the user_id does not exist in the database then this method
        will throw a KeyError
        """
        user = cls.db.get_item(Key={"user_id": str(user_id)})["Item"]
        return User(user_id=user["user_id"], seed=user["seed"])

    def create_wallet(self, seed=""):
        """
        Initializes the pywaves wallet for the User object.
        If seed is provided, the wallet is initialized from the seed,
        otherwise a wallet is generated from a new seed.
        """
        self.wallet = pywaves.Address(seed=seed)

    def save(self):
        """
        Saves the User object to database
        """
        try:
            self.db.put_item(
                Item={"user_id": str(self.user_id), "seed": self.wallet.seed}
            )
        except:
            # Handle more errors
            print("Error saving user")
            raise
