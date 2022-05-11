#ServiceProvider Class

class sPrv: #ServiceProvider Object
    '''serviceProvider class'''
    def __init__(self, ID, type):
        '''init variables'''
        super().__init__()

        self.ID = ID
        self.type = type

    def __repr__(self) -> str:
        return f"ID: {self.ID}, Type: {self.type}"

