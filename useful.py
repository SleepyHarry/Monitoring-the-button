#This is just a collection of stuff that I'm fed up rewriting, so, naturally,
#it contains lots of useful classes, hence the name

class Point(tuple):
    #class that's basically just a 2-tuple (a twople, if you will) with
    #magic methods
    def __add__(self, other):
        return Point((self[0] + other[0], self[1] + other[1]))

    def __sub__(self, other):
        return Point((self[0] - other[0], self[1] - other[1]))

    def x(self):
        return self[0]

    def y(self):
        return self[1]

    def __repr__(self):
        return "Point({}, {})".format(*self)

def load_image(name, colorkey=None):
    import pygame as pg
    import os

    if not pg.display.get_init():
        pg.init()
    
    #TODO: make os-independant
    #maybe just check it exists?
    if "C:" in name.upper():    #fucking ew
        fullname = name
##        print "absolute"
    else:
        fullname = os.path.join('resource', name)
##        print "relative"
        
    try:
        image = pg.image.load(fullname)
    except pg.error, message:
##        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image

class colors:
    white = (255, 255, 255)
    black = (0, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    magenta = (255, 0, 255)
    cyan = (0, 255, 255)

    @staticmethod
    def grey(lightness=128):
        return tuple(lightness for _ in range(3))

class Updateable():
    import time
    time_func = time.time
    
    def __init__(self, interval, func, *args, **kwargs):
        self.running = False
        self.last_activated = 0
        
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self.result = None

    def _do(self):
        self.last_activated = self.time_func()
        self.result = self.func(*self.args, **self.kwargs)

##        print self, "updated"

    def start(self):
        self.running = True
        
        self._do()

        return self

    def update(self):
        now = self.time_func()

        if self.running and now - self.last_activated > self.interval:
##            print now - self.last_activated
            self._do()
            return self.result

class RawInputSpoof():
    #mimics functionality of raw_input, without printing prompts

    #usually used as:
    #       raw_input = RawInputSpoof("line 1", "line 2")
    
    def __init__(self, *data):
        self.data = iter(map(str, data))

    def __call__(self, prompt=""):
        try:
            return next(self.data)
        except StopIteration:
            return ''

def repeat_every(interval):
    """ decorator that repeats a function every interval seconds
        calling the wrapped function once starts a new repeating thread
    """
    import threading
    
    def wrap(f):
        def inner(*args, **kwargs):
            result = f(*args, **kwargs)

            t = threading.Timer(interval, inner, args, kwargs)
            t.setDaemon(True)
            t.start()

            return result
            
        return inner
    
    return wrap

def convert(n, base=10):
    ''' Convert a base-10 integer (or string representation thereof)
        into a base-`base` string representation.

        Example:
            convert(27, base=8) -> "33"
            convert(17, base=2) -> "10001"
    '''
    import string

    tokens = string.digits + string.ascii_lowercase
    base_tokens = tokens[:base]

    n = int(n)  #allows the caller to give us a string

    converted = ''
    while n:
        n, r = int.__divmod__(n, base)
        converted += base_tokens[r]

    #we converted in reverse reading order, so reverse the string back
    #if the string is empty, n was 0, so return that
    return converted[::-1] or '0'

def permute_case(s, delimiter=' '):
    ''' Takes a string `s`, and returns a generator containing realistic
        permutations of casing.

        each word (defined by `delimiter`) has three possibilities:
            word
            Word
            WORD

        and every combination thereof is considered.

        Thus, the final generator will have `3**len(s.split(delimiter))`
        elements. Hence the generator.
    '''

    #start with an entirely lowercase string, then split it up
    s = s.lower()
    words = s.split(delimiter)

    #notice that each possible string can be represented uniquely by a trinary
    #number, such that
    #   0 == lowercase, 1 == Title Case, 2 == UPPERCASE
    cases = [str.lower, str.title, str.upper]

    #TODO: prettify f
    #f converts i to a 0-padded trinary string
    f = lambda i: ("{:0"+str(len(words))+"d}").format(int(convert(i, 3)))
    
    perms = map(f, xrange(3**len(words)))

    #sort permutations to favour lowercase and Title Case over UPPERCASE
    perms.sort(key=lambda x: x.count('2'))

    for perm in perms:
        yield delimiter.join(cases[c](words[i]) for i, c in enumerate(map(int, perm)))

