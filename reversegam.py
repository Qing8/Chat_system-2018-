import random
import sys

WIDTH = 8
HEIGHT = 8

def drawBoard(board):
    #print the board passed to this
    #funtion and  return NONE
    print("  12345678")
    print("  +------+")
    for y in range(HEIGHT):
        print("{0}|".format(y+1),end = "")
        for x in range(WIDTH):
            print(board[x][y],end="")
        print("|{0}".format(y+1))
    print("  +------+")
    print("  12345678")

def getNewBoard():
    # create a brand-new, blank board 
    # data structure
    board = []
    for i in range(WIDTH):
        board.append([" "," "," "," "," "," "," "," "])
    return board

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

def getBoardWithValidMoves(board,tile):
    # return a new board with periods marking the valid move the player can make
    boardCopy = getBoardCopy(board)
    
    for x,y in getValidMoves(boardCopy, tile):
        boardCopy[x][y] = "."
    return boardCopy

def getValidMoves(board,tile):
    # return a list of [x,y] lists of valid moves for the given player on the given board
    validMoves = []
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if isValidMove(board,tile,x,y) != False:
                validMoves.append([x,y])
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

def enterPlayerTile():
    # let the player enter which tile they want to be
    # return a list with the player's tile as the first item and computer's tile as the second
    
    tile = ""
    while not (tile == "X" or tile == "0"):
        tile = input("Do you want to be X or 0?").upper()
    # the first element in the list is the player's tile, and the second is the computer's tile
    if tile == "X":
        return ["X","0"]
    else:
        return ["0","X"]

def whoGoesFirst():
    # randomly choose who goes first
    if random.randint(0,1) == 0:
        return "computer"
    else:
        return "player"

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

def getBoardCopy(board):
    # make a duplicate of the board list and return it
    boardCopy = getNewBoard()
    for x in range(WIDTH):
        for y in range(HEIGHT):
            boardCopy[x][y] = board[x][y]
            
    return boardCopy

def isOnCorner(x,y):
    # return True if the position is in one of the four corners
    return (x==0 or x== WIDTH-1) and (y == 0 or y ==HEIGHT-1)

def getPlayerMove(board,playerTile):
    # let the player enter their move
    # return the move as [x,y] (or return the strings 'hints' or 'quit')
    DIGITSIT08 = '1 2 3 4 5 6 7 8'.split()
    while True:
        print("Enter your move, 'quit' to end the game, or 'hints' to toggle hints.")
        move = input().lower()
        if move == "quit" or move == "hints":
            return move
        
        if len(move) == 2 and move[0] in DIGITSIT08 and move[1] in DIGITSIT08:
            x = int(move[0]) -1
            y = int(move[1]) -1
            if isValidMove(board,playerTile,x,y) == False:
                continue
            else:
                break
        else:
            print("This is not a valid move, enter the column (1-8) and then the row(1-8)")
            print("For example, 81 will move on the top-right corner.")
    return [x,y] 

def getComputerMove(board,computerTile):
    # given a board and the computer's tile, determine where to move and return that mvoe as an [x,y] list.
    possibleMoves = getValidMoves(board,computerTile)
    # randomize the order of the moves
    random.shuffle(possibleMoves)
    # always go for a corner if available
    for x,y in possibleMoves:
        if isOnCorner(x,y):
            return [x,y]
    # find the highest-scoring move possible
    bestScore = -1
    for x,y in possibleMoves:
        boardCopy = getBoardCopy(board)
        makeMove(boardCopy,computerTile,x,y)
        score = getScoreOfBoard(boardCopy)[computerTile]
        if score > bestScore:
            bestMove = [x,y]
            bestScore = score
    return bestMove

def printScore(board,playerTile,computerTile):
    scores = getScoreOfBoard(board)
    print("You: {0} points\ncomputer: {1} points.".format(scores[playerTile],scores[computerTile]))
def playGame(playerTile, computerTile):
    showHints = False
    turn = whoGoesFirst()
    print("{0} goes first".format(turn))
    board = getNewBoard()
    board[3][3] = "X"
    board[3][4] = "0"
    board[4][3] = "0"
    board[4][4] = "X"
    
    while True:
        playerValidMoves = getValidMoves(board,playerTile)
        computerValidmoves = getValidMoves(board,computerTile)
        if playerValidMoves == [] and computerValidmoves == []:
            return board
        elif turn == "player":
            if playerValidMoves != []:
                if showHints:
                    validMovesBoard = getBoardWithValidMoves(board,playerTile)
                    drawBoard(validMovesBoard)
                else:
                    drawBoard(board)
                printScore(board,playerTile, computerTile)
                move = getPlayerMove(board,playerTile)
                if move == "quit":
                    print("Thanks for playing!")
                    #sys.exit()
                elif move == "hints":
                    showHints = not showHints
                    continue
                else:
                    makeMove(board,playerTile,move[0],move[1])
            turn = "computer" 
        elif turn == "computer":
            if computerValidmoves != []:
                drawBoard(board)
                printScore(board,playerTile,computerTile)
                input("Press Enter to see the computer's move")
                move = getComputerMove(board,computerTile)
                makeMove(board,computerTile,move[0],move[1])
                turn = "player"
def start():
    print("Welcome to Reversegam!")
    
    playerTile, computerTile = enterPlayerTile()
    while True:
        finalBoard = playGame(playerTile,computerTile)
        
        # display the final score
        drawBoard(finalBoard)
        scores = getScoreOfBoard(finalBoard)
        print("X scored {0} points, 0 scores {1} points.".format(scores['X'],scores['0']))
        if scores[playerTile] > scores[computerTile]:
            print("You beat the computer by {0} points".format(scores[playerTile]-scores[computerTile]))
#            result = "You beat the computer by {0} points".format(scores[playerTile]-scores[computerTile])
        elif scores[playerTile] < scores[computerTile]:
            print("You lost the computer by {0} points".format(-scores[playerTile]+scores[computerTile]))
#            result = ("You lost the computer by {0} points".format(-scores[playerTile]+scores[computerTile]))
        else:
            print("it's a tie")
#            result = "it's a tie"
        print("Do you want to play again? \n(yes or no)")
        if not input().lower().startwith('y'):

            break