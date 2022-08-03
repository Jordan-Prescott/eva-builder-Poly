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
externalCFA = 0
internalCFA = 0
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
def generatePassword():
    """
    Generates a random string of characters used for passwords 

    :return string: Random string of characters 
    """
    characters = string.digits + string.ascii_letters + string.digits
    password = "".join(choice(characters) for x in range(randint(8,16)))
    return password

def displayInputs(a): 
    """Displays user inputs to the terminal

    :param a: API objetc used to get the Region inputted by user
    :return: users inputs to the terminal with a number associated
    """
    print("[1] Region: " + a.region.upper()) 
    print("[2] Service Provider ID: " + serviceProviderID)
    print("[3] Group ID: " + groupID)
    print("[4] Inernal Calls: " + str(internalcalls))
    print("[5] Internal Calls Overflow: " + str(internalCFA))
    print("[6] External Calls: " + str(externalcalls))
    print("[7] Enternal Calls Overflow: " + str(externalCFA))
    print("[8] Agent Count: " + str(evaAgentCount))
    print("[9] Bursting Count: " + str(burstingCount) + "\n")

def main():
    """
    EVA Builder Script is a script to automate the Broadworks configuration for FourteenIP AI solution EVA.
    Inputs are taken with details on the group where the configuration needs to be built, the script performs a series of tasks building EVA on Broadworks.

    :company: FourteenIP
    :author: Jordan Prescott
    """

    # sets all below to global variables so they can be used in other function
    global username
    global password
    global serviceProviderID
    global groupID
    global evaAgentCount 
    global internalcalls
    global externalcalls
    global burstingCount
    global externalCFA
    global internalCFA
    
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

    serviceProviderID = str(input("\nService Provider or Enterprise ID: "))
    groupID = str(input("Group ID: "))

    menuchoice = str(input("\nWill EVA be used for internal calls? (y/n): "))
    if menuchoice == "y" or menuchoice == "Y":
        internalCFA = input("    Extension number of internal overflow: ")
        internalcalls = True
        users[1]['build'] = True
        users[3]['build'] = True
        users[5]['build'] = True

    menuchoice = str(input("Will EVA be used for external calls? (y/n): "))
    if menuchoice == "y" or menuchoice == "Y":
        externalCFA = input("    Extension number of external overflow: ")
        externalcalls = True
        
    # takes in number of channels and this will affect license appiled later
    evaAgentCount = int((input("\nAgent Count (Including Pilots): ")))
    users[0]['license'] = "EVA-AGENT-" + str(evaAgentCount)
    menuchoice = input("Will bursting be used? (y/n): ")
    if menuchoice == "y" or menuchoice == "Y":
        burstingCount = int((input("    Please enter how many bursting channels are needed: ")))

    #input validation
    print("\nInput Validation:" + "\nREMINDER: Magic is case sensitive" + "\n")
    displayInputs(a)
    menuChoice = str(input("Is all data correct? (y/n): "))

    if menuChoice == "n" or menuChoice == "N": # input validation to confirm the data is correct and no errors are thrown or wrong endpoint is chosen

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
                    users[1]['build'] = True
                    users[3]['build'] = True
                    users[5]['build'] = True
            elif numberChoice == "5":
                internalCFA = input("Extension number of internal overflow: ")
            elif numberChoice == "6":
                menuchoice = str(input("Will EVA be used for external calls? (y/n): "))
                if menuchoice == "y":
                    externalcalls = True
            elif numberChoice == "7":
                externalCFA = input("Extension number of external overflow: ")
            elif numberChoice == "8":
                evaAgentCount = int((input("Agent Count (Including Pilots): ")))
            elif numberChoice == "9":
                burstingCount = int(input("Please enter how many bursting channels are needed: "))
            else:
                print("\nInvalid Input") 

            menuChoice = input('\nAdjust another entry? (y/n): ') # while control 

            if menuChoice == 'n':
                displayInputs(a)
                break   
    elif menuChoice == 'y' or menuChoice == 'Y':
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
        enterprise.increaseCallCapacity(evaAgentCount, a, burstingCount)

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
    print("Increasing group trunking call capacity")
    g.increaseCallCapacity(evaAgentCount, a, burstingCount)

    # Create trunk group classes
    st = SIPTrunk.sipTrunk("EVA_Poly", generatePassword(), burstingCount, evaAgentCount)
    print("Building sip trunks...")
    st.buildTrunk(g, a)

    # build internal / external overflow TGs 
    if externalcalls:
        externaloflow = SIPTrunk.sipTrunk("EVA_ExternalOverflow", generatePassword(), externalCFA)
        externaloflow.buildTrunk(g, a)
    if internalcalls:
        internaloflow = SIPTrunk.sipTrunk("EVA_InternalOverflow", generatePassword(), internalCFA)
        internaloflow.buildTrunk(g, a)
    print("sip trunks built")

    # Create Users
    print("Building users")
    trunkUsers = []
    for x in users:
        if x['build'] == True:
            user_id = groupID + x['id'] + "@" + g.domain
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
    print("Primary Trunk Password: "+str(st.password) +"\n")
    print("Errors can be found in: lib/errors.txt")

if __name__ == "__main__":
    main()