import pygame as pg

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
magenta = (255, 0, 255)
cyan = (0, 255, 255)
bgblue = (27, 30, 37)

if pg.font:
    if not pg.font.get_init():
        pg.font.init()
    
    fontL = pg.font.SysFont("arial", 40, bold = True)
    fontM = pg.font.SysFont("arial", 24, bold = True)
    fontS = pg.font.SysFont("arial", 16, bold = True)

def textHollow(font, message, fontcolor):
    notcolor = [c^0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pg.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img

def textOutline(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = pg.Surface(outline.get_size(), 16)
    colorkey = filter(lambda x: x not in [fontcolor, outlinecolor],
                      [magenta, black, white])[0]
    img.fill(colorkey)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(colorkey)
    return img
