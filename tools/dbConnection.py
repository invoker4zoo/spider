# -*- coding: utf-8 -*-
from pymongo import MongoClient
import sys
from pymongo.errors import ConnectionFailure
import os
import json
from logger import logger

CURRENT_PATH = os.path.dirname(__file__)
if CURRENT_PATH:
    CURRENT_PATH = CURRENT_PATH + "/"


class dbConnector(object):

    def __init__(self,MONGODB_SERVER,MONGODB_PORT,MONGODB_DB,MONGODB_COLLECTION):

        try:
            self.connection = MongoClient(
                MONGODB_SERVER,
                MONGODB_PORT
            )
            self.db = self.connection[MONGODB_DB] # Getting a databse
            self.collection = self.db[MONGODB_COLLECTION]  # Getting a collection
        except ConnectionFailure, e:
            sys.stderr.write("Could not connect to MongoDB: %s" % e)
            sys.exit(1)

    def readNext(self):
            pass

    def getCollection(self):
        return self.collection

    def count(self):
        return self.collection.count()

    # def find_Info_by_category(self, category):
    #     try:
    #         Info = list()
    #         for record in  self.collection.aggregate([{'$match':{'category':category}},\
    #                                                   {'$project':{'salary':1,'degree':1,'workingYears':1,'sourceCity':1}}]):
    #             Info.append(record)
    #         return Info
    #     except Exception,e:
    #         logger.info('FUN[find_Info_by_category] failed for category:%s'%category)
    #
    # def find_company_name(self,num=None):
    #     try:
    #         count = 0
    #         company_list = list()
    #         for record in self.collection.find():
    #             count += 1
    #             print 'read record %d' %count
    #             company_list.append(record[u"companyName"])
    #             if (num != None) and (count >= num):
    #                 break
    #         company_name = list(set(company_list))
    #         return company_name
    #     except Exception,e:
    #         logger.info('FUN[find_company_name] failed ')
    #
    # def find_Info_by_companyName(self, companyName):
    #     try:
    #         count = 0
    #         company_Info = list()
    #         for record in self.collection.find({"companyName":companyName}):
    #             count += 1
    #             company_Info.append(record)
    #             print 'read information for company %s job_list length %d' %(companyName, count)
    #         return company_Info
    #     except Exception,e:
    #         logger.info('FUN[find_Info_by_companyName] failed for companyName:%s'%companyName)
    #
    # def upsert_period(self,companyName,period):
    #     try:
    #         insert_doc = {
    #             'companyName':companyName,
    #             'period':period
    #         }
    #         self.collection.update({'companyName':companyName},insert_doc,upsert=True)
    #     except Exception,e:
    #         logger.info('FUN[upsert_period] failed ')



if __name__ == "__main__":
    MONGODB_SERVER = "192.168.49.186"
    MONGODB_PORT = 27017
    MONGODB_DB = "proxy"
    MONGODB_COLLECTION = "proxys"
    db = dbConnector(MONGODB_SERVER,MONGODB_PORT,MONGODB_DB,MONGODB_COLLECTION)
    for i in db.collection.find():
        print str(i)