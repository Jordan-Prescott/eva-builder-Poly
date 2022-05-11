#API Class
#import
import requests
import json

class api:
    '''api class - api specific details as well as api calls that belong to no other class'''
    def __init__(self, username, password):
        '''init variables'''
        super().__init__()

        self.username = username
        self.password = password
        self.api_host = None
        self.token = None
    
    def setAPIHost(self, region): # sets the API host based on the region
        if region == "EU": 
            self.api_host = "https://fourteenip-eu.prod.odinapi.net/api/v2"
        elif region == "US": 
            self.api_host = "https://fourteenip.prod.odinapi.net/api/v2"

    def getToken(self): # gets the token from the API
        if self.token == None: # checks if the token is already set
            endpoint = "/auth/token"
            payload = {
                "username": self.username,
                "password": self.password
            }

            response = requests.post(self.api_host+endpoint, data=payload)
            self.token = response.json()["token"]
            return self.token
        else:
            return self.token # returns the token if it is already set

    def getEntType(self, serviceProviderID): # gets the enterprise type - important for how trunks are built
        endpoint = "/service-providers?serviceProviderId="+serviceProviderID
        headers = {
            "Authorization":"Bearer "+self.token
        }
        payload = {
        }

        response = requests.get(self.api_host+endpoint, headers=headers, data=payload)
        isEnterprise = response.json()['isEnterprise']

        if isEnterprise:
            return "enterprise"
        elif not isEnterprise:
            return "serviceprovider"

    def __repr__(self) -> str:
        return f'Username: {self.username}, Password: {self.password}, API Host: {self.api_host}, Token: {self.token}'