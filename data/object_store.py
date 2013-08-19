# coding=utf-8

'''
Wraps around object storage.
'''

__author__ = 'tmetsch'

import pymongo

from bson import ObjectId


class ObjectStore(object):
    '''
    Stores need to derive from this one.
    '''

    def list_objects(self, uid):
        '''
        List the objects of a user.
        
        :param uid: User id.User id.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def create_object(self, uid, content):
        '''
        Create an object for a user. Returns and id

        :param content: Some content.
        :param uid: User id.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def retrieve_object(self, uid, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def update_object(self, uid, obj_id, content):
        '''
        Add a object for a user.

        :param content: Some content.
        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def delete_object(self, uid, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')


class MongoStore(ObjectStore):
    '''
    Object Storage based on Mongo.
    '''

    def __init__(self, host, port):
        '''
        Setup a connection to the Mongo server.
        '''
        self.client = pymongo.MongoClient(host, port)

    def list_objects(self, uid):
        '''
        List the objects of a user.

        :param uid: User id.User id.
        '''
        db = self.client[uid]
        collection = db['data_objects']
        res = []
        for obj in collection.find():
            res.append(obj['_id'])
        return res

    def create_object(self, uid, content):
        '''
        Create an object for a user. Returns and id

        :param content: Some content.
        :param uid: User id.
        '''
        db = self.client[uid]
        collection = db['data_objects']
        tmp = {'value': content}
        obj_id = collection.insert(tmp)
        return obj_id

    def retrieve_object(self, uid, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        db = self.client[uid]
        collection = db['data_objects']
        content = collection.find_one({'_id': ObjectId(obj_id)})
        return content['value']

    def update_object(self, uid, obj_id, content):
        '''
        Add a object for a user.

        :param content: Some content.
        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        db = self.client[uid]
        collection = db['data_objects']
        collection.update({'_id': ObjectId(obj_id)},
                          {"$set": {'value': content}}, upsert=False)

    def delete_object(self, uid, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        '''
        db = self.client[uid]
        collection = db['data_objects']
        collection.remove({'_id': ObjectId(obj_id)})


class CDMIStore(ObjectStore):
    '''
    TODO: will retrieve objects from a (remote) CDMI enabled Object Storage
    Service.
    '''

    pass