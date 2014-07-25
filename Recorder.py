#!/usr/bin/env python

from libmproxy import controller, proxy
import os,re
import zlib
noresult = "(\.jpg|\.gif|\.png|\.css|\.js|\.ico)"

filter = re.compile(noresult,re.IGNORECASE)

class StickyMaster(controller.Master):
#file name 
    nametail = 0
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        #hid = (msg.host, msg.port)
        #print msg.host
        if msg.headers["Content-Encoding"] == ['gzip']:
            #print msg.headers["Content-Encoding"]
            postdata = self.Decode_Request_Body(msg.content)
        else:
            postdata = str(msg.content)

        body = str(msg.method) + " "+ str(msg.path) + " HTTP/1.1\r\n" + str(msg.headers) + "\r\n" + postdata + "\r\n"

        if( self.Noporxy_request(msg.path) ):
            pass
        else:
            self.Record_request(body,self.nametail,msg.host)
        

        msg.reply()

    def Record_request(self,content,nametail,hostname):
        filename = "/tmp/request."+hostname+'.'+str(StickyMaster.nametail)
        StickyMaster.nametail = StickyMaster.nametail + 1
        try:
            file = open(filename,"a")
            file.write(content)
            file.flush()
            
        except IOError,args:
            pass
        file.close()
    

    def Noporxy_request(self,url):
        oururl = str(url)
        result = filter.search(url)
        return result

    def Decode_Request_Body(self,data):
        if(not data):
            return ""
        result = zlib.decompress(data,16+zlib.MAX_WBITS)
        return result

config = proxy.ProxyConfig(cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"))


server = proxy.ProxyServer(config, 8089)
m = StickyMaster(server)
m.run()
