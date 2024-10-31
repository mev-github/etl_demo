from org.apache.nifi.processor.io import StreamCallback
import pymongo
import json
import io

class PyStreamCallback(StreamCallback):
    def process(self, inputStream, outputStream):
        client = pymongo.MongoClient('mongodb://mongo_user:mongo_password@mongodb:27017')
        db = client['mongo_db']
        collection = db['source_collection']
        data = list(collection.find({}, {'_id': 0}))
        outputStream.write(bytearray(json.dumps(data, default=str).encode('utf-8')))
        client.close()

flowFile = session.get()
if flowFile is not None:
    flowFile = session.write(flowFile, PyStreamCallback())
    session.transfer(flowFile, REL_SUCCESS)
else:
    session.transfer(flowFile, REL_FAILURE)
