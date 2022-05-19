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
        "license": "EVA-AGENT-" + str(evaAgentCount)
    },
    {
        "id": "141402_EVA_IL",
        "extension": "141402",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID"
    },
    {
        "id": "141403_EVA_ES",
        "extension": "141403",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID"
    },
    {
        "id": "141404_EVA_IS",
        "extension": "141404",
        "trunk": "EVA_Poly",
        "pilot": False,
        "license": "SIP-DID"
    },
    {
        "id": "141412_EVA_EOF",
        "extension": "141412",
        "trunk": "EVA_ExternalOverflow",
        "pilot": True,
        "license": "SIP-DID"
    },
    {
        "id": "141413_EVA_IOF",
        "extension": "141413",
        "trunk": "EVA_InternalOverflow",
        "pilot": True,
        "license": "SIP-DID"
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
    evaAgentCount = int((input("\nAgent Count (Including Pilots): ")))
    users[0]['license'] = "EVA-AGENT-" + str(evaAgentCount)
    menuchoice = input("Will busrting be used? (y/n): ")
    if menuchoice == "y":
        burstingCount = int((input("    Please enter how many bursting channels are needed: ")))

    #input validation
    print("\nInput Validation:" + "\nREMINDER: Magic is case sensitive" + "\n")
    displayInputs(a)
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
                evaAgentCount = int((input("Agent Count (Including Pilots): ")))
            elif numberChoice == "7":
                burstingCount = int(input("Please enter how many bursting channels are needed: "))
            else:
                print("\nInvalid Input") 

            menuChoice = input('\nAdjust another entry? (y/n): ') # while control 

            if menuChoice == 'n':
                displayInputs(a)
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
        enterprise.increaseCallCapacity(evaAgentCount + burstingCount, a)

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
    g.increaseCallCapacity(evaAgentCount + burstingCount, a)
    print("Increasing group trunking call capacity")

    # Create trunk group classes
    st = SIPTrunk.sipTrunk("EVA_Poly", generatePassword(), evaAgentCount + burstingCount)
    print("Building sip trunks...")
    st.buildTrunk(g, a)

    # build internal / external overflow TGs 
    if externalcalls:
        externaloflow = SIPTrunk.sipTrunk("EVA_ExternalOverflow", generatePassword())
        externaloflow.buildTrunk(g, a)
    if internalcalls:
        internaloflow = SIPTrunk.sipTrunk("EVA_InternalOverflow", generatePassword())
        internaloflow.buildTrunk(g, a)
    print("sip trunks built")

    # Create Users
    print("Building users")
    trunkUsers = []
    for x in users:
        user_id = groupID.upper() + x['id'] + "@" + g.domain
        trunkUsers.append(TrunkUser.trunkUser(x['id'], x['extension'], x['license'], x['pilot'], user_id, x['trunk'], password = generatePassword()))

    # builds user objects 
    for u in trunkUsers:
        u.buildUser(a, g)
        u.assignServicePack(a)
        u.setAuthenticationPass(a, g)
        u.setExtensionNumber(a, g)
        u.assigntoTrunk(a, g)
        if u.isPilot:
            u.setPilot(a, g)
        print("   Built user "+str(u.id))

    if burstingCount > 0:
        trunkUsers[0].assignBurstServicePack(a, "EVA-AGENTB-" + str(burstingCount))

    # build internal / external overflow HGs
    if internalcalls: # if internal calls, build internal overflow HG
        intOflowHG = HuntGroup.hg("internaloflow", "141415")
        intOflowHG.buildHG(a, g)

        intOflowHGSB = HuntGroup.hg("internaloflowSB","141417")
        intOflowHGSB.buildHG(a, g)
        print("Internal Hunt Groups built.")
    
    if externalcalls: # if externa calls are being used, build external overflow HG
        extOflowHG = HuntGroup.hg("externaloflow", "141414")
        extOflowHG.buildHG(a, g)

        extOflowHGSB = HuntGroup.hg("externaloflowSB", "141416")
        extOflowHGSB.buildHG(a, g)
        print("External Hunt Groups built.")

    ## print outputs
    print("Build complete.")
    print("\n## Credentials ##")
    print("Primary Trunk Register Username: " + g.groupID + users[0]['id'] + "@" + g.domain)
    print("Primary Trunk Authentication Username: "+str(st.username))
    print("Primary Trunk Password: "+str(st.password))

if __name__ == "__main__":
    main()