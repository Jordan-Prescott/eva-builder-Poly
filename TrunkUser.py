#TrunkUser Class
#imports
import requests
import json

#classes
import fileManager
class trunkUser: 
    '''trunkUser class - builds user and assigned to trunk, user details are stored in users {dict} in evabuilder-Poly'''
    def __init__(self, id, number, agentType, isPilot, userId, trunk, password):
        ''' 
        
        Hierachy: Ent/SP > Group > User
        
        variables:
        id(unique id, start of userId), number(extension number), agentType(license assigned), isPilot(Boolean on if user is pilot), userId(unique userid of user), trunk(trunk user belongs to), password(authenticatoion password)
        '''
        super().__init__()
        
        self.id = id
        self.number = number
        self.type = agentType
        self.isPilot = isPilot
        self.trunk = trunk
        self.userId = userId
        self.password = password

    def buildUser(self, a, g):
        '''
        builds 141401_EVA_EL, 141402_EVA_IL, 141403_EVA_ES, 141404_EVA_IS, 141412_EVA_EOF, 141413_EVA_IOF

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from POST request
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.buildUser.POST || {self.userId} || {error}')
        return response.json()
    
    def assigntoTrunk(self, a, g):
        '''
        assigns the user to the correct trunk

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from PUT request
        '''
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
            }
        }

        if self.trunk == "EVA_InternalOverflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_InternalOverflow@"+str(g.domain)
        if self.trunk == "EVA_ExternalOverflow":
            data["trunkAddressing"]["trunkGroupDeviceEndpoint"]["linePort"] = "EVA_ExternalOverflow@"+str(g.domain)
            

        # API call
        response = requests.put(a.api_host+endpoint, headers=headers, data=json.dumps(data))
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.assigntoTrunk.PUT || {self.userId} || {trunkGroup} || ')
        return response.json()
    
    def assignServicePack(self, a):
        '''
        assigns EVA-AGENT-X service pack to each user

        :param a: API object used for api calls
        :return: response from PUT request
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.assignServicePack.PUT || {self.userId} || {self.type.upper()} || {error}')
        return response.json()

    def assignBurstServicePack(self, a, b):
        '''
        assigns EVA-AGENTB-X service pack to each user

        :param a: API object used for api calls
        :param b: bursting servicepack 
        :return: response from PUT request
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.assignBurstServicePack.PUT || {self.userId} || {b.upper()} || {error}')
        return response.json()

    def setAuthenticationPass(self, a, g):
        '''
        sets authentication password of users

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from PUT request
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.setAuthenticationPass.PUT || {self.userId} || {self.password} || {error}')
        return response.json()
        
    def setExtensionNumber(self, a, g):
        '''
        sets the users extension number

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from POST request        
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.setExtensionNumber.PUT || {self.userId} || {self.number} || {error}')
        return response.json()

    def setPilot(self, a, g):
        '''
        sets a pilot user to the trunk group, pilots below:
            141401_EVA_EL
            141412_EVA_EOF
            141413_EVA_IOF

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: response from PUT request
        '''
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
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'TrunkUser.setPilot.PUT || {self.userId} || {error}')
        return response.json()

    def __repr__(self) -> str:
        return f"ID: {self.id}, Extension: {self.number}, Type: {self.type}, Pilot: {self.isPilot}, Trunk: {self.trunk}, UserID: {self.userId}, Password: {self.password}"