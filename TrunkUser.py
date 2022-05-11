#TrunkUser Class
#imports
import requests
import json

class TrunkUser: # Builds EVA Trunk Users
    '''trunkUser class - user object built againts a trunk'''
    def __init__(self, number, agentType, isPilot, password):
        '''init variables'''
        super().__init__()

        self.number = number
        self.type = agentType
        self.isPilot = isPilot
        self.trunk = None
        self.userId = None
        self.password = password

    def buildUser(self, a, g):
        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type":"application/json"
        }
        payload = {
            "userId": self.userId,
            "lastName": "EVA_Agent_"+str(self.number),
            "callingLineIdFirstName": g.groupID,
            "callingLineIdLastName": "EVA_Agent_"+str(self.number),
            "firstName": g.groupID,
            "password": self.password,
            "serviceProviderId": g.enterpriseID,
            "groupId": g.groupID
        }
        # sets name accordingly in api request for purpose 
        if self.trunk == "externaloflow":
            payload["lastName"] = "External Overflow"
            payload["callingLineIdLastName"] = "External Overflow"
        elif self.trunk == "internaloflow":
            payload["lastName"] = "Internal Overflow"
            payload["callingLineIdLastName"] = "Internal Overflow"
            
        # api request to create trunk user
        response = requests.post(a.api_host+endpoint, headers=headers, data=json.dumps(payload))
        return response.json()
    
    def assigntoTrunk(self):
        if self.trunk == "primary":
            trunkGroup = "EVA_Primary"
        elif self.trunk == "secondary":
            trunkGroup = "EVA_Secondary"
        elif self.trunk == "externaloflow":
            trunkGroup = "EVA_ExternalOverflow"
        elif self.trunk == "internaloflow":
            trunkGroup = "EVA_InternalOverflow"

        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "serviceProviderID": str(serviceProviderID),
            "groupId": str(groupID),
            "userId": str(self.userId),
            "endpointType": "trunkAddressing",
            "trunkAddressing": {
                "trunkGroupDeviceEndpoint": {
                    "name": trunkGroup,
                    "linePort": "EVA_Agent_"+str(self.number)+"@"+str(groupDomain),
                    "staticRegistrationCapable": False,
                    "useDomain": True,
                    "isPilotUser": False,
                    "contacts": []
                },
                "alternateTrunkIdentity": self.number
            }
        }

        if self.trunk == "internaloflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_InternalOverflow@"+str(groupDomain)
            del data["trunkAddressing"]["alternateTrunkIdentity"]
        if self.trunk == "externaloflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_ExternalOverflow@"+str(groupDomain)
            del data["trunkAddressing"]["alternateTrunkIdentity"]

        # API call
        response = requests.put(api_host+endpoint, headers=headers, data=json.dumps(data))
        return response.json()
    
    def assignServicePack(self):
        endpoint = "/users/services"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        body = {
            "userId": str(self.userId),
            "servicePackServices": [
                {
                    "serviceName": str(self.type.upper()),
                    "assigned": True
                }
            ]
        }

        # API call
        response = requests.put(api_host+endpoint, headers=headers, data=json.dumps(body))
        return response.json()

    def setAuthenticationPass(self):
        endpoint = "/users/authentication"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "userId": str(self.userId),
            "userName": "EVA_Agent_"+str(self.number),
            "newPassword": str(self.password)
        }
        if self.type == "externaloflow":
            data["userName"] = "EVA_ExternalOverflow"
        elif self.type == "internaloflow":
            data["userName"] = "EVA_InternalOverflow"
        response = requests.put(api_host+endpoint,headers=headers,data=json.dumps(data))
        return response.json()
        
    def setExtensionNumber(self):
        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "userId": str(self.userId),
            "serviceProviderId": str(serviceProviderID),
            "groupId": str(groupID),
            "extension": str(self.number)
        })
        response = requests.put(api_host+endpoint,headers=headers,data=data)
        return response.json()

    def setPilot(self):
        endpoint = "/groups/trunk-groups"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "serviceProviderId": str(serviceProviderID),
            "groupId": str(groupID),
            "pilotUserId": str(self.userId),
        }
        if self.trunk == "primary":
            data["name"] = "EVA_Primary"
        elif self.trunk == "secondary":
            data["name"] = "EVA_Secondary"
        elif self.trunk == "internaloflow":
            data["name"] = "EVA_InternalOverflow"
        elif self.trunk == "externaloflow":
            data["name"] = "EVA_ExternalOverflow"

        response = requests.put(api_host+endpoint, headers=headers, data=json.dumps(data))
        return response.json()