# coding=utf-8

'''
Wraps around object storage.
'''

__author__ = 'tmetsch'

import pymongo

from bson import ObjectId


def get_object_stor(uri):
    '''
    Returns the right instance of a object storage interface object for an
    given URI.

    :param uri: The URI of the object storage.
    :return: Instance of ObjectStore.
    '''
    # TODO: implement
    pass


class ObjectStore(object):
    '''
    Stores need to derive from this one.
    '''

    def list_objects(self, uid, token):
        '''
        List the objects of a user.
        
        :param uid: User id.
        :param token: Access token.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def create_object(self, uid, token, content):
        '''
        Create an object for a user. Returns and id

        :param content: Some content.
        :param uid: User id.
        :param token: Access token.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def retrieve_object(self, uid, token, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def update_object(self, uid, token, obj_id, content):
        '''
        Add a object for a user.

        :param content: Some content.
        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')

    def delete_object(self, uid, token, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        raise NotImplementedError('Needs to be implemented by subclass.')


class MongoStore(ObjectStore):
    '''
    Object Storage based on Mongo.
    '''

    auth = False

    def __init__(self, uri):
        '''
        Setup a connection to the Mongo server.
        '''
        self.client = pymongo.MongoClient(uri)

    def list_objects(self, uid, token):
        '''
        List the objects of a user.

        :param uid: User id.
        :param token: Access token.
        '''
        db = self.client[uid]
        db.authenticate(uid, token)
        collection = db['data_objects']
        res = []
        for obj in collection.find():
            res.append(obj['_id'])
        return res

    def create_object(self, uid, token, content):
        '''
        Create an object for a user. Returns and id

        :param content: Some content.
        :param uid: User id.
        :param token: Access token.
        '''
        db = self.client[uid]
        db.authenticate(uid, token)
        collection = db['data_objects']
        tmp = {'value': content}
        obj_id = collection.insert(tmp)
        return obj_id

    def retrieve_object(self, uid, token, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        db = self.client[uid]
        db.authenticate(uid, token)
        collection = db['data_objects']
        content = collection.find_one({'_id': ObjectId(obj_id)})
        return content['value']

    def update_object(self, uid, token, obj_id, content):
        '''
        Add a object for a user.

        :param content: Some content.
        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        db = self.client[uid]
        db.authenticate(uid, token)
        collection = db['data_objects']
        collection.update({'_id': ObjectId(obj_id)},
                          {"$set": {'value': content}}, upsert=False)

    def delete_object(self, uid, token, obj_id):
        '''
        Add a object for a user.

        :param obj_id: Identifier of the object.
        :param uid: User id.
        :param token: Access token.
        '''
        db = self.client[uid]
        db.authenticate(uid, token)
        collection = db['data_objects']
        collection.remove({'_id': ObjectId(obj_id)})


class CDMIStore(ObjectStore):
    '''
    TODO: will retrieve objects from a (remote) CDMI enabled Object Storage
    Service.
    '''

    pass