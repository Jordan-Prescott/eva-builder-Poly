#fileManager Class
class fm:
    '''fileManager - CRUDs files in this program'''

    def clearErrors():
        '''
        wipes the document of any errors 
        '''
        file = open(".\lib\errors.txt", "w")
        file.close()

    def writeErrors(e):
        '''
        writes error log to ./lib/errors.txt

        :param e: error log
        '''
        with open(".\lib\errors.txt", "a") as data:
            data.write(e + '\n')



