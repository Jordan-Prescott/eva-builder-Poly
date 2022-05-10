from math import trunc
import string
from random import randint, choice
import getpass
import logging
from types import BuiltinMethodType
import requests
import json
'''
EVA builder to automate the build of EVA SIP Trunk instances
'''

#####
#
# Global Variable Declaration
#
#####

region = ""
api_host = ""
username = ""
password = ""
serviceProviderID = ""
groupID = ""
evaAgentType = ""
evaAgentCount = ""
primaryPilotNumber = ""
groupDomain = ""
token = ""
internalcalls = False
externalcalls = False

####
#
# Class Constructors
#
####

class EnterpriseTrunk: # Builds Enterprise/ Service Provider Trunks 
    def __init__(self, isEnterprise=None):
        # sets class variable to determine if this build is for an enterprise or service provider
        if getEntType(serviceProviderID) == "enterprise":
            self.isEnterprise = True
        elif getEntType(serviceProviderID) == "serviceprovider":
            self.isEnterprise = False

    def buildTrunk(self):
        # builds enterprise trunk if this build is for an enterprise    
        if self.isEnterprise == True:
            endpoint = "/service-providers/enterprise-trunks"
            headers = {
                "Authorization": "Bearer "+getToken(),
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "maximumRerouteAttempts":5,
                "routeExhaustionAction": "None",
                "orderedRouting": {
                    "orderingAlgorithm": "Overflow"
                },
                "capacityManagement": {
                    "maximumActiveCalls":4,
                    "enabled": True
                },
                "serviceProviderId": serviceProviderID,
                "enterpriseTrunkName": groupID+"_EVA", # built in the enterprise 
                "trunkGroups": [] # empty as these are built in the group not at enterprise level
            })
            response = requests.post(api_host+endpoint, headers=headers, data=data)
            return response.json()

        # builds service provider trunk if this build is for a service provider
        elif self.isEnterprise == False:
            endpoint = "/groups/enterprise-trunks"
            headers = {
                "Authorization": "Bearer "+getToken(),
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "serviceProviderId":serviceProviderID,
                "groupId":groupID,
                "maximumRerouteAttempts":5,
                "routeExhaustionAction": "None", # added as it was throwing an error
                "orderedRouting": {
                    "orderingAlgorithm": "Overflow"
                },
                # enterprise trunk and trunk groups are built at group level in the SP
                "enterpriseTrunkName":groupID+"_EVA",
                "trunkGroups": [
                    {
                        "groupId": groupID,
                        "trunkGroupName": "EVA_Primary"
                    },
                    {
                        "groupId": groupID,
                        "trunkGroupName": "EVA_Secondary"
                    }
                ]
            })

            # api request to create trunk
            response = requests.post(api_host+endpoint,headers=headers,data=data)
            return response.json()

    def addUsersToEnterpriseTrunk(self, pilot1, pilot2):
        # adds users to the trunk if this build is for an enterprise
        if self.isEnterprise == True:
            endpoint = "/service-providers/enterprise-trunks/users"
            headers = {
                "Authorization": "Bearer {}".format(getToken()),
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "serviceProviderId":serviceProviderID,
                "enterpriseTrunkName":groupID+"_EVA",
                "users":[
                    {"userId":pilot1},
                    {"userId":pilot2}
                ]
            })

            response = requests.post(api_host+endpoint,headers=headers,data=data)
            return response.json()
        
        # adds users to the trunk if this build is for a service provider
        if self.isEnterprise == False:
            endpoint = "/groups/enterprise-trunks/users"
            headers = {
                "Authorization": "Bearer {}".format(getToken()),
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "serviceProviderId":serviceProviderID,
                "groupId" : groupID,
                "enterpriseTrunkName":groupID+"_EVA",
                "users":[
                    {"userId":pilot1},
                    {"userId":pilot2}
                ]
            })

            # api request to create trunk 
            response = requests.post(api_host+endpoint,headers=headers,data=data)
            return response.json()

class TrunkUser: # Builds EVA Trunk Users
    def __init__(self, number, agentType, isPilot, trunk=None, userId=None, password=None):
        self.number = number
        self.type = agentType
        self.isPilot = isPilot
        self.trunk = trunk
        self.userId = userId
        self.password = generatePassword()

    # api request to create EVA user 
    def buildUser(self):
        endpoint = "/users"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type":"application/json"
        }
        payload = {
            "userId": self.userId,
            "lastName": "EVA_Agent_"+str(self.number),
            "callingLineIdFirstName": groupID,
            "callingLineIdLastName": "EVA_Agent_"+str(self.number),
            "firstName": groupID,
            "password": self.password,
            "serviceProviderId": serviceProviderID,
            "groupId": groupID
        }
        # sets name accordingly in api request for purpose 
        if self.trunk == "externaloflow":
            payload["lastName"] = "External Overflow"
            payload["callingLineIdLastName"] = "External Overflow"
        elif self.trunk == "internaloflow":
            payload["lastName"] = "Internal Overflow"
            payload["callingLineIdLastName"] = "Internal Overflow"
            
        # api request to create trunk user
        response = requests.post(api_host+endpoint, headers=headers, data=json.dumps(payload))
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

class SipTrunk: # Builds group sip trunks 
    def __init__(self, trunkType, username=None, password=None):
        self.type = trunkType
    
    def buildTrunk(self): # depending on type sets class attributes to correct values
        if self.type == "primary":
            trunkName = "EVA_Primary"
            self.username = trunkName+"@"+groupDomain
            deviceName = "EVA_Primary_Trunk"
        elif self.type == "secondary":
            trunkName = "EVA_Secondary"
            self.username = trunkName+"@"+groupDomain
            deviceName = "EVA_Secondary_Trunk"
        elif self.type == "externaloflow":
            trunkName = "EVA_ExternalOverflow"
            self.username = trunkName+"@"+groupDomain
            deviceName = "EVA_ExternalOverflow"
        elif self.type == "internaloflow":
            trunkName ="EVA_InternalOverflow"
            self.username = trunkName+"@"+groupDomain
            deviceName = "EVA_InternalOverflow"

        # geneerate random password for authentication details
        self.password = generatePassword()

        endpoint = "/groups/trunk-groups"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        payload = { # data to be sent to API
            "name": trunkName,
            "serviceProviderId": serviceProviderID,
            "groupId": groupID,
            "maxActiveCalls": evaAgentCount,
            "enableBursting": True,
            "burstingMaxActiveCalls": 1,
            "requireAuthentication": True,
            "sipAuthenticationUserName": trunkName,
            "sipAuthenticationPassword": self.password,
            "trunkGroupIdentity": trunkName+"@"+groupDomain,
            "allowUnscreenedCalls": True,
            "accessDevice":{
                "serviceProviderId":serviceProviderID,
                "groupId":groupID,
                "deviceName":deviceName,
                "deviceLevel":"Group"
            },
            "capacityExceededTrapInitialCalls":0,
            "capacityExceededTrapOffsetCalls":0,
            "invitationTimeout":6,
            "pilotUserCallingLineIdentityForExternalCallsPolicy": "No Calls",
            "pilotUserChargeNumberPolicy": "No Calls",
            "continuousOptionsSendingIntervalSeconds":30,
            "failureOptionsSendingIntervalSeconds":10,
            "failureThresholdCounter":1,
            "successThresholdCounter":1,
            "inviteFailureThresholdCounter":1,
            "inviteFailureThresholdWindowSeconds":30,
            "pilotUserCallingLineAssertedIdentityPolicy": "All Originating Calls",
            "pilotUserCallOptimizationPolicy": "Optimize For User Services",
            "clidSourceForScreenedCallsPolicy":"Received Name Profile Number",
            "userLookupPolicy": "Basic",
            "pilotUserCallingLineIdentityForEmergencyCallsPolicy": "No Calls"
        }

        # adjusts call limit depending on type of trunk (only for internal and external overflow)
        if self.type == "externaloflow" or self.type == "internaloflow":
            payload["maxActiveCalls"] = 1
            payload["enableBursting"] = False
            payload["burstingMaxActiveCalls"] = 0

        # API call
        response = requests.post(api_host+endpoint,data=json.dumps(payload),headers=headers)
        return response.json()

class Enterprise: # adjust call capacity of enterprise trunk
    def __init__(self, ID, type):
        self.ID = ID
        self.type = type
    
    def authoriseService(self):
        return None ## ???

    def increaseCallCapacity(self, channels, bursting=0):
        currentCapacity = self.getCallCapacity() # calls method below and collects current capacity
        currentmaxcall = currentCapacity['maxActiveCalls'] # gets current max call capacity
        currentbursting = currentCapacity['burstingMaxActiveCalls'] # gets current bursting capacity

        if currentbursting == -1: # if no bursting capacity set to 0 
            currentbursting = 0
        
        endpoint = "/service-providers/trunk-groups/call-capacity"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "maxActiveCalls": currentmaxcall + channels,
            "serviceProviderId": self.ID
        }
        
        if bursting != 0: # if bursting capacity is set (passed into method increaseCallCapacity)
            data["burstingMaxActiveCalls"] = currentbursting + bursting

        # API call
        response = requests.put(api_host+endpoint,data=json.dumps(data),headers=headers) # PUT request so it uses payload to identify which group to adjust
        return response.json()

    # returns current call capacity used for above method
    def getCallCapacity(self):
        endpoint = "/service-providers/trunk-groups/call-capacity?serviceProviderId="+self.ID
        headers = {
            "Authorization": "Bearer "+getToken()
        }
        data = {
        }
        response = requests.get(api_host+endpoint,data=data,headers=headers)
        return response.json()

class ServiceProvider: # service provider class, just an instance of SP
    def __init__(self, ID, type):
        self.ID = ID
        self.type = type
    
    def authoriseService(self): ## ???
        return None

class Group: # builds group devices and adjusts trunk call capacity
    def __init__(self, enterpriseID, groupID):
        self.enterpriseID = enterpriseID
        self.groupID = groupID
        self.getDefaultDomain()

    def getDefaultDomain(self): # gets default domain for group
        global groupDomain
        endpoint = "/groups?serviceProviderId=" + self.enterpriseID + "&groupId="+self.groupID
        headers = {
            "Authorization":"Bearer "+getToken()
        }
        payload = {
        }

        # API call
        response = requests.get(api_host+endpoint, headers=headers, data=payload)
        
        # sets global groupDomain to default domain
        groupDomain = response.json()['defaultDomain']
        
    def buildHuntGroup(self): ## ???
        return None

    def createPrimaryDevice(self): # creates primary inference-sbc device
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        payload = {
            "deviceType": "Inference-sbc",
            "deviceName": "EVA_Primary_Trunk",
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        # API call
        response = requests.post(api_host+endpoint, data=json.dumps(payload), headers=headers)
        return response.json()
    
    def createSecondaryDevice(self): # creates secondary inference-sbc device
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        payload = {
            "deviceType": "Inference-sbc",
            "deviceName": "EVA_Secondary_Trunk",
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        # API call
        response = requests.post(api_host+endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

    def createInternalOverflowDevice(self): # creates internal overflow inference-sbc device
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        payload = {
            "deviceType": "Inference-sbc",
            "deviceName": "EVA_InternalOverflow",
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        # API call
        response = requests.post(api_host+endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

    def createExternalOverflowDevice(self): # creates external overflow inference-sbc device
        endpoint = "/groups/devices"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json" 
        }
        payload = {
            "deviceType": "Inference-sbc",
            "deviceName": "EVA_ExternalOverflow",
            "deviceLevel": "Group",
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }

        # API call
        response = requests.post(api_host+endpoint, data=json.dumps(payload), headers=headers)
        return response.json()


    # increases call capacity for trunk groups 
    def increaseCallCapacity(self, channels, bursting=0): # increases call capacity of group
        currentCapacity = self.getCallCapacity()
        currentmaxcall = currentCapacity['maxActiveCalls']
        currentbursting = currentCapacity['burstingMaxActiveCalls']

        endpoint = "/groups/trunk-groups/call-capacity"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "maxActiveCalls": currentmaxcall + channels,
            "serviceProviderId": self.enterpriseID,
            "groupId": self.groupID
        }
        if bursting != 0:
            data["burstingMaxActiveCalls"] = currentbursting + bursting
        
        # API call
        response = requests.put(api_host+endpoint,data=json.dumps(data),headers=headers) # PUT request so uses the payload to identify the trunk group
        return response.json()

    # gets current call capacity used for above method
    def getCallCapacity(self):
        endpoint = "/groups/trunk-groups/call-capacity?groupId="+self.groupID+"&serviceProviderId="+self.enterpriseID 
        headers = {
            "Authorization": "Bearer "+getToken()
        }
        data = {
        }

        # API call
        response = requests.get(api_host+endpoint,data=data,headers=headers)
        return response.json()    

class HuntGroup: # creates hunt groups in group
    def __init__(self, type):
        self.type = type

    
    def buildHG(self, extension): # builds the two huntgroups for the group
        endpoint = "/groups/hunt-groups"
        headers = {
            "Authorization": "Bearer "+getToken(),
            "Content-Type": "application/json"
        }
        data = {
            "serviceInstanceProfile": {
                "callingLineIdFirstName": "EVA",
                "extension": extension,
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
            "serviceProviderId": serviceProviderID,
            "groupId": groupID,
        }

        # looks at the type of huntgroup and sets the data accordingly for external and internal calls 
        if self.type == "externaloflow": # external group
            data["serviceInstanceProfile"]["name"] = "EVA External"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "External"
            data["serviceUserId"] = "EVA_External_HG@"+groupDomain
            data["agents"] = [
                {"userId":"EVA_Agent_"+str(primaryPilotNumber)+"@"+groupDomain},
                {"userId":"EVA_ExternalOverflow@"+groupDomain}
            ]
        elif self.type == "internaloflow": # internal group
            data["serviceInstanceProfile"]["name"] = "EVA Internal"
            data["serviceInstanceProfile"]["callingLineIdLastName"] = "Internal"
            data["serviceUserId"] = "EVA_Internal_HG@"+groupDomain
            data["agents"] = [
                {"userId":"EVA_Agent_"+str(primaryPilotNumber + 1)+"@"+groupDomain},
                {"userId":"EVA_InternalOverflow@"+groupDomain}
            ]

        # API call
        response = requests.post(api_host+endpoint, headers=headers, data=json.dumps(data))
        return response.json()
####
#
# Global Functions
#
####

def getToken(): # gets the token from the API
    global token
    if token == "": # checks if the token is already set
        endpoint = "/auth/token"
        payload = {
            "username": username,
            "password": password
        }

        # API call
        response = requests.post(api_host+endpoint, data=payload)
        token = response.json()["token"]
        return token # retyurns the token
    else:
        return token # returns the token if it is already set

def setAPIHost(region): # sets the API host based on the region
    global api_host
    if region == "EU": # sets the API host to the EU region
        api_host = "https://fourteenip-eu.prod.odinapi.net/api/v2"
        logging.debug("EU region selected. Using " + api_host)
    elif region == "US": # sets the API host to the US region
        api_host = "https://fourteenip.prod.odinapi.net/api/v2"
        logging.debug("US region selected. Using " + api_host)

def getEntType(serviceProviderID): # gets the enterprise type - important for how trunks are built
    endpoint = "/service-providers?serviceProviderId="+serviceProviderID
    headers = {
        "Authorization":"Bearer "+getToken()
    }
    payload = {
    }

    # API call
    response = requests.get(api_host+endpoint, headers=headers, data=payload)
    isEnterprise = response.json()['isEnterprise']
    if isEnterprise:
        return "enterprise"
    elif not isEnterprise:
        return "serviceprovider"
    
def generatePassword(): # generates a random password for the user
    characters = string.ascii_letters + string.punctuation + string.digits + string.ascii_uppercase
    password = "".join(choice(characters) for x in range(randint(8,16)))
    return password

def displayInputs(): # displays the inputs for the user
    print("[1] Region: " + region.upper())
    print("[2] Service Provider ID: " + serviceProviderID)
    print("[3] Group ID: " + groupID)
    print("[4] Inernal Calls: " + str(internalcalls))
    print("[5] External Calls: " + str(externalcalls))
    print("[6] Primary Pilot Number: " + str(primaryPilotNumber))
    print("[7] Agent Count: " + str(evaAgentCount))
    print("[8] Agent Type: " + evaAgentType + "\n")

def main(): # main function

    # sets all below to global variables so they can be used in other functions
    global region
    global api_host
    global username
    global password
    global serviceProviderID
    global groupID
    global evaAgentCount
    global evaAgentType
    global primaryPilotNumber
    global internalcalls
    global externalcalls
    
     
    # prints to terminal
    print("### Eva Builder Python App ###\n")
    
    # Input Capture and Store

    # takes in region and then calls setAPIHost() to set the API host depending on region
    region = input("Choose system [EU/US]: ")
    setAPIHost(region.upper())

    # takes in username used to log into magic   
    username = input("\nUsername: ") ## error check later
    logging.debug("Username captured")

    # takes in password used to log into magic
    password = getpass.getpass() # hides password ## error check later
    #password = input("Password: ")
    logging.debug("Password captured")
    
    # takes in serviceProviderID
    serviceProviderID = str(input("\nService Provider or Enterprise ID: "))

    # takes in groupID
    groupID = str(input("Group ID: "))

    # confirms internal use and if yes sets internalcalls to true
    menuchoice = str(input("\nWill EVA be used for internal calls? (y/n): "))
    if menuchoice == "y":
        internalcalls = True

    # confirms external use and if yes sets externalcalls to true
    menuchoice = str(input("Will EVA be used for external calls? (y/n): "))
    if menuchoice == "y":
        externalcalls = True

    # takes in pilot number
    primaryPilotNumber = int(input("\nPrimary Pilot Number: "))

    # takes in number of agents
    evaAgentCount = int(input("Agent Count (Including Pilots): "))

    # takes in agent type (different for SIP Trunk/ EV)
    evaAgentType = str(input("\nAgent Type [EVA-SVANL / EVA-VANL]: "))

    #input validation
    print("\nInput Validation:" + "\nREMINDER: Magic is case sensitive" + "\n")
    displayInputs()
    menuChoice = str(input("Is all data correct? (y/n): "))

    if menuChoice == "n": # input validation to confirm the data is correct and no errors are thrown or wrong endpoint is chosen

        print('\nSelect number to change entry') # shows user how to adjust an entry

        while True:
            numberChoice = str(input("\nNumber: ")) # takes in entry number user would like to adjust
            
            if numberChoice == "1":
                region = input("\nChoose system [EU/US]: ")
                setAPIHost(region.upper())
            elif numberChoice == "2":
                serviceProviderID = str(input("Service Provider or Enterprise ID: "))
            elif numberChoice == "3":
                groupID = str(input("Group ID: "))
            elif numberChoice == "4":
                menuchoice = str(input("Will EVA be used for internal calls? (y/n): "))
                if menuchoice == "y":
                    internalcalls = True
            elif numberChoice == "5":
                menuchoice = str(input("Will EVA be used for external calls? (y/n): "))
                if menuchoice == "y":
                    externalcalls = True
            elif numberChoice == "6":
                primaryPilotNumber = int(input("Primary Pilot Number: "))
            elif numberChoice == "7":
                evaAgentCount = int(input("Agent Count (Including Pilots): "))
            elif numberChoice == "8":
                evaAgentType = str(input("Agent Type [SIP-VANL / EVA-VANL]: "))
            else:
                print("\nInvalid Input") 

            menuChoice = input('\nAdjust another entry? (y/n): ') # asks user if they want to change another entry

            if menuChoice == 'n': # break the while loop and print the inputs a final time
                logging.debug('User input validated')
                displayInputs()
                break   
    elif menuChoice == 'y':
        print('\nStarted script')
        logging.debug('User input validated') ## need to change so the output is not printed to the terminal

    # Create Enterprise or Service Provider Class
    if getEntType(serviceProviderID) == "enterprise": # calls getEntType() to determine if serviceProviderID is an enterprise if so, create an Enterprise object
        enterprise = Enterprise(serviceProviderID, "enterprise")
    elif getEntType(serviceProviderID) == "serviceprovider": # calls getEntType() to determine if serviceProviderID is a service provider if so, create a ServiceProvider object.
        enterprise = ServiceProvider(serviceProviderID, "serviceprovider")
            
    # Create Group Class
    group = Group(serviceProviderID, groupID)

    # If enterprise, increate enterprise trunking call capacities
    if enterprise.type == "enterprise":
        print("Increasing Enterprise Trunking Call Capacity")
        logging.debug("Increasing enterprise trunking call capacity")
        enterprise.increaseCallCapacity(evaAgentCount + 1, 2)

    # Create Group Devices
    group.createPrimaryDevice() # calls group method and build primary device
    print("Creating primary trunk device")
    group.createSecondaryDevice() # calls group method and build secondary device
    print("Creating secondary trunk devices")
    logging.debug("Trunking devices created") ## error check later
    if externalcalls: # if external calls are being used, create external devices
        group.createExternalOverflowDevice() 
        print("Creating External Overflow Device")
    if internalcalls: # if internal calls are being used, create internal devices
        group.createInternalOverflowDevice()
        print("Creating Internal Overlfow Device")

    # Increase group trunking call capacities
    group.increaseCallCapacity(evaAgentCount, 2)
    print("Increasing group trunking call capacity")
    logging.debug("Increasing group trunking call capacity")

    # Create trunk group classes
    primaryTrunk = SipTrunk("primary")
    secondaryTrunk = SipTrunk("secondary")

    # Build Trunk Groups
    print("Building sip trunks...")
    primaryTrunk.buildTrunk()
    secondaryTrunk.buildTrunk()
    print("sip trunks built")


    # Create Users
    print("Building users")
    # empty list to store user objects
    users = []

    # creates user objects and adds them to the list
    for x in range(primaryPilotNumber, primaryPilotNumber + (evaAgentCount)):
        user_id = "EVA_Agent_"+str(x)+"@"+groupDomain
        users.append(TrunkUser(x,evaAgentType.upper(), False, userId=user_id))
    # sets first two users as pilot     
    users[0].isPilot = True
    users[1].isPilot = True

    ##review
    for user in users:
        user.trunk = "primary"
    users[1].trunk = "secondary"

    # builds user objects 
    for user in users:
        user.buildUser()
        user.assignServicePack()
        user.setAuthenticationPass()
        user.setExtensionNumber()
        user.assigntoTrunk()
        if user.isPilot:
            user.setPilot()
        print("   Built user "+str(user.number))
        
    # build enterprise trunk
    entTrunk = EnterpriseTrunk() # new object for enterprise trunk
    print("Building Enterprise trunk")
    entTrunk.buildTrunk()
    print("Adding users to enterprise trunk")
    entTrunk.addUsersToEnterpriseTrunk("EVA_Agent_"+str(primaryPilotNumber)+"@"+groupDomain, "EVA_Agent_"+str(primaryPilotNumber+1)+"@"+groupDomain)

    
    # build internal / external overflow TGs ##review
    if externalcalls:
        externaloflow = SipTrunk("externaloflow")
        externaloflow.buildTrunk()
    if internalcalls:
        internaloflow = SipTrunk("internaloflow")
        internaloflow.buildTrunk()

    # build internal / external overflow users
    if externalcalls: # if external calls are being used, create external overflow users
        extoflowuser = TrunkUser(primaryPilotNumber-1,"SIP-DID",True,"externaloflow", userId="EVA_ExternalOverflow@"+groupDomain)
        extoflowuser.buildUser()
        extoflowuser.assignServicePack()
        extoflowuser.setAuthenticationPass()
        extoflowuser.setExtensionNumber()
        extoflowuser.assigntoTrunk()
        extoflowuser.setPilot()
        print("   Built external overflow user")

    if internalcalls: # if internal calls are being used, create internal overflow users
        intoflowuser = TrunkUser(primaryPilotNumber-2,"SIP-DID", True, "internaloflow", userId="EVA_InternalOverflow@"+groupDomain)
        intoflowuser.buildUser()
        intoflowuser.assignServicePack()
        intoflowuser.setAuthenticationPass()
        intoflowuser.setExtensionNumber()
        intoflowuser.assigntoTrunk()
        intoflowuser.setPilot()
        print("   Built internal overflow user")

    # build internal / external overflow HGs
    if internalcalls: # if internal calls, build internal overflow HG
        intOflowHG = HuntGroup("internaloflow")
        intOflowHG.buildHG("141414")
        
    
    if externalcalls: # if externa calls are being used, build external overflow HG
        extOflowHG = HuntGroup("externaloflow")
        extOflowHG.buildHG("141415")
    
    ## print outputs
    print("Build complete.")
    print("\n## Credentials ##")
    print("Primary Trunk Register Username: EVA_Agent_"+str(users[0].number))
    print("Primary Trunk Authentication Username: "+str(primaryTrunk.username))
    print("Primary Trunk Password: "+str(primaryTrunk.password))
    print("\nSecondary Trunk Register Username: EVA_Agent_"+str(users[1].number))
    print("Secondary Trunk Authentication Username: "+str(secondaryTrunk.username))
    print("Secondary Trunk Password: "+str(secondaryTrunk.password))
    

if __name__ == "__main__":

    # outputs logs into file below
    logging.basicConfig(filename="evabuilder_log.txt", encoding="utf-8", level=logging.DEBUG)
    main()