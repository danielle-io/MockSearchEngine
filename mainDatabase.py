import pymongo
from collections import defaultdict
from credentials import Credentials

class MainDatabase:

    def __init__(self):

        client = pymongo.MongoClient(

            getCredentials())

        self.db = client.search_engine

        self.collection = self.db.final_index
        self.collection_content = self.db.final_content

        self.collection = self.db.final_index
        self.collection_content = self.db.final_final_content

        # Twogram collections
        self.twogram_collection = self.db.final_final_twogram_index
        self.twogram_content_collection = self.db.final_final_twogram_content


    def bulk_insert(self, docs):
        self.collection.insert_many(docs)

    def bulk_insert_content(self, docs):
        self.collection_content.insert_many(docs)

    def twogram_bulk_insert(self, docs):
        self.twogram_collection.insert_many(docs)

    def twogram_bulk_insert_content(self, docs):
        self.twogram_content_collection.insert_many(docs)

    # Insert a single document into the mongo collection: documents
    # and return the inserted _id
    def insert_mongo_document(self, document):
        return self.collection.insert_one(document).inserted_id


    def find_mongo_documents(self, key, value):
        return self.collection.find({key: value})

    def find_mongo_documents_by_key(self, key):
        return list(self.collection.find({key : {'$exists' : True}}))


    def count_words(self):
        word_dict = dict()
        for i in self.words:
            if i in word_dict:
                word_dict[i] += 1
            else:
                word_dict[i] = 1

        for i in word_dict:
            self.insert_mongo_document({i :word_dict[i]})


    def update_database(self, indexDictionary: dict):
        counter = 0
        incremCounter = 0

        for token in indexDictionary.keys():
            print(token)
            counter = counter + 1
            incremCounter = incremCounter + 1

            if incremCounter == 1000:
                incremCounter = 0

            self.collection.insert_one({
                'word': token,
                'urls': indexDictionary[token]['urls'],
                'amountOfURLs': indexDictionary[token]['amountOfURLs'],
                'df': indexDictionary[token]['amountOfURLs']
            })

if __name__ == "__main__":
    pass