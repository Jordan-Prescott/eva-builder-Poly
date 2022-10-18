#API Class
#import
import requests
import json

#classes
import fileManager
class api:
    '''api class - api specific details as well as api calls that belong to no other class'''
    def __init__(self, username, password):
        '''API class, sets and stores base URL, Token, Username, and Password for API calls.
    
        :variable username: magic Username
        :variable password: magic Password 
        :variable api_host: base URL
        :variable token: auth token
        :variable region: region of hotel
        '''
        super().__init__()

        self.username = username
        self.password = password
        self.api_host = None
        self.token = None
        self.region = None

    def setAPIHost(self, region):
        '''
        sets the host url for all api calls

        :param region: region where the hotel is located either US or UK
        '''
        if region == "EU": 
            self.api_host = "https://fourteenip-eu.prod.odinapi.net/api/v2"
            self.region = region
        elif region == "US": 
            self.api_host = "https://fourteenip.prod.odinapi.net/api/v2"
            self.region = region

    def getToken(self):
        '''
        gets an api token used for future api calls
        
        :return self.token: Odin API token for API requests
        '''
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

    def getEntType(self, serviceProviderID): # gets the enterprise type
        '''
        gets the enterpise type either enterprise or serviceprovider

        :param serviceProviderID: Enterprise or Serviceprovider ID inputted from user
        :return string: type 
        '''
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