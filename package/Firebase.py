# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials, auth, db
import json


class myFirebase():
    def __init__(self, json_dir, databaseURL, uid, reference_list, additional_claims={'premiumAccount':True}):
        self.cred = credentials.Certificate(json_dir)
        self.app = firebase_admin.initialize_app(self.cred, {
                'databaseURL': 'firebase URL'
                })
        self.uid = uid
        self.additional_claims = additional_claims
        self.custom_token = auth.create_custom_token(self.uid, self.additional_claims)
        if type(reference_list) is not list:
            print(type(reference_list))
            print('Warning reference is not list type !!!!!!!')
        self.ref = []
        self.ref_dict = {}
        for i in range(len(reference_list)):
            self.ref.append(db.reference(reference_list[i]))
            self.ref_dict[reference_list[i]] = i

    ### Post data to firebase
    def Post2Firebase(self, reference_name,json_data):
        pos = self.ref_dict[reference_name]
        self.ref[pos].push(json_data)

    ### Set data to firebase, Warning : It will cause previous data disappear
    def Set2Firebase(self, reference_name, json_data):
        pos = self.ref_dict[reference_name]
        self.ref[pos].set(json_data)

    ### Get data from firebase, Modes have "GET_RAW", "GET_LIST", "GET_JSON"
    def GetFromFirebase(self, reference_name, mode='GET_LIST'):
        pos = self.ref_dict[reference_name]
        if mode == 'GET_RAW':
            return self.ref[pos].get()
        elif mode is 'GET_LIST':
            list_data = []
            for d in self.ref[pos].get().values():
                list_data.append(d)
            return list_data
        elif mode is 'GET_JSON':
            list_data = []
            for d in self.ref[pos].get().values():
                list_data.append(d)
            return json.dumps(list_data)

    ### Add another reference to reference list
    def AddReferenceList(self, reference_list):
        for i in range(len(reference_list)):
            self.ref.append(db.reference(reference_list[i]))
            self.ref_dict[reference_list[i]] = i + len(self.ref) - 1

    def close(self):
        pass

if __name__ == '__main__':
    print('Run code start ... ')
    data = {'20180319':199}
    data = json.dumps(data)
    json_dir = 'XXX.json'
    databaseURL = 'firebase URL'
    uid = "UID"
    reference = ['Aquarium/indoor', 'Aquarium/outdoor']
    myfirebase = myFirebase(json_dir, databaseURL, uid, reference)
    myfirebase.Post2Firebase('Aquarium/indoor', data)
    myfirebase.Post2Firebase('Aquarium/outdoor', data)
    myfirebase.Post2Firebase('Aquarium/outdoor', data)

    myfirebase.AddReferenceList(['Aquarium/Test'])
    myfirebase.Post2Firebase('Aquarium/Test', data)
    myfirebase.Set2Firebase('Aquarium/Test', 1234)

    print(myfirebase.GetFromFirebase('Aquarium/indoor'))


