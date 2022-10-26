import Magic.API as API
import Magic.ServiceProvider as ServiceProvider
import Magic.Enterprise as Enterprise
import Magic.Group as Group
import Magic.SIPTrunk as SIPTrunk
import Magic.TrunkUser as TrunkUser
import Magic.HuntGroup as HuntGroup

a = API.api("Jordan.Prescott", "pwh7twx@FVY0dcv0tan")
a.setAPIHost("US")
a.getToken()

g = Group.grp("TestLab","EVA_TEST")
tu = TrunkUser.trunkUser("EVA_TEST141401_EVA_EL", 2015, "SIP-DID", True, "EVA_TEST141401_EVA_EL@testlab.ev.com", "EVA_Poly", "Blah123456!")

tu.assigntoTrunk(a,g)