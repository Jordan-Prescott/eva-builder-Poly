#test class
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
    username = input("\nUsername: ") 
    password = getpass.getpass()
    a.getToken()

