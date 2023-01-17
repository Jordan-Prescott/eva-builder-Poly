#Enterpise Class
#import
from distutils.log import error
import requests
import json

#classes
import fileManager
class ent: 
    '''enterprise class - any enterprise or serviceprovider functions'''
    def __init__(self, ID, type):
        '''Ent/SP is the brand or chain like Marriott with groups (individual hotels) and users (Staff/ Guests in the hotel).

        Hierachy: Ent/SP > Group > User 

        :variable ID: Ent/SP ID
        :variable type: Ent or SP Type
        '''

        self.ID = ID
        self.type = type

    def increaseCallCapacity(self, channels, a, bursting=0): 
        '''
        increases enterprise call capacity by the number of agents and bursting channels purchased.

        :param channels: number of agents inputted by user
        :param a: API object used for api calls
        :param bursting=0: bursting set by user, 0 by default 
        :return: response from PUT request 
        '''
        currentCapacity = self.getCallCapacity(a) 
        currentmaxcall = currentCapacity['maxActiveCalls']
        currentbursting = currentCapacity['burstingMaxActiveCalls']

        print(f'Increasing from: Max Active Calls - {currentmaxcall} Max Bursting Calls - {currentbursting} to: Max Active Calls - {currentmaxcall + channels + bursting}')

        if currentbursting == -1: # if no bursting capacity set to 0 
            currentbursting = 0
        
        endpoint = "/service-providers/trunk-groups/call-capacity"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "maxActiveCalls": currentmaxcall+channels+bursting,
            "serviceProviderId": self.ID
        }
        
        #REMOVED: bursting is now added into maxActiveCalls
        # if bursting != 0: # if bursting capacity is set (passed into method increaseCallCapacity)
        #     data["burstingMaxActiveCalls"] = currentbursting + bursting

        response = requests.put(a.api_host+endpoint,data=json.dumps(data),headers=headers) # PUT request so it uses payload to identify which group to adjust
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'Enteprise.increaseCallCapacity.PUT || maxActiveCalls: {currentmaxcall + channels + bursting} || {error}')
        return response.json()

    def getCallCapacity(self, a):
        '''
        used for icnreaseCallCapcity() to get the existing call capacity of ent

        :param a: API object used for api calls
        :return: response from GET request
        '''
        endpoint = "/service-providers/trunk-groups/call-capacity?serviceProviderId="+self.ID
        headers = {
            "Authorization": "Bearer "+a.token
        }
        data = {
        }
        response = requests.get(a.api_host+endpoint,data=data,headers=headers)
        return response.json()

    def __repr__(self) -> str:
        return f"ID: {self.ID}, Type: {self.type}"
    