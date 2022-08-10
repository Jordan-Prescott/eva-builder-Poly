#test class

class Api:
    def __init__(self, username, password, baseURL):
        super().__init__()
        self.username = username
        self.password = password
        self.baseURL = baseURL

    def apiHW(self):
        print(f'Hello world from {self.baseURL}, {self.username}, {self.password}')
class Ent(Api):
    def __init__(self, entID):
        super().__init__()
        self.entID = entID
    
    def entHW(self):
        print(f"Hello world from {self.entID}")
class Grp(Ent):
    def __init__(self, grpID, entID):
        super().__init__(entID)
        self.grpID = grpID

    def grpHW(self):
        print(f"Hello world from {self.grpID}")  
class Usr(Grp):
    def __init__(self, usrID, grpID, entID):
        super().__init__(grpID, entID)
        self.usrID = usrID

    def usrHW(self):
        print(f"Hello world from {self.usrID}")

def main():

    a = Api('Jordan.Prescott', 'blahBlahBlah', 'https://url.com/api/v1/')
    u = Usr("6001MANAP@manap.ev.com", "MANAP", "Marriott UK")

    print(u.entID)
    print(u.grpID)
    print(u.usrID)
    u.entHW()
    u.grpHW()
    u.usrHW()
    u.apiHW()
    
if __name__ == "__main__":
    main()