#!/usr/bin/env python3
from socket import *   #sockets-> the core requirement
import os              #to handle different paths, permissions
import sys 
import threading 
from _thread import *  #lightweight to implement multithreading
from config import *   #config file of serve
import datetime        #to format date header
import uuid            #to generate random unique ids for new files
import logging         #to implement access and error logs
import base64          #for authorization in DELETE method
import time
import random          #for generating random numbers for cookie name
import json

logging.basicConfig(filename= LOGGING, level= logging.INFO, format= '%(asctime)s : %(levelname)s : %(message)s')
#erformat= '%(asctime)s : %(levelname)s : %(message)s'
erlog= open(ERRLOG, 'a')

#File extensions and content type interconversion
#when type not mentioned default is text/plain
ext_t = {'.html':'text/html', '.txt':'text/plain', '': 'text/plain', '.css': 'text/css', '.jpg':'image/jpg', '.gif': 'image/gif', '.png':'image/png', '.jpeg':'image/webp', '.ico': 'image/vnd.microsoft.icon', '.json':'application/x-www-form-urlencoded', '.pdf': 'application/pdf', '.js': 'application/javascript', '.mp3' : 'audio/mpeg'}
#mirror of above dictionary
t_ext = {'text/html': '.html','text/plain': '.txt', 'image/png': '.png', 'image/gif': '.gif', 'image/jpg': '.jpg','image/vnd.microsoft.icon': '.ico', 'image/webp': '.jpeg', 'application/x-www-form-urlencoded':'.json', 'image/jpeg': '.jpeg', 'application/pdf': '.pdf', 'audio/mpeg': '.mp3', 'video/mp4': '.mp4'}
bintype= ['image/png', 'image/gif', 'image/jpg','image/vnd.microsoft.icon', 'image/webp', 'image/jpeg', 'application/pdf', 'audio/mpeg', 'video/mp4']

#months directory gives corresponding number of month. Used in converting http date to usable form
months = { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }

#status codes and their phrase
status_codes= {100: 'Continue', 101: 'Switching Protocols',
        200: 'OK', 201: 'Created', 202: 'Accepted', 203: 'Non-Authoritative Information', 
        204: 'No Content', 205: 'Reset Content', 206: 'Partial Content',
        300: 'Multiple Choices', 301: 'Moved Permanently', 302: 'Found', 303: 'See other', 304: 'Not Modified', 307: 'Temporary Redirect', 
        400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden' , 404: 'Not found', 405: 'Method not allowed', 
        406: 'Not Acceptable', 408: 'Request Timeout', 409: 'Conflict', 411: 'Length required', 414: 'Request-URI Too Long',
        415: 'Unsupported Media Type', 416: 'Requested Range Not Satisfiable',
        500: 'Internal Server Error', 501: 'Not Implemented', 502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Timeout', 
        505: 'HTTP Version Not Supported'}

#server class: sockets and threading
class Server:
    def __init__(self, port):
        self.ip= '127.0.0.1'
        self.port= port
        print("Server listening: http://"+ self.ip + ":" + str(self.port))
        
    
    def start_server(self):
        #create TCP socket
        server_sock= socket(AF_INET, SOCK_STREAM)
        threads= []
        try:
            server_sock.bind((self.ip, self.port))
            server_sock.listen(5)
            while(True):
                try:
                    client, addr= server_sock.accept()
                    if(len(threads)> MAXREQUEST):
                        resp= status(500)
                        client.send(resp.encode())
                    t= start_new_thread(welcomeClient, (client, addr,))
                    threads.append(t)
                except KeyboardInterrupt:
                    server_sock.close()
                    sys.exit()
        except KeyboardInterrupt:
            server_sock.close()
            sys.exit()
        
        except Exception as e:
            print("ERROR message: ", e)
        server_sock.close()
            
            
    def request(self, data):
        return data

#split the http message into headers and body. Header lines split into a list
def parse(message):
    #http headers and body(if exists) are separated by \r\n\r\n
    headers, body= message.split('\r\n\r\n')
    lines= headers.split('\r\n')
    return lines, body

#returns the status line in http response corr to given status code
def status(scode):
    resp= 'HTTP/1.1 '
    resp+= str(scode)+ ' '+ status_codes[scode]
    resp+= '\r\n'
    return resp

#returns an html page for error status codes, like 404, 401, 403, etc
def errpages(scode):
    #sline= 'HTTP/1.1 ' + str(scode)+ ' '+ status_codes[scode]
    sline= status(scode)
    html= "<html><head><body><h1> " + sline+ " </h1></body></html>"
    return html

#gives date in http format. if no arg passed-> now.
def get_date(t= 0):
    t= datetime.datetime.now() + datetime.timedelta(seconds= t)
    date= t.strftime('%a')+ ', '+ t.strftime('%d')+ ' '+ t.strftime('%b')+ ' '+ t.strftime('%Y')
    date+= ' '+ t.strftime('%X')+ ' GMT\r\n'
    return date

#returns common headers
def response_default(content_type, size, rheaders, loc= ''):
    if(content_type== None):
        content_type= 'text/html'
    resp= ''
    if('Connection' in rheaders.keys()):
        conline= 'Connection: ' + rheaders['Connection']+ '\r\n'
    else:
        #by default non-persistant
        conline= 'Connection: close\r\n'
    resp+= 'Server: ' + 'AnushkaT HTTP\r\n'
    date= get_date()
    resp+= 'Date: ' +  date
    resp+= 'Accept-Ranges: bytes\r\n'
    if('Cookie' not in rheaders.keys()):
        cookieheader= set_cookie()
        resp+= cookieheader
    resp+= conline
    for h in rheaders:
        if(h== 'Accept'):
            resp+= 'Content-Type: '+ content_type + '\r\n'
        elif(h== 'Accept-Language'):
            resp+= ('Content-Language: ' + rheaders[h] + '\r\n')
        elif(h== 'Accept-Encoding' and size!= None):
            resp+= ('Content-Length: ' + str(size) + '\r\n')
        #handle date and if-modified header
        else:
            continue
    if(loc != ''):
        resp+= 'Content-Location: '+ loc+ '\r\n'
    #resp+= conline
    resp+= '\r\n'
    return resp

#logs into error.log file
def log_error(rline, scode):
    erlog= open(ERRLOG, 'a')
    err= str(time.asctime()) + ' : ' + 'INFO : '
    err+= rline
    err+= status(scode)+ '\n'
    erlog.write(err)

#sets set-cookie header with cookid and maxage    
def set_cookie():
    ''' Set-Cookie is response header sent if Cookie header absent in request
    cookie name and max age defined in config file'''
    c= COOKIE + str(random.randint(10000, 40000))+ MAXAGE + ' \r\n'
    return c

def mod_time(reqpath):
    t= time.ctime(os.path.getmtime(reqpath))
    t= t.split(' ')
    t[0]= t[0]+ ', '
    mtime= t[0]+ t[2]+ ' '+ t[1]+ ' '+ t[4] + ' ' + t[3] + ' GMT'
    return mtime

#handles conditional get-> If modified since header(value in imsh)
def if_modified(reqpath, imsh):
    cget= False
    imsh= imsh.split(' ')
    d= int(imsh[1]) #date
    m= months[imsh[2]] #month
    y= int(imsh[3]) #year
    t= imsh[4].split(':')
    h, mi, s= int(t[0]), int(t[1]), int(t[2]) #hour, min, sec
    htime= datetime.datetime(y, m, d, h, mi, s)
    htime= int(time.mktime(htime.timetuple()))
    mtime= int(os.path.getmtime(reqpath))
    if(mtime>= htime):
        cget= True #modified since header date. So send
    else:
        cget= False #not modified. so dont send file data
    return cget

#parses application/x-www-form-urlencoded type body in post
def urlencoded_parse(body):
    form_data= {}
    #in application/x-www-form-urlencoded name value pairs separated by &
    body= body.split('&')
    for pair in body:
        #split the name value pair
        pair= pair.split('=')
        form_data[pair[0]]= pair[1]
    return form_data

#parse multipart type body in post
def multipart_parse(ctype, body):
    boundary= ctype.split('=')
    boundary= boundary[1][1: -1]
    boundary= '--'+ boundary
    form_data= {}
    fileex=0
    for i in body:
        if(boundary in i ):
            pass
        elif('Content-Disposition' in i):
            if('filename' in i):
                fileex=1
                filename= i[i.index('filename')+ 10 : -1]
                fileindex= body.index(i)
                if(filename!= ''):
                    form_data['filename']= filename
        if('Content-Type' in i or filename!= ''):
            try:
                _, ext= os.path.splitext(filename)
                ftype= ext_t[ext]
            except:
                    #pass
                ftype= i[i.index(':')+ 1: ]
            form_data['file-type']= ftype
    if(fileex==1):
        if(ftype in bintype):
            fdata= body[fileindex: ]
    
    return form_data, fdata

#bridge function-> target of threading. Calls appropriate method 
bindata=0
def welcomeClient(clientsock, clientaddr):
    bindata=0
    message= clientsock.recv(SIZE)
    try:
        request= message.decode('utf-8')
        headerlines, body = parse(request)
    except UnicodeDecodeError:
        headerlines, body= message.split(b'\r\n\r\n')
        headerlines= headerlines.decode(errors= 'ignore')
        headerlines= headerlines.split('\r\n')
        bindata= 1
    
    reqline= headerlines[0]
    line0= reqline.split(' ')
    method= line0[0]
    uri= line0[1]
    ver= line0[2]
    
    #check version
    if(ver== 'HTTP/1.1'):
        #list out header fields and their values into a dictionary
        rheaders= {}
        for i in range(1, len(headerlines)):
            line= headerlines[i].split(': ')
            rheaders[line[0]]= line[1]
            
        m= HTTP()
        if(method=='GET' or method== 'HEAD'):
            if(body != ''):
                resp= status(400)
                dat= errpages(400)
                s= len(dat.encode())
                resp+= response_default('text/html', s, rheaders)
                resp+= dat
                resp= resp.encode()
                clientsock.send(resp)
                return
            m.get_head_method(clientsock, uri, rheaders, method)
        elif(method== 'PUT'):
            m.put_method(clientsock, uri, rheaders, body, bindata)
        elif(method== 'POST'):
            m.post_method(clientsock, uri, rheaders, body, message)
        elif(method== 'DELETE'):
            if(body != ''):
                #if body present then bad request
                resp= status(400)
                dat= errpages(400)
                s= len(dat.encode())
                resp+= response_default('text/html', s, rheaders)
                resp+= dat
                resp= resp.encode()
                clientsock.send(resp)
                return
            m.delete_method(clientsock, uri, rheaders)
        else:
            resp= status(501)
            dat= errpages(501)
            s= len(dat.encode())
            resp+= response_default('text/html', s, rheaders)
            resp+= dat
            resp= resp.encode()
            clientsock.send(resp)
    else:
        #version not supported
        resp= status(505)
        dat= errpages(505)
        s= len(dat.encode())
        resp+= response_default('text/html', s, rheaders)
        resp+= dat
        resp= resp.encode()
        clientsock.send(resp)
    
    
#headers= {'Server': 'My http', 'Content- Type': 'text/html'}

#http class manages all request methods
class HTTP:
    def get_head_method(self, clientsock, uri, rheaders, method):
        ''' Check if uri is file existing
        if it is / then send default root page content
        check permissions for file write+read
        for files-> set content type acc to file extenion
        '''
        rline= method+ ' ' + uri + '\n'
        persistent=0
        html= None
        if(uri== '/'):
            reqpath= ROOT + '/index.html'
            content_type= 'text/html'
        elif(uri== '/favicon.ico'):
            reqpath= FAVICON
            content_type= 'image/vnd.microsoft.icon'
        else:
            reqpath= ROOT+ uri
        #add cookie functionality
        #check if file exists
        
        print('Request for: ', reqpath)
        print(method)
        isF= os.path.isfile(reqpath)
        if(not isF):
            reqpath= reqpath.rstrip('/')
            isF= os.path.isfile(reqpath)
        #isD= os.path.isdir(reqpath)
        resp= ''
        #respheaders={}
        if(isF):
            #requested content exists and is a file
            #ext= '.'+ reqpath.split('.')[1]
            _ , ext= os.path.splitext(reqpath)
            content_type= ext_t[ext]
            #check permissions
            if(os.access(reqpath, os.R_OK) and os.access(reqpath, os.W_OK)):
                #respheaders[]= content_type
                try:
                    f= open(reqpath, 'rb')
                    size= os.path.getsize(reqpath)
                    data= f.read(size)
                    scode= 200
                    resp+= status(200)
                except:
                    scode= 500
                    resp+= status(500)
                    html= errpages(scode)
                
                if('Connection' in rheaders.keys()):
                    conline= 'Connection: ' + rheaders['Connection']+ '\r\n'
                    if(rheaders['Connection']== 'keep alive'):
                        persistent=1
                else:
                    #by default non-persistant
                    conline= 'Connection: close\r\n'
                cget= True
                if('If-Modified-Since' in rheaders.keys()):
                    cget= if_modified(reqpath, rheaders['If-Modified-Since'])
                    if(cget== False):
                        scode= 304
                        resp= status(scode)
                        
                for h in rheaders:
                    if(h== 'User-Agent'):
                        resp+= 'Server: AnushkaT \r\n'
                        resp+= 'Date: '+ get_date()
                    elif(h== 'Accept'):
                        resp+= 'Content-Type: '+ content_type + '\r\n'
                    elif(h== 'Accept-Language'):
                        resp+= ('Content-Language: ' + rheaders[h] + '\r\n')
                    elif(h== 'Accept-Encoding'):
                        resp+= ('Content-Length: ' + str(size) + '\r\n')
                    
                    #handle date and if-modified header
                    #handle etag header-> if etag header value matches then send, otherwise not
                    else:
                        continue
                 
                resp+= conline
                
                if('Cookie' in  rheaders.keys()):
                    #print('Cookie already there')
                    pass
                else:
                    c=set_cookie()
                    #print(c)
                    resp+= c
                    
                resp+= 'Last-Modified: '+ mod_time(reqpath) + '\r\n'
                resp+= '\r\n'
                sent= clientsock.send(resp.encode())
                #print(sent)
                
                if(method== 'GET' and cget== True):
                    sent= clientsock.send(data)
                    #print(sent)
                logging.info(' {} {} \n'.format(rline, resp))
                
            else:
                scode= 403
                resp= status(403)
                html= errpages(scode)
                s= len(html.encode())
                resp+= response_default('text/html', s, rheaders)
                log_error(rline, scode)
                if(method== 'GET'):
                    resp+= html
                resp= resp.encode()
                clientsock.send(resp)
        else:
            scode= 404
            resp= status(404)
            html= errpages(scode)
            s= len(html.encode())
            resp+= response_default('text/html', s, rheaders)
            log_error(rline, scode)
            if(method== 'GET'):
                resp+= html
            resp= resp.encode()
            clientsock.send(resp)
            clientsock.close()
        
                
        '''if(isD):
            #request for directory listing
            dirs= os.listdir(reqpath)
            if(os.access(reqpath, os.R_OK) and os.access(reqpath, os.W_OK)):
                resp= status(200)
                
            else:
                resp= status(403)'''
                    
                
    ''' content types-> application/x-www-form-urlencoded, multipart/form-data, text/plain'''
    def post_method(self, clientsock, uri, rheaders, body, message):
        reqpath= ROOT+ uri
        rline= 'POST ' + uri + '\n'
        ctype= rheaders['Content-Type']
        resp=''
        if('application/x-www-form-urlencoded' in ctype):
            resp= status(201)
            form_data= urlencoded_parse(body)
            js= json.dumps(form_data)
            file= 'DumpHere/'+ str(uuid.uuid4()) + '.json'
            f= open(file, 'w')
            f.write(js)
            resp+= response_default('',0, rheaders, ROOT+ file)
            logging.info(' {} {} \n'.format(rline, resp))
            clientsock.send(resp.encode())
            return
        elif('multipart/form-data' in ctype):
            body= body.split('\n')
            form_data, fdata= multipart_parse(ctype, body)
            filename= form_data['filename']
            reqpath= ROOT+ filename
        elif('text/plain' in ctype):
            fdata= parse_qs(body)
            
        isF= os.path.isfile(reqpath)
        isD= os.path.isdir(reqpath)
        if(isF):
            scode= 200
            resp= status(scode)
            f= open(reqpath, 'a')
            f.write(fdata)
        elif(isD):
            scode= 201 #created
            resp= status(scode)
            reqpath+= str(uuid)+ '.json'
            f= open(reqpath, 'w')
            f.write(fdata)
        else:
            scode= 404
            resp= status(scode)
            clientsock.send(resp.encode())
            return
        resp+= response_default(content_type, 0, rheaders, reqpath)
        logging.info(' {} {} \n'.format(rline, resp))
        clientsock.send(resp.encode())
        
            
    
    ''' PUT method: resource can be created/modified
    created-> 201, modified-> 200 or 204
    if uri is dir-> create new file with random name (specify in content location header)
    if uri is existing file-> modify/update it. If doesnot exist-> create'''
    def put_method(self, clientsock, uri, rheaders, body, bindata):
        rline= 'PUT ' + uri + '\n'
        reqpath= ROOT+ uri
        isF= os.path.isfile(reqpath)
        isD= os.path.isdir(reqpath)
        isexist= os.path.exists(reqpath)
        resp=''
        fdata= b''
        
        ctype= rheaders['Content-Type'].split(';')
        content_type= ctype[0]
        try:
            ext= t_ext[content_type]
        except:
            #media type not handled
            scode= 415
            resp= status(415)
            html= errpages(415)
            log_error(rline, scode)
        
        try:
            #fsize denotes the actual size of data to be written
            fsize= int(rheaders['Content-Length'])
        except:
            scode= 411
            resp= status(scode)
            s= len(html.encode())
            resp+= response_default('text/html', s, rheaders)
            log_error(rline, scode)
            resp+= html
            resp= resp.encode()
            clientsock.send(resp)
        try:
            fdata+= body
        except TypeError:
            fdata+= body.encode()
        #Some part of data received as payload, keep receiving until we have complete data
        diff= fsize - len(fdata) #i.e keep receiving from client untill this difference becomes 0
        while(diff>0):
            body= clientsock.recv(SIZE)
            try:
                fdata+= body
            except TypeError:
                fdata+= body.encode()
            diff-= len(body)
        
        if(content_type== 'application/x-www-form-urlencoded'):
            resp= status(201)
            form= urlencoded_parse(fdata.decode())
            js= json.dumps(form)
            f= open(reqpath, 'w')
            f.write(js)
            resp+= response_default('',0, rheaders, reqpath)
            logging.info(' {} {} \n'.format(rline, resp))
            clientsock.send(resp.encode())
            return
            
        #uri corr to an existing file
        if(isF and isexist):
            if(os.access(reqpath, os.W_OK)):
                scode= 204
                f= open(reqpath, 'wb') #wb because overwrite existing resource in put
                resp= status(scode)
            else:
                scode= 403
                resp= status(scode)
                html= errpages(scode)
                s= len(html.encode())
                resp+= response_default('text/html', s, rheaders)
                log_error(rline, scode)
                resp+= html
                resp= resp.encode()
                clientsock.send(resp)
                return
        elif(isD):
            uid= str(uuid.uuid4())
            reqpath+= '/' + uid + ext
            f= open(reqpath, 'wb')
            scode= 201 #created
            resp= status(201)
        else:
            f= open(reqpath, 'wb')
            scode= 201 #created
            resp= status(scode)
        
        #handle put response headers
        resp+= response_default(content_type, 0, rheaders, loc= reqpath)
        logging.info(' {} {} \n'.format(rline, resp))
        f.write(fdata)
        clientsock.send(resp.encode())
        
    
    ''' DELETE method: requests for a resource to be removed.
    Check for authorization(else 401), resource exists(else 404),
    file permissions(else 403). If all good-> remove resource and send 204'''
    def delete_method(self, clientsock, uri, rheaders):
        rline= 'DELETE ' + uri + '\n'
        reqpath= ROOT + uri
        isF= os.path.isfile(reqpath)
        resp= ''
        #for delete operation authentication required
        #Basic authentication: username:password and encoded base64
        if('Authorization' in rheaders.keys()):
            a= rheaders['Authorization']
            a= a.split(' ') #consider a[0]= Basic
            a= base64.decodebytes(a[1].encode()).decode() #decode from 
            u, p= a.split(':')
            if(u== USERNAME and p== PASSWORD):
                if(isF):
                    if(os.access(reqpath, os.W_OK)):
                        os.remove(reqpath)
                        scode= 200
                        resp= status(scode)
                        resp+= response_default('text/html', 0, rheaders)
                        logging.info(' {} {} \n'.format(rline, resp))
                        #add www-authenticate header
                        clientsock.send(resp.encode())
                        clientsock.close()
                        return
                    else:
                        scode= 403 #forbidden-> no permission
                        resp= status(scode)
                        
                else:
                    scode= 404 #resource not found
                    resp= status(scode)
                    
            else:
                scode= 401 #unauthorised ->credentials dont match
                resp= status(scode)
        else:
            scode= 401 #unauthorised-> no authorization info
            resp= status(scode)
            
        resp+= response_default('text/html', 0, rheaders)
        log_error(rline, scode)
        resp+= errpages(scode)
        clientsock.send(resp.encode())
        clientsock.close()
    

if __name__== "__main__":
    #accept port number as commandline arguement
    if(len(sys.argv) >1):
        port= int(sys.argv[1])
    else:
        port= 8000
        
    s= Server(port)
    s.start_server()