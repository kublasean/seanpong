#!/usr/bin/env python

import asyncio
import json
import websockets
import concurrent.futures
import time
import pong
import queue

USERS = {}
FUTURES = {}
MAX_GAMES = 20
SESSIONS = queue.Queue()
ACTIVE_GAMES = 0
GAME_ID = 0
FRAMERATE = 40

class session:
    def __init__(self):
        self.STATE = {'time': 0, 'pos': [[0,0],[0,0]], 'score': [0,0], 'ball': [300, 200], 'continue': True}
        self.players = {}

async def register(user):
    global ACTIVE_GAMES
    global MAX_GAMES
    global GAME_ID
    
    if ACTIVE_GAMES >= MAX_GAMES:
        return False
    
    if SESSIONS.empty():
        s = session()
    else:
        s = SESSIONS.get()
    
    numplayers = len(s.players)
    s.players[user] = numplayers
    USERS[user] = s

    if len(s.players) == 2:
        ACTIVE_GAMES += 1
        FUTURES[s] = ( EXECUTOR.submit(pong.game_init, s.STATE) )
    else:
        SESSIONS.put(s)
    output = " numplayers: " + repr(len(s.players)) + "\n"
    output += "active games: " + repr(ACTIVE_GAMES)
    print(output)
    return True

def consume(user, message):
    data = json.loads(message)
    s = USERS[user]
    index = s.players[user]
    s.STATE['pos'][index] = data['pos']

async def consumer_handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed as e:
            break
        consume(websocket, message)

async def produce(user):
    await asyncio.sleep(1.0/FRAMERATE)
    return json.dumps(USERS[user].STATE)

async def producer_handler(websocket):
    while True:
        message = await produce(websocket)
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed as e:
            break

async def main(websocket, path):
    global ACTIVE_GAMES
    global GAME_ID
    if await register(websocket):
        consumer_task = asyncio.ensure_future(consumer_handler(websocket))
        producer_task = asyncio.ensure_future(producer_handler(websocket))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
        #disconnect logic
        s = USERS[websocket]                 # = session for this user
        output = "disconnect: " + repr(websocket) + " " 
        for task in pending:
            task.cancel()
        
        USERS.pop(websocket)                #remove this client from users dict
        s.players.pop(websocket)             #remove this client from session.players dict
        other_players = list(s.players.keys());
        s.STATE['continue'] = False

        if s in FUTURES:
            output += repr(FUTURES[s].result())
            FUTURES.pop(s)
            ACTIVE_GAMES -= 1
            output += " thread result " 
                
        if other_players:
            p = other_players[0]
            if not SESSIONS.empty():        #connect other player to next waiting player
                snext = SESSIONS.get()
                snext.players[p] = 1
                USERS[p] = snext
                FUTURES[snext] = ( EXECUTOR.submit(pong.game_init, snext.STATE) ) #start new game
                ACTIVE_GAMES += 1
                output += "added other player to " + repr(snext) + " "
            else:
                s.players[p] = 0                   #set the player number of other player to one if present
                SESSIONS.put(s)                  #put the old session with other player on waiting queue
                output += "added other player's session to waiting queue "
        else:
            output += "no other player "
        output += "active games: " + repr(ACTIVE_GAMES)
        print(output)
    
SESSIONS.put(session())
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_GAMES) as EXECUTOR:
    try:
        asyncio.get_event_loop().run_until_complete(websockets.serve(main, '74.208.211.192', 8080))
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as e:
        print("server shutdown")
        for future in FUTURES:
            future.cancel()
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().run_forever()
    finally:
        asyncio.get_event_loop().close()

