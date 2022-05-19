#TrunkUser Class
#imports
import requests
import json

class trunkUser: # Builds EVA Trunk Users
    '''trunkUser class - user object built againts a trunk'''
    def __init__(self, id, number, agentType, isPilot, userId, trunk, password):
        '''init variables'''
        super().__init__()
        
        self.id = id
        self.number = number
        self.type = agentType
        self.isPilot = isPilot
        self.trunk = trunk
        self.userId = userId
        self.password = password

    def buildUser(self, a, g): # builds user 
        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type":"application/json"
        }
        payload = {
            "userId": self.userId,
            "lastName": self.id,
            "callingLineIdFirstName": g.groupID,
            "callingLineIdLastName": self.id,
            "firstName": g.groupID,
            "password": self.password,
            "serviceProviderId": g.enterpriseID,
            "groupId": g.groupID
        }
        
        response = requests.post(a.api_host+endpoint, headers=headers, data=json.dumps(payload))
        return response.json()
    
    def assigntoTrunk(self, a, g):
        if self.trunk == "EVA_Poly":
            trunkGroup = "EVA_Poly"
        elif self.trunk == "EVA_ExternalOverflow":
            trunkGroup = "EVA_ExternalOverflow"
        elif self.trunk == "EVA_InternalOverflow":
            trunkGroup = "EVA_InternalOverflow"

        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "serviceProviderID": str(g.enterpriseID),
            "groupId": str(g.groupID),
            "userId": str(self.userId),
            "endpointType": "trunkAddressing",
            "trunkAddressing": {
                "trunkGroupDeviceEndpoint": {
                    "name": trunkGroup,
                    "linePort": g.groupID+self.id+"@"+str(g.domain),
                    "staticRegistrationCapable": False,
                    "useDomain": True,
                    "isPilotUser": False,
                    "contacts": []
                },
                "alternateTrunkIdentity": self.number
            }
        }

        if self.trunk == "EVA_InternalOverflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_InternalOverflow@"+str(g.domain)
            del data["trunkAddressing"]["alternateTrunkIdentity"]
        if self.trunk == "EVA_ExternalOverflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_ExternalOverflow@"+str(g.domain)
            del data["trunkAddressing"]["alternateTrunkIdentity"]

        # API call
        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(data))
        return response.json()
    
    def assignServicePack(self, a):
        endpoint = "/users/services"
        headers = {
            "Authorization": "Bearer "+a.token,
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

        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(body))
        return response.json()

    def assignBurstServicePack(self, a, b):
        endpoint = "/users/services"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        body = {
            "userId": str(self.userId),
            "servicePackServices": [
                {
                    "serviceName": str(b.upper()),
                    "assigned": True
                }
            ]
        }

        # API call
        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(body))
        return response.json()

    def setAuthenticationPass(self, a, g):
        endpoint = "/users/authentication"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "userId": str(self.userId),
            "userName": g.groupID + self.id,
            "newPassword": str(self.password)
        }

        response = requests.put(a.api_host+endpoint,headers=headers,data=json.dumps(data))
        return response.json()
        
    def setExtensionNumber(self, a, g):
        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "userId": str(self.userId),
            "serviceProviderId": str(g.enterpriseID),
            "groupId": str(g.groupID),
            "extension": str(self.number)
        })
        response = requests.put(a.api_host+endpoint,headers=headers,data=data)
        return response.json()

    def setPilot(self, a, g):
        endpoint = "/groups/trunk-groups"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        data = {
            "serviceProviderId": str(g.enterpriseID),
            "groupId": str(g.groupID),
            "pilotUserId": str(self.userId),
        }
        if self.trunk == "EVA_Poly":
            data["name"] = "EVA_Poly"
        elif self.trunk == "EVA_InternalOverflow":
            data["name"] = "EVA_InternalOverflow"
        elif self.trunk == "EVA_ExternalOverflow":
            data["name"] = "EVA_ExternalOverflow"

        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(data))
        return response.json()

    def __repr__(self) -> str:
        return f"ID: {self.id}, Extension: {self.number}, Type: {self.type}, Pilot: {self.isPilot}, Trunk: {self.trunk}, UserID: {self.userId}, Password: {self.password}"