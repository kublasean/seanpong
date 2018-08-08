#!/usr/bin/env python
# sean whalen
# 7 24 18
# define game logic for pong game
# velocity is per frame

import time

class bounds:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class player:
    def __init__(self, width, height, y):
        self.w = width
        self.h = height
        self.y = y
        self.x = 0
        self.vx = 0
        
class ball:
    def __init__(self, radius):
        self.x = 0
        self.y = 0
        self.vx = 0.5
        self.vy = 4
        self.r = radius

class game:
    def __init__(self, bnds, frame_rate, b, p1, p2, center):
        self.bounds = bnds
        self.fr = frame_rate
        self.ball = b
        self.p1 = p1
        self.p2 = p2
        self.center = center
        self.hit = False

# p = a player
#  calcs x vel using previous position
def update_player(p, pos):
    p.vx = p.x - pos
    p.x = pos
    
# b = the ball
# updates b acel, vel, and pos
def update_ball(b):
    b.x += b.vx
    b.y += b.vy

# p = player, b = ball
# has ball been hit by player?
def hit_detect(p, b):
    thresh = 1.0
    dy = abs(p.y - b.y) - p.h - b.r;
    dx = abs(p.x - b.x) - p.w/2.0 - b.r;
    if dx < thresh and dy < thresh:
        b.vy *= -1
        b.vx += p.vx
        return True
    return False

# b = ball
# adjust score / b.vx if out-of-bounds
def bounds_detect(b, bounds, score, center):
    if b.x <= bounds.x[0] or b.x >= bounds.x[1]:
        b.vx *= -1
    if b.y > bounds.y[1]:
        score[1] += 1
        b.x = center[0]
        b.y = center[1]
        b.vy = 4
        b.vx = 0.5
    if b.y < bounds.y[0]:
        score[0] += 1
        b.x = center[0]
        b.y = center[1]
        b.vy = 4
        b.vx = 0.5

# s = state (dict to be sent to clients)
def game_init(s):
    s['score'] = [0,0]
    s['time'] = 0
    b = ball(25)
    p1 = player(100, 10, 400)
    p2 = player(100, 10, 0)
    bnds = bounds((0, 600), (0, 400))
    g = game(bnds, 30, b, p1, p2, (300, 200))
    g.ball.x = g.center[0]
    g.ball.y = g.center[1]
    while True:
        event_loop(s,g)
    return True

# s = state, g = internal game state
def event_loop(s, g):
    print("event loop")
    time.sleep(1.0 / g.fr)
    
    update_player(g.p1, s['pos'][0][0])
    update_player(g.p2, s['pos'][1][0])
    update_ball(g.ball)
    
    bounds_detect(g.ball, g.bounds, s['score'], g.center)
    
    hit_detect(g.p1, g.ball)
    hit_detect(g.p2, g.ball)
   
    s['time'] += 1.0 / g.fr
    s['ball'] = [g.ball.x, g.ball.y]
    return True
    