# -*- coding: utf-8 -*-
"""
@author: Charbel Marche, University of Mary Washington, fall 2017
"""

from chess_player import ChessPlayer
import copy
#from random import randint
import time

class hope_ChessPlayer(ChessPlayer):

    def __init__(self, board, color):
        super().__init__(board, color)
        
        #Figure out how deep we want to search, with each iteration being a ply
        self.maxiterations = 2
        
        self.time = 0
        
        self.ninf = -1000000
        self.inf = 1000000
        
        self.king = 100
        self.queen = 90
        self.princess = 70
        self.rook = 50
        self.fool = 50
        self.bishop = 30
        self.knight = 30
        self.pawn = 10
        self.maxRow = 0
        self.value = 0
        
        self.valueOfLast = self.ninf
        
        self.bestMove = Move(0, self.ninf*2, 0)
        
        self.moveNumber = 0
        
        self.pruned = 0
        self.numberOfMovesNotProperlyCalculated = 0
        self.numberOfMoves = 0
        self.quickValOn = True
        
        if (color == 'white'):
            self.adversaryColor = 'black'
        else:
            self.adversaryColor = 'white'

    def get_move(self, your_remaining_time, opp_remaining_time, prog_stuff):
        # YOUR MIND-BOGGLING CODE GOES HERE
        self.numberOfMovesNotProperlyCalculated = 0
        self.quickValOn = False
        self.ValueOfLast = self.getValue(self.board, False, 0)
        self.quickValOn = True
        if (self.moveNumber < 5 or self.board.is_king_in_check(self.color)):
            self.maxiterations = 1
            self.quickValOn = False
        else:
            self.maxiterations = 2
            self.quickValOn = True
        if(your_remaining_time < 40):
            self.maxiterations = 1
            self.quickValOn = False
        if (self.moveNumber == 0):
            if (self.color == 'white'):
                self.maxRow = int(self.board.get_king_location(self.adversaryColor)[1])
                if(self.maxRow == 6):
                    self.moveNumber += 1
                    return('d2', 'd3')
                    
            else:
                self.maxRow = int(self.board.get_king_location(self.color)[1])
                if(self.maxRow == 6):
                    self.moveNumber += 1
                    return('d5', 'd4')
        self.bestMove.clearMove()
        copiedBoard = copy.deepcopy(self.board)
        alpha_beta = [self.ninf*2, self.inf*2]
        self.time = time.time()
        self.getMaxMove(copiedBoard, alpha_beta, 0, 0)
        if (isinstance(self.bestMove.getMove(), int)):
            moves = copiedBoard.get_all_available_legal_moves(self.color)
            moves = self.orderMovesMax(moves, copiedBoard)
            print('HAD TO DO MINMAX CAUSE IT DIDNT GET A VALID MOVE')
            for move in moves:
                newBoard = copy.deepcopy(self.board)
                newBoard.make_move(move[0], move[1])
                self.quickValOn = False
                value = self.getValue(newBoard, False, False)
                if value > self.bestMove.getValue():
                    self.bestMove.setMove(move)
                    self.bestMove.setValue(value)
        print('PRUNED: ' + str(self.pruned))
        self.bestMove.printMove()
        self.moveNumber += 1
        self.valueOfLast = self.bestMove.getValue()
        return(self.bestMove.getMove())
    
    def getMaxMove(self, board, alpha_beta, iterations, toCompare):
        iterations += 1
        if (board.is_king_in_checkmate('black') or 
            board.is_king_in_checkmate('white') or 
            #(time.time() - self.time) > self.timelimit or
            iterations > self.maxiterations):
            #print(iterations)
            value = (self.getValue(board, True, toCompare))
            #print(str(time.time() - t0) + ' time to getValue!')
            return value
        value = (self.ninf)
        moves = board.get_all_available_legal_moves(self.color)
        self.numberOfMoves = len(moves)
        #t0 = time.time()
        moves = self.orderMovesMax(moves, board)
        #print(str(time.time() - t0) + ' time to order in MAX')
        #t0 = time.time()
        for potentialMove in moves:
            newBoard = copy.deepcopy(board)
            newBoard.make_move(potentialMove[0], potentialMove[1])
            value = max(value, 
                        self.getMinMove(newBoard, copy.deepcopy(alpha_beta), copy.copy(iterations), alpha_beta[1]))
            if(value > self.bestMove.getValue() and iterations == 1):
                self.bestMove.setValue(value)
                self.bestMove.setMove(potentialMove)
            if float(value) >= float(alpha_beta[1]):
                self.pruned += 1
                return value
            alpha_beta[0] = max(alpha_beta[0], value)
        #if(iterations == 1):
            #print(str(time.time() - t0) + ' time to do all of getting depth')
        return value
    
    def getMinMove(self, board, alpha_beta, iterations, toCompare):
        iterations += 1
        if (board.is_king_in_checkmate('black') or 
            board.is_king_in_checkmate('white') or
            #(time.time() - self.time) > self.timelimit or
            iterations > self.maxiterations):
            #print(iterations)
            value = (self.getValue(board, True, toCompare))
            return value
        value = (self.inf)
        moves = board.get_all_available_legal_moves(self.adversaryColor)
        #t0 = time.time()
        moves = self.orderMovesMin(moves, board)
        #print(str(time.time() - t0) + ' time to do all of getting order of MIN')
        for potentialMove in moves:
            #print("Itr: " + str(iterations) + "; alpha: " + str(alpha_beta[0]) + "; beta: " + str(alpha_beta[1]))
            newBoard = copy.deepcopy(board)
            newBoard.make_move(potentialMove[0], potentialMove[1])
            value = min(value, 
                         self.getMaxMove(newBoard, copy.deepcopy(alpha_beta), 
                                         copy.copy(iterations), alpha_beta[0]))
            #print('Value: ' + str(value))
            if float(value) <= float(alpha_beta[0]):
                self.pruned += 1
                #print('PRUNING ' + str(value) + '; Itr: ' + str(iterations) + "; alpha: " + str(alpha_beta[0]) + "; beta: " + str(alpha_beta[1]))
                return value
            alpha_beta[1] = min(alpha_beta[1], value)
        return value
                            
    def getValue(self, board, isMax, toCompare):
        self.value = 0
        maxPieces = self.getAllMaxPieces(board)
        minPieces = self.getAllMinPieces(board)
        if isMax:
            if (float(self.value) <= float(toCompare) or float(self.value) < self.valueOfLast) and self.quickValOn:
                self.rewardAdvancementOfPieces(maxPieces)
                self.evalCheckMate(board)
                #print('INACCURATE VAL OF A MOVE TO SAVE TIME')
                self.numberOfMovesNotProperlyCalculated += 1
                return self.value
        if isMax == False:
            if (float(self.value) >= float(toCompare) or float(self.value) > self.valueOfLast) and self.quickValOn:
                self.rewardAdvancementOfPieces(maxPieces)
                self.evalCheckMate(board)
                #print('INACCURATE VAL OF A MOVE TO SAVE TIME')
                return self.value
        threateningSquares = self.getAllThreateningSquares(board)
        threatenedSquares = self.getAllThreatenedSquares(board)
        threateningSquares = self.penalizeAllThreatenedPieces(threatenedSquares, threateningSquares, maxPieces)
        self.rewardAllThreateningPieces(threateningSquares, minPieces)
        self.rewardAdvancementOfPieces(maxPieces)
        self.rewardKingSafety(maxPieces, board)
        self.evalCheckMate(board)
        return(self.value)
    
    def rewardKingSafety(self, maxPieces, board):
        for piece in maxPieces:
            if (self.inProximity(piece.getLocation(), board.get_king_location(self.color))):
                print("Another piece around king")
                self.value += 5
                
    def inProximity(self, piece, king):
        if (int(king[1]) - int(piece[1]) != 1) or (int(king[1]) - int(piece[1]) != -1):
            return False
        piece = self.normalizeColumn(piece)
        king = self.normalizeColumn(king)
        if (int(king[0]) - int(piece[0]) != 1) or (int(king[0]) - int(piece[0]) != -1):
            return False
        return True
        
    def normalizeColumn(self, piece):
        if(piece[0] == 'a'):
            piece[0] = 1
        elif(piece[0] == 'b'):
            piece[0] = 2
        elif(piece[0] == 'c'):
            piece[0] = 3
        elif(piece[0] == 'd'):
            piece[0] = 4
        elif(piece[0] == 'e'):
            piece[0] = 5
        elif(piece[0] == 'f'):
            piece[0] = 6
        elif(piece[0] == 'g'):
            piece[0] = 7
        elif(piece[0] == 'h'):
            piece[0] = 8
        elif(piece[0] == 'j'):
            piece[0] = 9
        elif(piece[0] == 'k'):
            piece[0] = 10
        return piece
    
    def evalCheckMate(self, board):
        if board.is_king_in_checkmate(self.color):
            self.value += self.ninf
        elif board.is_king_in_checkmate(self.adversaryColor):
            self.value += self.inf
        elif board.is_king_in_check(self.color):
            self.value -= (self.inf)
        
    
    def rewardAdvancementOfPieces(self, maxPieces):
        for piece in maxPieces:
            if(self.color == 'white'):
                location = piece.getLocation()
                if (piece.getNotation() == 'P'):
                    if (location[1] == self.maxRow):
                        self.value = (self.value - self.pawn) + self.queen
                    else:
                        self.value += int(location[1]) * 2
                else:
                    self.value += int(location[1])
            else:
                location = piece.getLocation()
                if(piece.getNotation() == 'P'):
                    if (location[1] == 0):
                        self.value = (self.value + self.pawn)
                    else:
                        self.value += (self.maxRow - int(location[1])) * 2
                else:
                    self.value += self.maxRow - int(location[1])
        
    
    def penalizeAllThreatenedPieces(self, threatenedSquares, threateningSquares, maxPieces):
        for piece in maxPieces:
            for square in threatenedSquares:
                if piece.getLocation() == square[1]:
                    threateningSquares = self.removeThreateningForPiece(piece, threateningSquares)
                    self.value -= (self.getPieceValue(piece))
        return threateningSquares
                    
    def rewardAllThreateningPieces(self, theateningSquares, minPieces):
        for piece in minPieces:
            for square in theateningSquares:
                if piece.getLocation() == square[1]:
                    if(piece.getNotation() == 'K'):
                        return
                    else:
                        self.value += (self.getPieceValue(piece) / 50)
                    
    def removeThreateningForPiece(self, piece, threateningSquares):
        itr = 0
        while itr < len(threateningSquares):
            square = threateningSquares[itr]
            if (square[0] == piece.getLocation()):
                threateningSquares.pop(itr)
            else:
                itr += 1
        return threateningSquares
    
    def getAllThreatenedSquares(self, board):
        threatenedSquares = board.get_all_available_legal_moves(self.adversaryColor)
        return threatenedSquares
            
    def getAllThreateningSquares(self, board):
        threateningSquares = board.get_all_available_legal_moves(self.color)
        return threateningSquares
    
    def getAllMaxPieces(self, board):
        maxPieces = []
        for location, piece in board.items():
            if(self.color == 'white'):
                try:
                    if(piece.get_notation().isupper()):
                        pieceObj = Piece(piece.get_notation(), location)
                        maxPieces.append(pieceObj)
                        self.value = self.addPieceValueToValue(pieceObj)
                except:
                    maxPieces.append(piece = Piece('P', location))
                    self.value = self.value + self.pawn
            else:
                try:
                    if(piece.get_notation().islower()):
                        pieceObj = Piece(piece.get_notation().upper(), location)
                        maxPieces.append(pieceObj)
                        self.value = self.addPieceValueToValue(pieceObj)
                except:
                    maxPieces.append(piece = Piece('P', location))
                    self.value = self.value + self.pawn
        return maxPieces
    
    def getAllMinPieces(self, board):
        minPieces = []
        for location, piece in board.items():
            if(self.adversaryColor == 'white'):
                try:
                    if(piece.get_notation().isupper()):
                        pieceObj = Piece(piece.get_notation().upper(), location)
                        minPieces.append(pieceObj)
                        self.value = self.subtractPieceValueToValue(pieceObj)
                except:
                    minPieces.append(piece = Piece('P', location))
                    self.value = self.value - self.pawn
            else:
                try:
                    if(piece.get_notation().islower()):
                        pieceObj = Piece(piece.get_notation().upper(), location)
                        minPieces.append(pieceObj)
                        self.value = self.subtractPieceValueToValue(pieceObj)
                except:
                    minPieces.append(piece = Piece('P', location))
                    self.value = self.value - self.pawn
        return minPieces
            
    def addPieceValueToValue(self, piece):
        if (piece.getNotation() == 'N'):
            self.value = self.value + self.knight
        elif (piece.getNotation() == 'R'):
            self.value = self.value + self.rook
        elif (piece.getNotation() == 'B'):
            self.value = self.value + self.bishop
        elif (piece.getNotation() == 'Q'):
            self.value = self.value + self.queen
        elif (piece.getNotation() == 'S'):
            self.value = self.value + self.princess
        elif (piece.getNotation() == 'F'):
            self.value = self.value + self.fool
        elif (piece.getNotation() == 'K'):
            self.value = self.value + self.king
        elif (piece.getNotation() == 'P'):
            self.value = self.value + self.pawn
        return self.value
    
    def subtractPieceValueToValue(self, piece):
        if (piece.getNotation() == 'N'):
            self.value = self.value - self.knight
        elif (piece.getNotation() == 'R'):
            self.value = self.value - self.rook
        elif (piece.getNotation() == 'B'):
            self.value = self.value - self.bishop
        elif (piece.getNotation() == 'Q'):
            self.value = self.value - self.queen
        elif (piece.getNotation() == 'S'):
            self.value = self.value - self.princess
        elif (piece.getNotation() == 'F'):
            self.value = self.value - self.fool
        elif (piece.getNotation() == 'K'):
            self.value = self.value - self.king
        elif (piece.getNotation() == 'P'):
            self.value = self.value - self.pawn
        return self.value
    
    def getPieceValue(self, piece):
        if (piece.getNotation() == 'P'):
            return self.pawn
        elif (piece.getNotation() == 'N'):
            return self.knight
        elif (piece.getNotation() == 'R'):
            return self.rook
        elif (piece.getNotation() == 'B'):
            return self.bishop
        elif (piece.getNotation() == 'Q'):
            return self.queen
        elif (piece.getNotation() == 'K'):
            return self.king
        elif (piece.getNotation() == 'S'):
            return self.princess
        elif (piece.getNotation() == 'F'):
            return self.fool
        
    def orderMovesMax(self, moves, board):
        minPieces = self.getAllMinPieces(board)
        itr = 0 
        numberOfOnes = 0
        numberOfTwos = 0
        numberOfThrees = 0
        numberOfFours = 0
        while (itr < len(moves)):
            number = self.quickEvalMax(moves[itr], moves, minPieces, board)
            if(number == 1):
                move = moves.pop(itr)
                moves.insert(0, move)
                numberOfOnes += 1
            elif(number == 2):
                move = moves.pop(itr)
                moves.insert(numberOfOnes + 1, move)
                numberOfTwos += 1
            elif(number == 3):
                move = moves.pop(itr)
                moves.insert(numberOfOnes + numberOfTwos + 1, move)
                numberOfThrees += 1
            elif(number == 4):
                move = moves.pop(itr)
                moves.append(move)
                numberOfFours += 1
            itr += 1 
        return moves
    
    def orderMovesMin(self, moves, board):
        maxPieces = self.getAllMaxPieces(board)
        itr = 0 
        numberOfOnes = 0
        numberOfTwos = 0
        numberOfThrees = 0
        numberOfFours = 0
        while (itr < len(moves)):
            number = self.quickEvalMin(moves[itr], moves, maxPieces, board)
            if(number == 1):
                move = moves.pop(itr)
                moves.insert(0, move)
                numberOfOnes += 1
            elif(number == 2):
                move = moves.pop(itr)
                moves.insert(numberOfOnes + 1, move)
                numberOfTwos += 1
            elif(number == 3):
                move = moves.pop(itr)
                moves.insert(numberOfOnes + numberOfTwos + 1, move)
                numberOfThrees += 1
            elif(number == 4):
                move = moves.pop(itr)
                moves.append(move)
                numberOfFours += 1
            itr += 1 
        return moves
    
    def sacraficeWorthIt(self, pieceToSacrafice, pieceToSacraficeFor):
        if(pieceToSacrafice == pieceToSacraficeFor):
            return False
        if(pieceToSacraficeFor == 'P'):
            return False
        if(pieceToSacraficeFor == 'Q'):
            return True
        if(pieceToSacraficeFor == 'P' and pieceToSacrafice != 'Q'):
            return True
        if((pieceToSacraficeFor == 'R' or pieceToSacraficeFor == 'F') and pieceToSacrafice != 'Q' and pieceToSacrafice != 'P'):
            return True
        if(pieceToSacraficeFor == 'B' or pieceToSacraficeFor == 'N'):
            if (pieceToSacrafice == 'P'):
                return True
            else:
                return False
        return False

    
    def quickEvalMax(self, move, moves, opponentPieces, board):
        itr = 0 
        for piece in opponentPieces:
            if piece.getLocation() == moves[itr][1] and self.isProtectedMax(piece.getLocation(), board):
                if(self.sacraficeWorthIt(board[moves[itr][1]], piece.getNotation())):
                    return 2
                else: 
                    return 4
            elif piece.getLocation() == moves[itr][1] and not self.isProtectedMax(piece.getLocation(), board):
                #print(piece.getNotation())
                #print('_______________________')
                return 1
            elif (self.color == 'white'):
                if moves[itr][1][1]  > moves[itr][0][1]:
                    return 3
            elif (self.color == 'black'):
                if moves[itr][1][1]  < moves[itr][0][1]:
                    return 3
            else: 
                return 4
                
    
    def isProtectedMax(self, location, board):
        otherPlayerMoves = self.getAllThreatenedSquares(board)
        boardTmp = copy.deepcopy(board)
        for move in otherPlayerMoves:
            if move[0] == location:
                boardTmp.make_move(move[0], move[1])
                otherPlayerMoves = self.getAllThreatenedSquares(boardTmp)
                for move in otherPlayerMoves:
                    if move[1] == location:
                        return True
        return False
    
    def quickEvalMin(self, move, moves, opponentPieces, board):
        itr = 0 
        for piece in opponentPieces:
            if piece.getLocation() == moves[itr][1] and self.isProtectedMin(piece.getLocation(), board):
                if(self.sacraficeWorthIt(board[moves[itr][1]], piece.getNotation())):
                    return 2
                else: 
                    return 4
            elif piece.getLocation() == moves[itr][1] and not self.isProtectedMax(piece.getLocation(), board):
                #print(piece.getNotation())
                #print('_______________________')
                return 1
            elif (self.adversaryColor == 'white'):
                if moves[itr][1][1]  > moves[itr][0][1]:
                    return 3
            elif (self.adversaryColor == 'black'):
                if moves[itr][1][1]  < moves[itr][0][1]:
                    return 3
            else: 
                return 4
                
    
    def isProtectedMin(self, location, board):
        otherPlayerMoves = self.getAllThreateningSquares(board)
        boardTmp = copy.deepcopy(board)
        for move in otherPlayerMoves:
            if move[0] == location:
                boardTmp.make_move(move[0], move[1])
                otherPlayerMoves = self.getAllThreateningSquares(boardTmp)
                for move in otherPlayerMoves:
                    if move[1] == location:
                        return True
        return False
        
#    def orderMovesMin(self, moves, board):
#        maxPieces = self.getAllMaxPieces(board)
#        itr = 0 
#        numberOfCaptures = 0
#        while (itr < len(moves)):
#            for piece in maxPieces:
#                if piece.getLocation() == moves[itr][1]:
#                    move = moves.pop(itr)
#                    moves.insert(0, move)
#                    numberOfCaptures += 1         
#            itr += 1 
#        #TRY AND DO MOVES THAT LEAD TO SQUARES WHERE U THREATEN AND DONT GET KILLED?
#        itr = numberOfCaptures
#        numberOfAdvances = 0
#        while (itr < len(moves)):
#            if (self.adversaryColor == 'white'):
#                if moves[itr][1][1]  > moves[itr][0][1]:
#                    move = moves.pop(itr)
#                    moves.insert(numberOfCaptures, move)
#                    numberOfAdvances += 1
#            else:
#                if moves[itr][1][1]  < moves[itr][0][1]:
#                    move = moves.pop(itr)
#                    moves.insert(numberOfCaptures, move)
#                    numberOfAdvances += 1
#            itr += 1 
#        return moves
#
#    def orderMovesMax(self, moves, board):
#        minPieces = self.getAllMinPieces(board)
#        itr = 0 
#        numberOfCaptures = 0
#        while (itr < len(moves)):
#            for piece in minPieces:
#                if piece.getLocation() == moves[itr][1]:
#                    move = moves.pop(itr)
#                    moves.insert(0, move)
#                    numberOfCaptures += 1
#            itr += 1 
#        #TRY AND DO MOVES THAT LEAD TO SQUARES WHERE U THREATEN AND DONT GET KILLED?
#        itr = numberOfCaptures
#        numberOfAdvances = 0
#        while (itr < len(moves)):
#            if (self.color == 'white'):
#                if moves[itr][1][1]  > moves[itr][0][1]:
#                    move = moves.pop(itr)
#                    moves.insert(numberOfCaptures, move)
#                    numberOfAdvances += 1
#            else:
#                if moves[itr][1][1]  < moves[itr][0][1]:
#                    move = moves.pop(itr)
#                    moves.insert(numberOfCaptures, move)
#                    numberOfAdvances += 1
#            itr += 1 
#        return moves
    

class Piece():
    def __init__(self, notation, location):
        self.notation = notation
        self.location = location
        
    def getLocation(self):
        return self.location
    
    def getNotation(self):
        return self.notation
        
class Move():
    def __init__(self, move, value, board):
        self.move = move
        self.value = value
        self.board = board
        
    def getMove(self):
        return self.move
    
    def getValue(self):
        return self.value
    
    def getBoard(self):
        return self.board
    
    def setValue(self, value):
        self.value = value
        
    def setMove(self, move):
        self.move = move
        
    def setBoard(self, board):
        self.board = board
        
    def printMove(self):
        print('Move: ' + str(self.move))
        print('Value: ' + str(self.value))
        
    def clearMove(self):
        self.move = 0
        self.value = -1000000
        self.board = 0

        
        

