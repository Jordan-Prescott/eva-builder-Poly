#fileManager Class
#import

class fm:
    '''fileManager - CRUDs files in this program'''

    def clearErrors():
        file = open(".\lib\errors.txt", "w")
        file.close()

    def writeErrors(e):
        with open(".\lib\errors.txt", "a") as data:
            data.write(e + '\n')



