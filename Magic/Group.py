#Group Class
#import
import requests
import json

#classes 
import fileManager
class grp: 
    ''' group class - creates a group object and makes any group related api cals'''

    def __init__(self, enterpriseID, groupID):
        '''A group is an individual hotel with users (Guest/ Staff) inside.
        
        Hierachy: Ent/SP > Group > User 

        :variable enterpriseID: Ent/SP ID
        :variable groupID: Group ID
        '''
        super().__init__()

        self.enterpriseID = enterpriseID
        self.groupID = groupID
        self.domain = None

    def getDefaultDomain(self, a):
        '''
        gets default domain of the group and sets self.domain to this value

        :param a: API object used for api calls
        '''
        endpoint = "/groups?serviceProviderId=" + self.enterpriseID + "&groupId="+ self.groupID
        headers = {
            "Authorization":"Bearer "+a.token
        }
        payload = {
        }

        response = requests.get(a.api_host+endpoint, headers=headers, data=payload)
        self.domain = response.json()['defaultDomain']

    def createDevice(self, name, a): 
        '''
        creates device profile used for trunks.
        The device name is 'Inference-sbc' but this is used for PolyAI also.

        :param name: name of the device being built depending on trunk
        :param a: API object used for api calls
        :return: response from POST request
        '''
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        payload = {
            "deviceType": "Poly AI - SBC Trunk",
            "deviceName": name,
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        response = requests.post(a.api_host+endpoint, data=json.dumps(payload), headers=headers)
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'Group.createDevice.POST || {name} || {error}')
        return response.json()

    def increaseCallCapacity(self, channels, a, bursting = 0): 
        '''
        increases group call capacity by the number of agents and bursting channels purchased.

        :param channels: number of agents inputted by user
        :param a: API object used for api calls
        :param bursting=0: bursting set by user, 0 by default 
        :return: response from PUT request 
        '''
        currentCapacity = self.getCallCapacity(a)
        currentmaxcall = currentCapacity['maxActiveCalls']
        currentbursting = currentCapacity['burstingMaxActiveCalls']

        print(f'Increasing from: Max Active Calls - {currentmaxcall} Max Bursting Calls - {currentbursting} to: Max Active Calls - {currentmaxcall + channels} Max Bursting Calls - {currentbursting + bursting}')

        endpoint = "/groups/trunk-groups/call-capacity"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "maxActiveCalls": currentmaxcall + channels,
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }
        if bursting != 0:
            data["burstingMaxActiveCalls"] = currentbursting + bursting

        response = requests.put(a.api_host+endpoint,data=json.dumps(data),headers=headers)
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'Group.increaseCallCapacity.PUT || maxActiveCalls: {currentmaxcall + channels} || {error}')
        return response.json()

    def getCallCapacity(self, a): 
        '''
        used for icnreaseCallCapcity() to get the existing call capacity of the group

        :param a: API object used for api calls
        :return: response from GET request
        '''
        endpoint = "/groups/trunk-groups/call-capacity?groupId="+self.groupID+"&serviceProviderId="+self.enterpriseID 
        headers = {
            "Authorization": "Bearer "+a.token
        }
        data = {
        }

        response = requests.get(a.api_host+endpoint,data=data,headers=headers)
        return response.json()   

    def __repr__(self) -> str:
        return f'EnterpriseID: {self.enterpriseID}, GroupID: {self.groupID}, Domain: {self.domain}'