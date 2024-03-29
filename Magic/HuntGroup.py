#Hunt Group Class
#import
from email.policy import Policy
from tokenize import group
from wsgiref import headers
import requests
import json

#classes
import fileManager
class hg: 
    '''hunt group class - builds internal and external hunt gruops'''
    def __init__(self, type, extension):
        '''A huntgroup is a collection of users with a virtual extension that can be called to reach all users in the group
        
        Hierachy: Ent/SP > Group > HuntGroup > User

        :variable type: External or Internal 
        :variable extension: Extension number
        '''
        super().__init__()

        self.type = type
        self.extension = extension
    
    def buildHG(self, a, g):
        '''
        builds EVA External, EVA Internal, EVA External Sandbox, EVA Internal Sandbox

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from POST request
        '''
        endpoint = "/groups/hunt-groups"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "serviceInstanceProfile": {
                "callingLineIdFirstName": "EVA",
                "extension": self.extension,
            },
            "policy": "Weighted",
            "huntAfterNoAnswer": False,
            "noAnswerNumberOfRings": 5,
            "forwardAfterTimeout": False,
            "forwardTimeoutSeconds": 0,
            "allowCallWaitingForAgents": True,
            "useSystemHuntGroupCLIDSetting": True,
            "includeHuntGroupNameInCLID": True,
            "enableNotReachableForwarding": False,
            "makeBusyWhenNotReachable": False,
            "allowMembersToControlGroupBusy": False,
            "enableGroupBusy": False,
            "applyGroupBusyWhenTerminatingToAgent": False,
            "serviceProviderId": g.enterpriseID,
            "groupId": g.groupID,
        }

        if self.type == "externaloflow": # external group
            data["serviceInstanceProfile"]["name"] = "EVA External"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "External"
            data["serviceUserId"] = "EVA_External_HG@"+g.domain
            data["agents"] = [
                {"userId":g.groupID+"141401_EVA_EL@"+g.domain}, #SATDT141401_EVA_EL@satdt.evtrunk.com
                {"userId":g.groupID+"141412_EVA_EOF@"+g.domain} #SATDT141412_EVA_EOF@satdt.evtrunk.com
            ]
        elif self.type == "internaloflow": # internal group
            data["serviceInstanceProfile"]["name"] = "EVA Internal"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "Internal"
            data["serviceUserId"] = "EVA_Internal_HG@"+g.domain
            data["agents"] = [
                {"userId":g.groupID+"141402_EVA_IL@"+g.domain}, #SATDT141402_EVA_IL@satdt.evtrunk.com
                {"userId":g.groupID+"141413_EVA_IOF@"+g.domain} #SATDT141413_EVA_IOF@satdt.evtrunk.com
            ]
        elif self.type == "internaloflowSB": # internal sandbox group
            data["serviceInstanceProfile"]["name"] = "EVA Internal Sandbox"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "Internal Sandbox"
            data["serviceUserId"] = "EVA_Internal_HG_SB@"+g.domain
            data["agents"] = [
                {"userId":g.groupID+"141404_EVA_IS@"+g.domain}

            ]
        elif self.type == "externaloflowSB": # internal group
            data["serviceInstanceProfile"]["name"] = "EVA External Sandbox"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "External Sandbox"
            data["serviceUserId"] = "EVA_External_HG_SB@"+g.domain
            data["agents"] = [
                {"userId":g.groupID+"141403_EVA_ES@"+g.domain}
            ]

        response = requests.post(a.api_host+endpoint, headers=headers, data=json.dumps(data))
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'HuntGroup.buildHG.POST || {self.type} || {error}')
        return response.json()

    def setWeight(self, a, g):
        '''
        sets the hunt groups weighting call distribution to below:

        External:
         	141401_EVA_EL: 100%
 	        141412_EVA_EOF: 0%
        
        External:
         	141402_EVA_IL: 100%
 	        141413_EVA_IOF: 0%
        
        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        '''
        endpoint = '/groups/hunt-groups/weighted-call-distribution'
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "serviceProviderId": g.enterpriseID,
            "groupId":g.groupID,
            "agents": [
                {
                    "userId": "",
                    "weight": 100
                },
                {
                    "userId": "",
                    "weight": 0
                }
            ]
        }

        if self.type == "externaloflow": # external group
            data["serviceUserId"] = "EVA_External_HG@" + g.domain
            data["agents"][0]["userId"] = g.groupID + "141401_EVA_EL@" + g.domain
            data["agents"][1]["userId"] = g.groupID + "141412_EVA_EOF@" + g.domain   
        if self.type == "internaloflow": # internal group
            data["serviceUserId"] = "EVA_Internal_HG@" + g.domain
            data["agents"][0]["userId"] = g.groupID + "141402_EVA_IL@" + g.domain
            data["agents"][1]["userId"] = g.groupID + "141413_EVA_IOF@" + g.domain  

        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(data))
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'HuntGroup.setWeight.PUT || {self.type} || {error}')
        return response.json()       

    def __repr__(self) -> str:
        return f"Type: {self.type}, Extension: {self.extension}"