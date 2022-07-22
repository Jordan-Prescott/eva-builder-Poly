#import
from ast import Str
from math import trunc
import string
from random import randint, choice
import getpass
from types import BuiltinMethodType

#classes
import API
import ServiceProvider
import Enterprise
import Group
import SIPTrunk
import TrunkUser
import HuntGroup
import fileManager

#variables
username = ""
password = ""
serviceProviderID = ""
groupID = ""
evaAgentCount = 0
burstingCount = 0
groupDomain = ""
token = ""
internalcalls = False
externalcalls = False
users = [
    {
        "id": "141401_EVA_EL",
        "extension": "141401",
        "trunk": "EVA_Poly",
        "pilot": True,
        "license": "EVA-AGENT-" + str(evaAgentCount),
        "build": True
    },
    {
        "id": "141402_EVA_IL",
        "extension": "141402",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID",
        "build": False
    },
    {
        "id": "141403_EVA_ES",
        "extension": "141403",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID",
        "build": True
    },
    {
        "id": "141404_EVA_IS",
        "extension": "141404",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID",
        "build": False
    },
    {
        "id": "141412_EVA_EOF",
        "extension": "141412",
        "trunk": "EVA_ExternalOverflow",
        "pilot": True,
        "license": "SIP-DID",
        "build": True
    },
    {
        "id": "141413_EVA_IOF",
        "extension": "141413",
        "trunk": "EVA_InternalOverflow",
        "pilot": True,
        "license": "SIP-DID",
        "build": False
    }
]


#methods
def generatePassword(): # generates a random password for the user
    characters = string.digits + string.ascii_letters + string.digits
    password = "".join(choice(characters) for x in range(randint(8,16)))
    return password

def displayInputs(a): # displays the inputs for the user
    print("[1] Region: " + a.region.upper()) 
    print("[2] Service Provider ID: " + serviceProviderID)
    print("[3] Group ID: " + groupID)
    print("[4] Inernal Calls: " + str(internalcalls))
    print("[5] External Calls: " + str(externalcalls))
    print("[6] Agent Count: " + str(evaAgentCount))
    print("[7] Bursting Count: " + str(burstingCount) + "\n")

def main(): # main function

    # sets all below to global variables so they can be used in other function
    global username
    global password
    global serviceProviderID
    global groupID
    global evaAgentCount 
    global internalcalls
    global externalcalls
    global burstingCount
    
    fileManager.fm.clearErrors() #clears errors in ./lib/errors.txt from previous run

    print("### Eva Builder Python App ###\n")

    region = input("Choose system [EU/US]: ")

    # Magic creds
    username = input("\nUsername: ") 
    password = getpass.getpass()

    #create api object
    a = API.api(username, password)
    a.setAPIHost(region.upper())
    
    try:
        a.getToken()
    except KeyError:
        print('ERROR: Username or Password incorrect.')
        a.username = input("\nUsername: ") 
        a.password = getpass.getpass()
        a.getToken()

 
if __name__ == "__main__":
    main()