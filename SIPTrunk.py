#SipTrunk Class
#import
import requests 
import json

#classes
import fileManager
class sipTrunk:
    '''sipTrunk class - builds sip trunk under the group'''
    def __init__(self, type, password, CFA = 0, burstingCount = 1, maxActiveCalls = 1):
        ''' SIP trunk is a shared link to make and receive calls and its hosted inside a group
        
        Hierachy: Ent/SP > Group > SIP Trunk > Users
        
        :variable type: type of 3 trunks
        :variable password: authentication password
        :variable burtsingCount: number of bursting channels
        :variable maxActiveCalls: number of normal channels
        '''

        self.type = type
        self.password = password
        self.CFA = CFA
        self.burstingCount = burstingCount
        self.maxActiveCalls = maxActiveCalls
    
    def buildTrunk(self, g, a):
        '''
        builds EVA_Poly, EVA_ExternalOverflow, EVA_InternalOverflow

        :param a: API object used for api calls
        :param g: Grp object used for details in api calls
        :return: reponse from POST API request
        '''
        if self.type == "EVA_Poly":
            trunkName = "EVA_Poly"
            self.username = trunkName+"@"+g.domain
            deviceName = "EVA_Poly"
        elif self.type == "EVA_ExternalOverflow":
            trunkName = "EVA_ExternalOverflow"
            self.username = trunkName+"@"+g.domain
            deviceName = "EVA_ExternalOverflow"
        elif self.type == "EVA_InternalOverflow":
            trunkName ="EVA_InternalOverflow"
            self.username = trunkName+"@"+g.domain
            deviceName = "EVA_InternalOverflow"

        endpoint = "/groups/trunk-groups"
        headers = {
            "Authorization": "Bearer "+a.token,
            "Content-Type": "application/json"
        }
        payload = { # data to be sent to API
            "name": trunkName,
            "serviceProviderId": g.enterpriseID,
            "groupId": g.groupID,
            "maxActiveCalls": self.maxActiveCalls,
            "enableBursting": True,
            "burstingMaxActiveCalls": self.burstingCount,
            "requireAuthentication": True,
            "sipAuthenticationUserName": trunkName,
            "sipAuthenticationPassword": self.password,
            "trunkGroupIdentity": trunkName+"@"+g.domain,
            "allowUnscreenedCalls": False,
            "accessDevice":{
                "serviceProviderId":g.enterpriseID,
                "groupId":g.groupID,
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
        if self.type == "EVA_ExternalOverflow" or self.type == "EVA_InternalOverflow":
            payload["maxActiveCalls"] = 1
            payload["enableBursting"] = False
            payload["burstingMaxActiveCalls"] = 0
            payload["callForwardingAlwaysAction"] = "Forward"
            payload["callForwardingAlwaysForwardAddress"] = self.CFA

        # API call
        response = requests.post(a.api_host+endpoint,data=json.dumps(payload),headers=headers)
        if str(response) != '<Response [200]>':
            error = response.json()['error']
            fileManager.fm.writeErrors(f'SIPTrunk.buildTunk.POST || {self.type} || {error}')
        return response.json()

    def __repr__(self) -> str:
        return f"Type: {self.type}, Password: {self.password}, Max Active Calls: {self.maxActiveCalls}"