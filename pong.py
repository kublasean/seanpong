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
    def __init__(self, radius, center):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 4
        self.r = radius
        self.center = center
    def reset(self):
        self.x = self.center[0]
        self.y = self.center[1]
        self.vx = 0
        self.vy = 4

class game:
    def __init__(self, bnds, frame_rate, b, p1, p2):
        self.bounds = bnds
        self.fr = frame_rate
        self.ball = b
        self.p1 = p1
        self.p2 = p2
        self.hit = 1

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
        b.vx += -.1*p.vx
        return True
    return False

# b = ball
# adjust score / b.vx if out-of-bounds
def bounds_detect(b, bounds, score):
    if b.x-b.r <= bounds.x[0] or b.x+b.r >= bounds.x[1]:
        b.vx *= -1
    if b.y > bounds.y[1]:
        score[1] += 1
        return True
    if b.y < bounds.y[0]:
        score[0] += 1
        return True
    return False

# g = game state
# reset stuff for next round (called when p scores)
def next_round(g):
    g.ball.reset()
    g.hit = 1

# s = state
def game_init(s):
    s['score'] = [0,0]
    s['time'] = 0
    s['continue'] = True
    b = ball(25, (300, 200))
    p1 = player(100, 10, 400)
    p2 = player(100, 10, 0)
    bnds = bounds((0, 600), (0, 400))
    g = game(bnds, 40, b, p1, p2)
    g.ball.reset()
    while s['continue']:
        event_loop(s,g)
    print("thread graceful death")
    return True

# s = state, g = internal game state
def event_loop(s, g):
    time.sleep(1.0 / g.fr)
    
    update_player(g.p1, s['pos'][0][0])
    update_player(g.p2, s['pos'][1][0])
    update_ball(g.ball)
    
    
    if bounds_detect(g.ball, g.bounds, s['score']):
        next_round(g)
        return True
    
    if g.hit == 1:
        if hit_detect(g.p1, g.ball):
            g.hit = 0
    else:
        if hit_detect(g.p2, g.ball):
            g.hit = 1
   
    s['time'] += 1.0 / g.fr
    s['ball'] = [g.ball.x, g.ball.y]
    return True
   
#s = {'pos': [[0,0],[0,0]]}
#game_init(s)
