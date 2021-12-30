import os

'''
VERSION
'''
VERSION= '1.1'

'''
Data size to receive from client
'''
SIZE= 8192

'''
Document root of server
'''
ROOT= os.getcwd()

'''
ico file when browser requests for favicon. 
Displayed in left corner of browser tab
'''
fav= '/images/favicon.ico'
FAVICON= ROOT + fav

'''
Maximum simultaneous connections allowed
'''
MAXREQUEST= 30

'''
Log file to keep log of requests
'''
LOGGING= ROOT + '/logs/access.log'

'''
Log file to keep error records
'''
ERRLOG= ROOT + '/logs/errors.log'

'''
Authorization for delete
'''
USERNAME= 'nushks'
PASSWORD= 'httpcn'

'''
Cookie settings: header basic and max age(in seconds)
'''
COOKIE= 'Set-Cookie: cookid='
MAXAGE= '; Max-Age= 3600'