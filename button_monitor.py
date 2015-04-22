import websocket
import os
import threading
import time
import json
from pprint import pprint

class ButtonMonitor():
    #annoyingly, this is dynamic
    #I don't use this enough to bother getting it dynamically
    #it can be done just by requesting /r/thebutton and searching
    #(using regex) for a wss url

    #TODO: try/except when this happens, so that the user understands
    #      why something went wrong
    ws_url = "wss://wss.redditmedia.com/thebutton?h=\
9b98bf9ebcfb2c56f9128208991995f441371868&e=1429530922"

    def __init__(self, callback, log_callback=None):
        #callback should be a callable object
        #the idea here is that whatever messages are recieved will be passed
        #to callback

        #for example, if callback==print (as a function), then whenever
        #a message is recieved, it'll be printed (in unformatted JSON)

        def black_hole(*args):
            pass
        
        self.callback = callback

        #log_callback has a similar signature to callback, but it's called
        #when opens, closes and errors occur
        self.log_callback = log_callback or black_hole

        self.ws = None
        self.old_ws = None
        self.t = None

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
        self.ws = websocket.WebSocketApp(ButtonMonitor.ws_url,
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
