import requests, webbrowser
import threading
import os, sys

#resp= requests.get('http://www.shakthimaan.com', headers= {'If-Modified-Since': 'Sat, 13 Nov 2021 00:15:51 GMT'})
#print(resp)
#print(resp.request.headers)
#print(resp.text)

def get_page(url):
    resp= requests.get(url)
    print('\nGET {} : {} '.format(url, resp.status_code))

def test_cget(url, t):
    resp= requests.get(url, headers= {'If-Modified-Since': t})    
    print('\nTesting If-Modified-Since with GET\nGET {} : {} '.format(url, resp.status_code))
    
def head_page(url):
    resp= requests.head(url)
    print('\nHEAD {} : {} '.format(url, resp.status_code))
    #print(resp.content)

def cookie_test(url):
    resp= requests.get(url)
    disp= '\nCookie test\nFirst request GET : {}'.format(url)
    c= resp.headers['Set-Cookie']
    disp+='\nReceived header Set-Cookie: '+ str(c)
    resp= requests.get(url, headers= {'Cookie': c})
    disp+='\nSecond request'
    if('Set-Cookie' not in resp.headers.keys()):
        disp+='\nStatus code: {}, No set cookie header this time'.format(resp.status_code)
        print(disp)
    else:
        print('something went wrong with cookies')
    
def get_bad(url):
    resp= requests.get(url, data= {'key': 'value'})
    print('\nbad GET {} : {}'.format(url, resp.status_code))
    
def get_notexist(url):
    #url+= '/notexist.html'
    resp= requests.get(url)
    print('\nGET {} : {} Not Found'.format(url, resp.status_code))

    
def test_delete(url):
    disp= '\nTesting unauthorised: \n'
    resp= requests.delete(url)
    disp+= 'DELETE: {} ; Status code: {}'.format(url, resp.status_code) + '\n'
    disp+='Testing authorised delete\n'
    resp= requests.delete(url, auth= ('nushks', 'httpcn'))
    disp+= 'DELETE: {} ; Status code: {}'.format(url, resp.status_code)+ '\n'
    print(disp)

def putFile(url, path, filename, ctype):
    #url+= '/'+ filename
    resp = requests.put(url, data= open(path, 'rb'), headers= {'Content-Type': ctype})
    disp='\nPUT : {} ; Status code: {}'.format(filename, resp.status_code)
    disp+='\nContent-Location: {}'.format(resp.headers['Content-Location'])
    print(disp)

def putobj(url, d):
    resp= requests.put(url, data=d)
    disp='\nPUT : {} ; Status code: {}'.format(url, resp.status_code)
    disp+='\nContent-Location: {}'.format(resp.headers['Content-Location'])
    print(disp)

def post_urlenc(url, form):
    resp= requests.post(url, data= form)
    disp= '\nPOST : {} ; Status code: {}'.format(url, resp.status_code)
    disp+='\nContent-Location: {}'.format(resp.headers['Content-Location'])
    print(disp)

if(len(sys.argv)> 1):
    port= sys.argv[1]
else:
    port= '8000'
    
#head_page('http://www.shakthimaan.com')
baseurl= 'http://127.0.0.1:'+ port

pages= ['/', '/new.html', '/withimage.html', '/audio.html', '/form.html']

#testing get
for i in pages:
    threading.Thread(target= get_page, args=(baseurl+ i, )).start()

#get_bad(baseurl+ '/')

threading.Thread(target= cookie_test, args=(baseurl, )).start()
threading.Thread(target= get_notexist, args= (baseurl+ '/notexist.html', )).start()
threading.Thread(target= test_cget, args=(baseurl+'/new.html', 'Sun, 14 Nov 2021 10:00:51 GMT', )).start()


#testing head
threading.Thread(target= head_page, args=(baseurl, )).start()

#testing put
threading.Thread(target= putFile, args=(baseurl+ '/Dumphere', 'BinFiles/bird.png', 'bird.png', 'image/png' , )).start()
threading.Thread(target= putFile, args=(baseurl+ '/Dumphere/bird.png', 'BinFiles/bird.png', 'bird.png', 'image/png' , )).start()
threading.Thread(target= putFile, args=(baseurl+ '/Dumphere/stats.pdf', 'BinFiles/stats.pdf', 'stats.pdf', 'image/png' , )).start()
threading.Thread(target= putobj, args=(baseurl+ '/Dumphere/demo.txt', {'key': 'value', 'name': 'anushka'}, )).start()

#testing post
#threading.Thread(target= post_urlenc, args=(baseurl+'/form.html', {'anuja': '5009'}, )).start()

#testing delete
threading.Thread(target= test_delete, args= (baseurl+'/deldemo.txt', )).start()
resp= requests.delete(baseurl+'/notfound.html', auth= ('nushks', 'httpcn'))
print('\nDELETE {} ; Status code: {}'.format(resp.request.path_url, resp.status_code))

threading.Thread(target= get_bad, args= (baseurl, )).start()
webbrowser.get().open(baseurl)