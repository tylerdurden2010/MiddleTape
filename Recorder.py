#!/usr/bin/env python

from libmproxy import controller, proxy
import os,re
noresult = "(\.jpg|\.gif|\.png|\.css|\.js)"

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
        #print msg.method + " " +msg.path
        #print msg.get_url()
        #print msg.headers
        #print msg.content
        body = str(msg.method) + " "+ str(msg.path) + " HTTP/1.1\r\n" + str(msg.headers) + "\r\n" + str(msg.content) + "\r\n"
       
        #print self.Noporxy_request(msg.path)

        if( self.Noporxy_request(msg.path) ):
            pass
        else:
            self.Record_request(body,self.nametail)
        

        msg.reply()

    def Record_request(self,content,nametail):
        filename = "/tmp/request"+str(StickyMaster.nametail)
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

config = proxy.ProxyConfig(cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"))


server = proxy.ProxyServer(config, 8089)
m = StickyMaster(server)
m.run()
