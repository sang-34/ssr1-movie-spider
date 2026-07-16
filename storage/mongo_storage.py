import logging

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from config import MONGO_COLLECTION, MONGO_DATABASE, MONGO_URI


class MongoStorage:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DATABASE]
        self.collection = self.db[MONGO_COLLECTION]
        self.create_indexes()

    def create_indexes(self):
        self.collection.create_index(
            [("url", ASCENDING)],
            unique=True,
            name="idx_url_unique",
        )
        self.collection.create_index(
            [("name", ASCENDING)],
            name="idx_name",
        )
        self.collection.create_index(
            [("score", ASCENDING)],
            name="idx_score",
        )

    def save(self, item):
        try:
            update_item = item.copy()
            created_at = update_item.pop("created_at", None)

            result = self.collection.update_one(
                {"url": item["url"]},
                {
                    "$set": update_item,
                    "$setOnInsert": {
                        "created_at": created_at,
                    },
                },
                upsert=True,
            )

            if result.upserted_id:
                logging.info("MongoDB insert success: %s", item.get("name"))
            elif result.modified_count:
                logging.info("MongoDB update success: %s", item.get("name"))
            else:
                logging.info("MongoDB no change: %s", item.get("name"))

            return True
        except PyMongoError:
            logging.exception("MongoDB save failed: %s", item.get("url"))
            return False