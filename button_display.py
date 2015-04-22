from __future__ import print_function
import pygame as pg
import sys, time, random, math, json, threading
from pprint import pprint
from collections import defaultdict
from useful import load_image, colors, repeat_every
from textFuncs import *
from button_monitor import ButtonMonitor

size = width, height = 640, 480
fps_tgt = 30

save_path = "resource/{}"
log_path = save_path.format("log.json")
log_t_path = save_path.format("logt.txt")    #order-preserving

class Bar():
    flair_colors = map(pg.color.Color,
                       (
                           0x888888ff,      #non-presser
                           0xe50000ff,      #10s
                           0xe59500ff,      #20s
                           0xe5d900ff,      #30s
                           0x02be01ff,      #40s
                           0x0083c7ff,      #50s
                           0x820080ff       #60s
                        )
                       )
    
    def __init__(self, w, h):
        self.w, self.h = w, h

        self.rect = (0, h/2-50, w, 100)

        self.info = None

        self.last_update = time.clock()

        self.last_sec = 60
        self.press_log = defaultdict(int)
        self.presses_raw = ""
        self.all_presses = defaultdict(int)

    def update(self, msg_json):
        self.info = msg_json["payload"]

        secs_left = int(self.info["seconds_left"])
        if secs_left > self.last_sec or secs_left == 60:
            #a press has occurred
            self.press_log[self.last_sec] += 1

        self.presses_raw += "{:02d}".format(secs_left)

        self.last_sec = secs_left

        self.last_update = time.clock()

    def save(self, log_path, log_t_path):
        try:
            with open(log_path) as f:
                press_log = defaultdict(int, json.load(f))
        except IOError:
            #file doesn't exist
            press_log = defaultdict(int)
        
        out_log = {}
        for k in press_log.keys() + self.press_log.keys():
            out_log[int(k)] = press_log[unicode(k)] + self.press_log[int(k)]
        
        json.dump(out_log, open(log_path, 'w'))

        self.press_log = defaultdict(int)
        self.all_presses = out_log

        with open(log_t_path, 'a') as f:
            f.write(self.presses_raw)

        self.presses_raw = ""
        
    def draw(self, surface):
        if self.info is None:
            #we haven't had our first update yet, so let's not draw anything

            #except a loading notification
            text = textOutline(fontL, "Loading The Button",
                               colors.white, colors.black)
            screen.blit(text, text.get_rect(center=(self.w/2, self.h/2)))
            return

        ##update bar itself
        secs_left = int(self.info["seconds_left"])

        #more precise seconds counter
        f_secs_left = secs_left - (time.clock() - self.last_update)

        flair_color = Bar.flair_colors[max(0, (int(f_secs_left)-1)/10 + 1)]

        left, top, w, h = self.rect
        w =max(0, int(f_secs_left*self.w/60.))
        self.rect = (left, top, w, h)
        
        pg.draw.rect(surface, flair_color, self.rect)

        s = "{:.2f}s remaining"
        text = textOutline(fontL,
                           s.format(f_secs_left),
                           colors.white, colors.black)
        surface.blit(text, text.get_rect(bottom=self.rect[1],
                                         centerx=self.w/2))

bar = Bar(width, height)

btn = ButtonMonitor(bar.update, print)
btn.new()
btn.start()

#set up auto-saving every five minutes
@repeat_every(300)
def save_log(log_path, log_t_path):
    print("saving to", log_path, "and", log_t_path)
    bar.save(log_path, log_t_path)

#saves and starts the autosaving timer
save_log(log_path, log_t_path)

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(size)

##btn.start()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            btn.kill()

            save_log(log_path, log_t_path)
            
            pg.quit()
            sys.exit()

        if event.type == pg.MOUSEBUTTONDOWN:
            m1, m3, m2 = pg.mouse.get_pressed()
            mX, mY = pg.mouse.get_pos()

            if m2:
                print('-'*80)
                print('\n'.join("{}: {}".format(k, v) \
                                for k, v in sorted(bar.press_log.items())))

        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()

    screen.fill((234, 234, 234))

    bar.draw(screen)
    
    pg.display.flip()

    clock.tick(fps_tgt)
