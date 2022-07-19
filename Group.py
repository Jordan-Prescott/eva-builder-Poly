#Group Class
#import
import requests
import json

#classes 
import fileManager
class grp: # builds group devices and adjusts trunk call capacity
    ''' group class - creates a group object and makes any group related api cals'''
    def __init__(self, enterpriseID, groupID):
        '''init variables'''
        super().__init__()

        self.enterpriseID = enterpriseID
        self.groupID = groupID
        self.domain = None

    def getDefaultDomain(self, a): # gets default domain for group
        endpoint = "/groups?serviceProviderId=" + self.enterpriseID + "&groupId="+ self.groupID
        headers = {
            "Authorization":"Bearer "+a.token
        }
        payload = {
        }

        response = requests.get(a.api_host+endpoint, headers=headers, data=payload)
        self.domain = response.json()['defaultDomain']

    def createDevice(self, name, a): # creates inference-sbc device
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        payload = {
            "deviceType": "Inference-sbc",
            "deviceName": name,
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        response = requests.post(a.api_host+endpoint, data=json.dumps(payload), headers=headers)
        if str(response) != '<Response [200]>':
            fileManager.fm.writeErrors(f'Group.createDevice.POST - {name}')
        return response.json()

    def increaseCallCapacity(self, channels, a): 
        currentCapacity = self.getCallCapacity(a)
        currentmaxcall = currentCapacity['maxActiveCalls']

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
        
        response = requests.put(a.api_host+endpoint,data=json.dumps(data),headers=headers)
        if str(response) != '<Response [200]>':
            fileManager.fm.writeErrors(f'Group.increaseCallCapacity.PUT - maxActiveCalls: {currentmaxcall + channels}')
        return response.json()

    def getCallCapacity(self, a): # gets current call capacity used for above method
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