"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
#import reversegam
import random

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
    
    def game_connect(self,peer):
        msg = json.dumps({"action":"game connect","target":peer})
        mysend(self.s,msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You may play game with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play with yourself (sick)\n'
        else:
            self.out_msg += 'player is not online, try again later\n'
        return(False)
        
        
    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
    
    
        
        
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                
                elif my_msg[0] == "g":
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.game_connect(peer) == True:
                        self.state = S_GAME
                        self.out_msg += "Game with  " + peer
                        self.out_msg += '-----------------------------------\n'
                        self.out_msg += "\n"+menu2
#                        mysend(self.s,json.dumps({"action":"who goes first"}))
                        
#                        # draw the borad graph
#                        mysend(self.s, json.dumps({"action":"draw board graph"}))
#                        graph = json.loads(myrecv(self.s))["result"]
#                        self.out_msg += graph
                    
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                    
                    
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                
                        

                else:
                    self.out_msg += menu 

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                elif peer_msg["action"] == "game connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += "  You are on game with " + self.peer
                    self.out_msg += "\n" + menu2
                    self.state = S_GAME
                

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#===========================================================================
# game statede
#==========================================================================
        elif self.state == S_GAME:
            
            if len(my_msg) > 0:
                if my_msg == "who goes first":
                    mysend(self.s, json.dumps({"action":"who goes first"}))
                    msg = json.loads(myrecv(self.s))
                    self.out_msg += msg["order"] + " goes first"
                    sign = msg["sign"]
                    self.out_msg += ". \nYour sign is " + sign
                    if msg["order"] == self.me:
                        self.state = S_GAME
                        self.out_msg += "\nTYPE IN 'move' BEFORE EVERY MOVE!!!!!!!!!!\n"
                    else:
                        self.out_msg += "\nWait!"
                        self.state = S_GAMEWAIT
                    
                elif my_msg == "ready":
                    mysend(self.s,json.dumps({"action":"draw graph"}))
                    msg = json.loads(myrecv(self.s))["result"]
                    self.out_msg += msg
        
                elif len(my_msg)==2 and my_msg.isdigit() == True:
                    mysend(self.s,json.dumps({"action":"make move","move":my_msg}))
                    msg = json.loads(myrecv(self.s))["message"]
                    self.out_msg += msg
                    self.state = S_GAMEWAIT
                    self.out_msg += "Wait for {0}'s move".format(self.peer)
                # elif quit the game
                elif my_msg == "move":
                    mysend(self.s,json.dumps({"action":"check move"}))
                    msg = json.loads(myrecv(self.s))["message"]
                    if msg == "You lose":
                        self.out_msg += "Sorry you lose, Maybe next time"
                        self.state = S_ENDGAME
                    elif msg == "Okay":
                        self.out_msg += "Type in your move which consists of two numbers (ColumnRow)"
                        
                elif my_msg == "bye":
                    mysend(self.s,json.dumps({"action":"quit game"}))
                    self.out_msg += "See you next time!"
                    #####################
                    self.state = S_ENDGAME
                        
                else:
                    self.out_msg += menu2
                
                if self.state == S_ENDGAME:
                    self.out_msg += menu
                    
                    
            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "who goes first":
                    order = peer_msg["order"]
                    sign = peer_msg["sign"]
                    self.out_msg += order + " goes first"
                    self.out_msg += ".\nYour sign is " + sign
                    if self.me == order:
                        self.state = S_GAME
                        self.out_msg += "\nTYPE IN 'move' BEFORE EVERY MOVE!!!!!!!!!!\n"
                    else:
                        self.state = S_GAMEWAIT
                        self.out_msg += "\nWait!"
                elif peer_msg["action"] == "make move":
                    
                    self.out_msg += peer_msg["message"]
                    
                elif peer_msg["action"] == "check move":
                    msg = peer_msg["message"]
#                    if msg == "Okay":
#                        self.out_msg += "Wait for {0}'s move".format(peer_msg["from"])
               ###########################
                if self.state == S_ENDGAME:
                    self.out_msg += menu
                    self.state = S_LOGGEDIN
#        elif self.state == S_ENDGAME:
#            self.out_msg += menu
            
        elif self.state == S_GAMEWAIT:
            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
    
                if peer_msg["action"] == "check move":
                    msg = peer_msg["message"]
                    if msg == "Okay":
#                        self.state = S_GAME
                        self.out_msg += "{0} is thinking and about to move".format(peer_msg["from"])
                    elif msg == "You lose":
                        self.out_msg += "Congrates! You won the game!"
                        self.state = S_ENDGAME
                        
                elif peer_msg["action"] == "make move":
                
                    self.state = S_GAME
                    self.out_msg += peer_msg["message"]
                    self.out_msg += "\nNow it's your turn"
                    self.out_msg += "\n TYPE IN 'move' BEFORE EVERY MOVE"
                
                elif peer_msg["action"] == "quit game":
                    self.out_msg += "The opposite side quits!"
                    self.state = S_ENDGAME
                    
                if self.state == S_ENDGAME:
                    self.out_msg += "\n" + menu
                    self.state = S_LOGGEDIN
        elif self.state == S_ENDGAME:
            self.state = S_LOGGEDIN
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
