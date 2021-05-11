import pymongo
from dotenv import load_dotenv
import os

load_dotenv()


def get_client():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PW")
    url = os.getenv("MONGO_URL")
    return pymongo.MongoClient(
        f"mongodb+srv://{username}:{password}@{url}?retryWrites=true&w=majority"
    )


mongoClient = get_client()
