# coding = utf-8
import sys
import os
from dbConnection import dbConnector
from logger import logger


class ipPool(dbConnector):

    def get_all_ip(self):
        try:
            result = list()
            for record in self.collection.aggregate(
                            [
                                {'$match': {'score': {'$gte': 10}}},
                                {'$project': {'_id': 0, 'ip': 1, 'port': 1}}
                            ]
                        ).batch_size(1):
                result.append(record)

            return result

        except Exception as e:
            logger.error('get all ip failed for %s'%str(e))

    def get_count_ip(self, limit=10):

        try:
            result = list()
            for record in self.collection.aggregate(
                    [
                        {'$match': {'score': {'$gte': 10}}},
                        {'$limit': limit},
                        {'$project': {'_id': 0, 'ip': 1, 'port': 1}}
                    ]
            ).batch_size(1):
                result.append(record)

            return result

        except Exception as e:
            logger.error('get count ip failed for %s' % str(e))


if __name__ == "__main__":
    MONGODB_SERVER = "192.168.49.186"
    MONGODB_PORT = 27017
    MONGODB_DB = "proxy"
    MONGODB_COLLECTION = "proxys"
    db = ipPool(MONGODB_SERVER,MONGODB_PORT,MONGODB_DB,MONGODB_COLLECTION)
    result = db.get_all_ip()
    print result
    # for i in db.collection.find():
    #     print str(i)
