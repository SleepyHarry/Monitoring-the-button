import websocket
import os
import threading
import time
import json
import re
import requests

from pprint import pprint

class ButtonMonitor:
    _ws_url_re = re.compile(r"wss://wss.redditmedia.com/thebutton\?h=[0-9a-f]+"
                           r"&e=[0-9]+")
    
    def __init__(self, callback, log_callback=None):
        #callback should be a callable object
        #the idea here is that whatever messages are recieved will be passed
        #to callback

        #for example, if callback==print (as a function), then whenever
        #a message is recieved, it'll be printed (in unformatted JSON)
        
        self.callback = callback

        #log_callback has a similar signature to callback, but it's called
        #when opens, closes and errors occur
        self.log_callback = log_callback or (lambda *a: None)
        
        self.ws = None
        self.old_ws = None
        self.t = None

    @property
    def ws_url(self):
        response = requests.get("http://www.reddit.com/r/thebutton")

        if not response.ok:
            raise requests.exceptions.ConnectionError("Cannot connect to reddit")

        match = self._ws_url_re.search(response.text)

        if match:
            return match.group()

        raise Exception("Cannot find a websocket address")

    def active_ws(self):
        return self.ws is not None

    def new(self):
        def on_message(ws, message):
            message_json = json.loads(message)

            self.callback(message_json)

        def on_error(ws, error):
            self.log_callback(error)

        def on_close(ws):
            self.log_callback("websocket {} closed".format(ws.url))

        def on_open(ws):
            self.log_callback("websocket {} opened".format(ws.url))
        
##        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.ws_url,
                                  on_message = on_message,
                                  on_error = on_error,
                                  on_close = on_close,
                                  on_open = on_open)

        self.t = threading.Thread(target=self.ws.run_forever)
        self.t.setDaemon(True)

    def start(self):
        if self.t is not None:
            self.t.start()
        else:
            raise Exception("No active websocket!")

    def kill(self):
        if self.ws:
            self.ws.close()
            self.old_ws = self.ws
        
        self.ws = None
        self.t = None
