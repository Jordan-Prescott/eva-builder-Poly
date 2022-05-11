#import
from math import trunc
import string
from random import randint, choice
import getpass
import logging
from types import BuiltinMethodType
import requests
import json

#classes
import API
import ServiceProvider
import Enterprise
import Group
import SIPTrunk

#variables
username = ""
password = ""
serviceProviderID = ""
groupID = ""
evaAgentType = ""
evaAgentCount = ""
groupDomain = ""
token = ""
internalcalls = False
externalcalls = False

#methods
def generatePassword(): # generates a random password for the user
    characters = string.ascii_letters + string.punctuation + string.digits + string.ascii_uppercase
    password = "".join(choice(characters) for x in range(randint(8,16)))
    return password

def displayInputs(a): # displays the inputs for the user
    print("[1] Region: " + a.region.upper()) # TODO: pull from api object
    print("[2] Service Provider ID: " + serviceProviderID)
    print("[3] Group ID: " + groupID)
    print("[4] Inernal Calls: " + str(internalcalls))
    print("[5] External Calls: " + str(externalcalls))
    print("[6] Agent Count: " + str(evaAgentCount))
    print("[7] Agent Type: " + evaAgentType + "\n")

def main(): # main function

    # sets all below to global variables so they can be used in other function
    global username
    global password
    global serviceProviderID
    global groupID
    global evaAgentCount
    global internalcalls
    global externalcalls
    
    print("### Eva Builder Python App ###\n")

    region = input("Choose system [EU/US]: ")

    # Magic creds
    username = input("\nUsername: ") 
    password = getpass.getpass()

    #create api object
    a = API.api(username, password)
    a.setAPIHost(region.upper())
    a.getToken()
    

    serviceProviderID = str(input("\nService Provider or Enterprise ID: "))
    groupID = str(input("Group ID: "))

    menuchoice = str(input("\nWill EVA be used for internal calls? (y/n): "))
    if menuchoice == "y":
        internalcalls = True
    menuchoice = str(input("Will EVA be used for external calls? (y/n): "))
    if menuchoice == "y":
        externalcalls = True

    # takes in number of channels and this will affect license appiled later
    evaAgentCount = int(input("Agent Count (Including Pilots): "))

    # TODO: Check this will be dependant on licenses that Stu is still working through
    # takes in agent type (different for SIP Trunk/ EV)
    # evaAgentType = str(input("\nAgent Type [EVA-SVANL / EVA-VANL]: "))

    #input validation
    print("\nInput Validation:" + "\nREMINDER: Magic is case sensitive" + "\n")
    displayInputs()
    menuChoice = str(input("Is all data correct? (y/n): "))

    if menuChoice == "n": # input validation to confirm the data is correct and no errors are thrown or wrong endpoint is chosen

        print('\nSelect number to change entry') 

        while True:
            numberChoice = str(input("\nNumber: "))
            
            if numberChoice == "1":
                region = input("\nChoose system [EU/US]: ")
                a.setAPIHost(region.upper())
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
                evaAgentCount = int(input("Agent Count (Including Pilots): "))
            elif numberChoice == "7":
                evaAgentType = str(input("Agent Type [SIP-VANL / EVA-VANL]: "))
            else:
                print("\nInvalid Input") 

            menuChoice = input('\nAdjust another entry? (y/n): ') # while control 

            if menuChoice == 'n':
                displayInputs()
                break   
    elif menuChoice == 'y':
        print('\nStarted script')


    # Create Enterprise or Service Provider Class
    if a.getEntType(serviceProviderID) == "enterprise": 
        enterprise = Enterprise.ent(serviceProviderID, "enterprise")
    elif a.getEntType(serviceProviderID) == "serviceprovider": 
        enterprise = ServiceProvider.sPrv(serviceProviderID, "serviceprovider")
            
    # Create Group Class
    g = Group.grp(serviceProviderID, groupID)
    g.getDefaultDomain(a)

    # If enterprise, increase enterprise trunking call capacities
    if enterprise.type == "enterprise":
        print("Increasing Enterprise Trunking Call Capacity")
        enterprise.increaseCallCapacity(evaAgentCount + 1, a, 2)

    # Create Group Devices
    g.createDevice("EVA_Poly", a) 
    print("Creating EVA_Poly trunk device")  
    if externalcalls: 
        g.createDevice("EVA_ExternalOverflow", a) 
        print("Creating External Overflow Device")
    if internalcalls:
        g.createDevice("EVA_InternalOverflow", a)
        print("Creating Internal Overlfow Device")

    # Increase group trunking call capacities
    g.increaseCallCapacity(evaAgentCount, a, 2)
    print("Increasing group trunking call capacity")

    # Create trunk group classes
    sp = SIPTrunk.sipTrunk("EVA_Poly", generatePassword(a), evaAgentCount)
    print("Building sip trunks...")
    sp.buildTrunk(g, a)
    print("sip trunks built")

    # Create Users
    print("Building users")
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