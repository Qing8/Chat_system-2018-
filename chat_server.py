"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import reversegam as game
import random

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        # game
        self.name2sign = {}
        self.board = self.getNewBoard()
        self.board[3][3] = "X"
        self.board[3][4] = "0"
        self.board[4][3] = "0"
        self.board[4][4] = "X"
        
    def getNewBoard(self):
        # create a brand-new, blank board 
        # data structure
        graph = []
        for i in range(8):
            graph.append([" "," "," "," "," "," "," "," "])
        return graph
        

    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        #move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        #add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        #load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name]=pkl.load(open(name+'.idx','rb'))
                            except IOError: #chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps({"action":"login", "status":"ok"}))
                    else: #a client under this name has already logged in
                        mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print ('wrong code received')
            else: #client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code
        msg = myrecv(from_sock)
        WIDTH = 8
        HEIGHT = 8
        
#        def getNewBoard():
#            # create a brand-new, blank board 
#            # data structure
#            graph = []
#            for i in range(WIDTH):
#                graph.append([" "," "," "," "," "," "," "," "])
#            return graph
#        
        def drawboard(board):
                
            graph = ''
#            board[3][3] = "X"
#            board[3][4] = "0"
#            board[4][3] = "0"
#            board[4][4] = "X"
            graph += ("  12345678") + "\n"
            graph += ("  +------+") + "\n"
            for y in range(8):
                graph += "{0}|".format(y+1)
                for x in range(8):
                    graph += self.board[x][y] 
                graph += "|{0}".format(y+1) + "\n"
            graph += "  +------+" + "\n"
            graph += "  12345678" + "\n"
            return graph
        
        def isValidMove(board, tile, xstart, ystart):
            
            
            # return False if the player's 
            # move on space xstart, ystart 
            # is invalid
            
            # if it is a valid move, return
            # a list of spaces that would 
            # become the player's if they 
            # made a move here
            
            if board[xstart][ystart] != " " or not isOnBoard(xstart,ystart):
                return False
            if tile == "X":
                otherTile = "0"
            else:
                otherTile = "X"
            tilesToFlip = []
            
            for xdirection, ydirection in [[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]:
                x, y = xstart, ystart
                x += xdirection
                y += ydirection
                while isOnBoard(x,y) and board[x][y] == otherTile:
                    # keep moving in this x&y direction
                    x += xdirection
                    y += ydirection
                    
                    if isOnBoard(x, y) and board[x][y] == tile:
                        # there are pieces to flip over, go in the reverse direction 
                        # until we reach the original space, noting all the tiles 
                        # along the way.
                        
                        while True:
                            x -= xdirection
                            y -= ydirection
                            
                            if x == xstart and y == ystart:
                                break
                            tilesToFlip.append([x,y])
            
            if len(tilesToFlip) == 0:
                return False
            return tilesToFlip
        def isOnBoard(x, y):
            return 0 <= x <= WIDTH-1 and 0 <= y <= HEIGHT-1

        
        def getValidMoves(board,tile):
            # return a list of [x,y] lists of valid moves for the given player on the given board
            validMoves = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if isValidMove(self.board,tile,x,y) != False:
                        validMoves.append([x+1,y+1])
            return validMoves
        
        def getScoreOfBoard(board):
            # determine the score by counting the tiles. return a dictionary with key "x"&"0"
            xscore = 0
            oscore = 0
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if board[x][y] == "X":
                        xscore += 1
                    if board[x][y] == "0":
                        oscore += 1
            return {"X":xscore, "0":oscore} 

            
        def whoGoesFirst():
            # randomly choose who goes first
            if random.randint(0,1) == 0:
                return 1
            else:
                return 2
    
        def makeMove(board,tile,xstart,ystart):
            # place the tile on the board at xstart, ystart and flip any of the opponent's pieces
            # return False if this is an invalid move, True if it is valid
            tilesToFlip = isValidMove(board,tile,xstart,ystart)
            if tilesToFlip == False:
                return False
            
            board[xstart][ystart] = tile
            for x,y in tilesToFlip:
                board[x][y] = tile
            return True
        
        

    

        def printScore(board,playerTile,computerTile):
            scores = getScoreOfBoard(self.board)
            print("You: {0} points\ncomputer: {1} points.".format(scores[playerTile],scores[computerTile]))


    
        if len(msg) > 0:
#==============================================================================
# handle connect request
#==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"connect", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"connect", "status":"no-user"})
                mysend(from_sock, msg)
                
            elif msg["action"] == "game connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"game connect", "status":"self"})
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.game_connect(from_name, to_name)
                    the_guys = self.group.list_game_me(from_name)

                    msg = json.dumps({"action":"game connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"game connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"game connect", "status":"no-user"})
                mysend(from_sock, msg)
            
     
                
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                #said = msg["from"]+msg["message"]
                said2 = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))
#==============================================================================
#                 listing available peers
#==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_sect(poem_indx)
                print('here:\n', poem)
                mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action":"time", "results":ctime}))
#==============================================================================
#                 search
#==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                search_rslt = (self.indices[from_name].search(term)).strip()
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"disconnect"}))
                    
                    
#---------------------------------------------------------------------------
#                 game                       
#---------------------------------------------------------------------------
            elif msg["action"] == "draw graph":
                
                drawboard = drawboard(self.board)
                                              
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_game_me(from_name)
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"draw board graph", "result":drawboard}))
            
            elif msg["action"] == "who goes first":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_game_me(from_name)
                
                result = whoGoesFirst()
                
                if result == 1:
                    turn = the_guys[0]
                    self.name2sign[turn] = "X"
                    self.name2sign[the_guys[1]] = "0"
                    
                elif result == 2:
                    turn = the_guys[1]
                    self.name2sign[turn] = "X"
                    self.name2sign[the_guys[0]] = "0"
                    

                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"who goes first", "order":turn,"sign":self.name2sign[g]}))

            elif msg["action"] == "check move":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_game_me(from_name)
                playersign = self.name2sign[from_name]
                validmoves = getValidMoves(self.board,playersign)
                if validmoves == []:
                    for g in the_guys:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"check move", "message":"You lose","from":from_name}))
                elif validmoves != []:
                    for g in the_guys:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"check move", "message":"Okay","from":from_name}))
                        
            elif msg["action"] == "make move":

                from_name = self.logged_sock2name[from_sock]
                column = int(msg["move"][0])-1
                row = int(msg["move"][1])-1
                playersign = self.name2sign[from_name]
                makeMove(self.board,playersign,column,row)
                finalboard = drawboard(self.board)
                the_guys = self.group.list_game_me(from_name)
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"make move", "message":finalboard}))

            elif msg["action"] == "quit game":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_game_me(from_name)
                self.group.game_disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:
                    for g in the_guys:
                        g = the_guys.pop()
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"quit game"}))
                self.board = self.getNewBoard()
                self.board[3][3] = "X"
                self.board[3][4] = "0"
                self.board[4][3] = "0"
                self.board[4][4] = "X"
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================

        else:
            #client died unexpectedly
            self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)

def main():
    server=Server()
    server.run()

main()
