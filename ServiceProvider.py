#ServiceProvider Class

class sPrv: #ServiceProvider Object
    '''serviveProvider class - saves type but API calls are used in Enterprise'''
    def __init__(self, ID, type):
        '''SP is the brand or chain like Marriott with groups (individual hotels) and users (Staff/ Guests in the hotel).
        
        Hierachy: Ent/SP > Group > User 
        
        variables:
        ID(SP ID), type(Ent or SP Type)
        '''
        super().__init__()

        self.ID = ID
        self.type = type

    def __repr__(self) -> str:
        return f"ID: {self.ID}, Type: {self.type}"

