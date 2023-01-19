import pygame

import time
import threading

searched = {}


def negamax(state, depth, alpha, beta, colorsign, bestMoveReturn, root=True):
    global searched
    if depth == 0:
        return colorsign * state.eval()

    moves = state.allvalidMoves(state.opp)
    if not moves:
        return colorsign * state.eval()

    if root:
        bestMove = moves[0]
    bestValue = -100000
    for move in moves:
        state_aux = state.clone()
        board = state_aux.board
        move_aux = Move(move[0][0], move[0][1], move[1][0], move[1][1], board)
        state_aux.makeMove(move_aux)
        key = state_aux.pos2key()
        if key in searched:
            value = searched[key]
        else:
            value = -negamax(state_aux, depth - 1, -beta, -alpha, -colorsign, [], False)
            searched[key] = value
        if value > bestValue:
            bestValue = value
            if root:
                bestMove = move
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    if root:
        searched = {}
        bestMoveReturn[:] = bestMove
        return

    return bestValue


WIDTH = HEIGHT = 512
DIMENSION = 8
SQR_SIZE = HEIGHT // DIMENSION
MENU_SINGLE = pygame.transform.scale(pygame.image.load("menu/single.png"), (4 * SQR_SIZE, 4 * SQR_SIZE))
MENU_MULTI = pygame.transform.scale(pygame.image.load("menu/multi.png"), (3 * SQR_SIZE, 3 * SQR_SIZE))
MENU_WHITE = pygame.transform.scale(pygame.image.load("menu/white.png"), (3 * SQR_SIZE, 3 * SQR_SIZE))
MENU_BLACK = pygame.transform.scale(pygame.image.load("menu/black.png"), (3 * SQR_SIZE, 3 * SQR_SIZE))
MENU_SINGLE1 = pygame.transform.scale(pygame.image.load("menu/single1.png"), (4 * SQR_SIZE, 2 * SQR_SIZE))
MENU_MULTI1 = pygame.transform.scale(pygame.image.load("menu/multi1.png"), (4 * SQR_SIZE, 2 * SQR_SIZE))
MENU_WHITE1 = pygame.transform.scale(pygame.image.load("menu/white1.png"), (4 * SQR_SIZE, 2 * SQR_SIZE))
MENU_BLACK1 = pygame.transform.scale(pygame.image.load("menu/black1.png"), (4 * SQR_SIZE, 2 * SQR_SIZE))
WHITE_WINNER = pygame.transform.scale(pygame.image.load('winner/white.jpg'), (8 * SQR_SIZE, 8 * SQR_SIZE))
BLACK_WINNER = pygame.transform.scale(pygame.image.load('winner/black.jpg'), (8 * SQR_SIZE, 8 * SQR_SIZE))
SONG1 = 'music/song1.mp3'
PIECE_SOUND = 'music/piece_sound.wav'
FPS = 60
IMG = {}
BOARD = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

TOMOVE = 'w'
OPP = 'b'
WKINGPOS = (7, 4)
BKINGPOS = (0, 4)
WCASTLEQ = True
WCASTLEK = True
BCASTLEQ = True
BCASTLEK = True
ENP = -1


def LoadImages():  # funcao que carrega as sprites das peças
    pieces = ["bB", "bK", "bN", "bp", "bQ", "bR", "wB", "wK", "wN", "wp", "wQ", "wR"]
    for piece in pieces:
        IMG[piece] = pygame.transform.scale(pygame.image.load("img/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(SONG1)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    move_sound = pygame.mixer.Sound(PIECE_SOUND)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("black"))
    state = State(BOARD, TOMOVE, OPP, WKINGPOS, BKINGPOS, WCASTLEQ,
                  WCASTLEK,
                  BCASTLEQ,
                  BCASTLEK,
                  ENP)
    LoadImages()
    sqrSelected = ()
    listofMoves = []
    isDown = False
    running = True
    isMenu = True
    isMenu2 = False
    isGameOver = False
    AI_Color = 'b'
    Player = 'w'
    colorsign = -1

    while running:
        if isMenu:
            drawMenu(screen)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // SQR_SIZE
                    if col < 4:
                        AI = False
                    else:
                        AI = True
                        isMenu2=True
                    isMenu=False
        elif isMenu2:
            screen.fill(pygame.Color("black"))
            drawMenuColor(screen)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] / SQR_SIZE
                    if col < 4.5:
                        colorsign = -1
                        Player = 'w'
                        AI_Color = 'b'
                    else:
                        colorsign = 1
                        Player = 'b'
                        AI_Color = 'w'
                    isMenu2=False
        else:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

                elif not isDown and e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // SQR_SIZE
                    row = pos[1] // SQR_SIZE
                    sqrSelected = (row, col)
                    toPlay = state.toMove
                    if not state.isSqrOccupiedby(row, col, toPlay):
                        continue

                    listofMoves = state.validMoves(row, col, state.opp)
                    listofallMoves = state.allvalidMoves(state.opp)
                    isDown = True

                elif isDown and e.type == pygame.MOUSEBUTTONUP:
                    if state.toMove == Player or not AI:
                        isDown = False
                        pos = pygame.mouse.get_pos()
                        col2 = pos[0] // SQR_SIZE
                        row2 = pos[1] // SQR_SIZE
                        print("Peca:")
                        print((row2, col2))
                        print("Lista de Movimento da peca:")
                        print(listofMoves)
                        print("Lista de Movimento do jogador:")
                        print(listofallMoves)
                        print(state.eval())

                        if not (row2, col2) in listofMoves:
                            continue
                        move = Move(row, col, row2, col2, state.board)
                        state.makeMove(move)
                        pygame.display.flip()
                        pygame.mixer.Sound.play(move_sound)
                elif state.toMove == AI_Color and AI:
                    bestMoveReturn = []
                    move_thread = threading.Thread(target=negamax,
                                                   args=(state, 3, -1000000, 1000000, colorsign, bestMoveReturn))
                    move_thread.start()
                    while move_thread.is_alive():

                        pygame.display.flip()
                    row, col = bestMoveReturn[0]
                    row2, col2 = bestMoveReturn[1]
                    move = Move(row, col, row2, col2, state.board)
                    state.makeMove(move)
                    pygame.display.flip()
                    pygame.mixer.Sound.play(move_sound)
                elif state.isCheckmate('w') or state.isCheckmate('b') or state.isStalemate('w') or state.isStalemate('b'):
                    time.sleep(5)
                    running = False
            drawGame(screen, state, listofMoves, sqrSelected)
        clock.tick(FPS)
        pygame.display.flip()


def drawWinner(screen, color):
    if color == 'w':
        screen.blit(WHITE_WINNER, pygame.Rect(0 * SQR_SIZE, 0 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    else:
        screen.blit(BLACK_WINNER, pygame.Rect(0 * SQR_SIZE, 0 * SQR_SIZE, SQR_SIZE, SQR_SIZE))


def drawMenu(screen):
    pygame.draw.rect(screen, pygame.Color('white'), pygame.Rect(4 * SQR_SIZE, 1 * SQR_SIZE, 4 * SQR_SIZE, 6 * SQR_SIZE))
    pygame.draw.rect(screen, pygame.Color('white'), pygame.Rect(0 * SQR_SIZE, 1 * SQR_SIZE, 4 * SQR_SIZE, 6 * SQR_SIZE))
    screen.blit(MENU_SINGLE, pygame.Rect(4 * SQR_SIZE, 1 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_SINGLE1, pygame.Rect(4 * SQR_SIZE, 5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_MULTI, pygame.Rect(0.5 * SQR_SIZE, 1.5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_MULTI1, pygame.Rect(0 * SQR_SIZE, 5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))

def drawMenuColor(screen):
    pygame.draw.rect(screen, pygame.Color('white'), pygame.Rect(4 * SQR_SIZE, 1 * SQR_SIZE, 4 * SQR_SIZE, 6 * SQR_SIZE))
    pygame.draw.rect(screen, pygame.Color('white'), pygame.Rect(0 * SQR_SIZE, 1 * SQR_SIZE, 4 * SQR_SIZE, 6 * SQR_SIZE))
    screen.blit(MENU_BLACK, pygame.Rect(4.5 * SQR_SIZE, 1.5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_WHITE, pygame.Rect(0.5 * SQR_SIZE, 1.5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_BLACK1, pygame.Rect(0 * SQR_SIZE, 5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))
    screen.blit(MENU_WHITE1, pygame.Rect(4 * SQR_SIZE, 5 * SQR_SIZE, SQR_SIZE, SQR_SIZE))

def drawGame(screen, state, listofMoves, sqrSelected):
    drawBoard(screen)
    drawHighlights(screen, listofMoves, state, sqrSelected)
    drawPieces(screen, state)


def drawBoard(screen):
    colors = [pygame.Color("white"), pygame.Color(75, 115, 153)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQR_SIZE, r * SQR_SIZE, SQR_SIZE, SQR_SIZE))


def drawPieces(screen, state):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = state.board[r][c]
            if piece != 0:
                screen.blit(IMG[piece], pygame.Rect(c * SQR_SIZE, r * SQR_SIZE, SQR_SIZE, SQR_SIZE))


def drawHighlights(screen, listofMoves, state, sqrSelected):
    if sqrSelected != ():
        r, c = sqrSelected
        if state.isSqrOccupiedby(r, c, state.toMove):
            s = pygame.Surface((SQR_SIZE, SQR_SIZE))
            s.set_alpha(200)
            s.fill(pygame.Color(117, 199, 232))
            screen.blit(s, (c * SQR_SIZE, r * SQR_SIZE))
            for move in listofMoves:
                r2, c2 = move
                pygame.draw.circle(screen, (210, 209, 189), (c2 * SQR_SIZE + 32, r2 * SQR_SIZE + 30), 12)
    if state.lastMove != -1:
        r, c, r2, c2 = state.lastMove
        s = pygame.Surface((SQR_SIZE, SQR_SIZE))
        s.set_alpha(120)
        s.fill(pygame.Color("yellow"))
        screen.blit(s, (c * SQR_SIZE, r * SQR_SIZE))
        screen.blit(s, (c2 * SQR_SIZE, r2 * SQR_SIZE))
    if state.isCheck('b'):
        r, c = state.WKingPos
        s = pygame.Surface((SQR_SIZE, SQR_SIZE))
        s.set_alpha(120)
        s.fill(pygame.Color("red"))
        screen.blit(s, (c * SQR_SIZE, r * SQR_SIZE))
    if state.isCheck('w'):
        r, c = state.BKingPos
        s = pygame.Surface((SQR_SIZE, SQR_SIZE))
        s.set_alpha(120)
        s.fill(pygame.Color("red"))
        screen.blit(s, (c * SQR_SIZE, r * SQR_SIZE))
import copy
from collections import Counter


class State():  # Classe que representa o tabuleiro atual
    def __init__(self, board, toMove, opp, WKingPos, BKingPos, WCastleQ, WCastleK, BCastleQ, BCastleK,
                 enP):
        self.board = board
        self.toMove = toMove
        self.opp = opp
        self.WKingPos = WKingPos
        self.BKingPos = BKingPos
        self.WCastleQ = WCastleQ
        self.WCastleK = WCastleK
        self.BCastleQ = BCastleQ
        self.BCastleK = BCastleK
        self.enP = enP
        self.lastMove = -1
        self.moveLog = []

    def getboard(self):
        return self.board

    def clone(self):
        clone = State(copy.deepcopy(self.board), self.toMove, self.opp, copy.deepcopy(self.WKingPos),
                      copy.deepcopy(self.BKingPos), self.WCastleQ, self.WCastleK, self.BCastleQ, self.BCastleK,
                      self.enP)
        return clone

    def makeMove(self, move, Test=False):

        type = move.typeMoved
        toMove = move.colorMoved
        if not (move.endCol == move.startCol and move.endRow == move.startRow):
            if type == 'R':
                if toMove == 'w':
                    if move.startRow == 7 and move.startCol == 0:
                        self.WCastleQ = False
                    if move.startRow == 7 and move.startCol == 7:
                        self.WCastleK = False
                if toMove == 'b':
                    if move.startRow == 0 and move.startCol == 0:
                        self.BCastleQ = False
                    if move.startRow == 0 and move.startCol == 7:
                        self.BCastleK = False
            elif type == 'K':
                if toMove == 'w':
                    self.WCastleQ = False
                    self.WCastleK = False
                    self.WKingPos = (move.endRow, move.endCol)

                    if abs(move.endCol - move.startCol) == 2:
                        if move.endCol == 6:
                            self.board[7][7] = 0
                            self.board[7][5] = 'wR'
                        else:
                            self.board[7][0] = 0
                            self.board[7][3] = 'wR'

                elif toMove == 'b':
                    self.BCastleQ = False
                    self.BCastleK = False
                    self.BKingPos = (move.endRow, move.endCol)
                    if abs(move.endCol - move.startCol) == 2:
                        if move.endCol == 6:
                            self.board[0][7] = 0
                            self.board[0][5] = 'bR'
                        else:
                            self.board[0][0] = 0
                            self.board[0][3] = 'bR'
            elif type == 'p':
                if self.enP == (move.endRow, move.endCol):
                    print(self.enP)
                    if toMove == 'w':
                        self.board[move.endRow + 1][move.endCol] = 0
                    if toMove == 'b':
                        self.board[move.endRow - 1][move.endCol] = 0

                if abs(move.endRow - move.startRow) == 2:
                    self.enP = (int((move.endRow + move.startRow) / 2), move.endCol)
                else:
                    self.enP = -1

                if move.endRow == 0 or move.endRow == 7:
                    move.pieceMoved = toMove + 'Q'
            else:
                self.enP = -1
            self.board[move.startRow][move.startCol] = 0
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.lastMove = (move.startRow, move.startCol, move.endRow, move.endCol)
            if not Test:
                self.toMove = self.opp
                self.opp = toMove
                self.moveLog.append(move)

    def isSqrOccupiedby(self, row, col, color):
        if self.board[row][col] == 0:
            return False

        if self.board[row][col][0] == color:
            return True
        return False

    def isSqrOccupied(self, row, col):

        if self.board[row][col] == 0:
            return False
        return True

    def validMoves(self, row, col, opp_color, AttackSearch=False):
        listofMoves = []
        type = self.board[row][col][1]
        color = self.board[row][col][0]

        if type == 'p':  # Se a peca  for um peao
            if color == 'w':  # Se a peca  for um peao branco mostra todos os movimentos possiveis
                if not self.isSqrOccupied(row - 1, col) and not AttackSearch:
                    listofMoves.append((row - 1, col))
                    if row == 6 and not self.isSqrOccupied(row - 2, col):
                        listofMoves.append((row - 2, col))
                if col != 0 and self.isSqrOccupiedby(row - 1, col - 1, 'b'):
                    listofMoves.append((row - 1, col - 1))
                if col != 7 and self.isSqrOccupiedby(row - 1, col + 1, 'b'):
                    listofMoves.append((row - 1, col + 1))
                if self.enP != -1:
                    if self.enP == (row - 1, col + 1) or self.enP == (row - 1, col - 1):
                        listofMoves.append(self.enP)

            elif color == 'b':
                if not self.isSqrOccupied(row + 1, col) and not AttackSearch:
                    listofMoves.append((row + 1, col))
                    if row == 1 and not self.isSqrOccupied(row + 2, col):
                        listofMoves.append((row + 2, col))

                if col != 0 and self.isSqrOccupiedby(row + 1, col - 1, 'w'):
                    listofMoves.append((row + 1, col - 1))
                if col != 7 and self.isSqrOccupiedby(row + 1, col + 1, 'w'):
                    listofMoves.append((row + 1, col + 1))
                if self.enP != -1:
                    if self.enP == (row + 1, col - 1) or self.enP == (row + 1, col + 1):
                        listofMoves.append(self.enP)

        elif type == 'N':
            for change_row in [-2, -1, 1, 2]:
                if abs(change_row) == 2:
                    change_col2 = 1
                else:
                    change_col2 = 2
                for change_col in [-change_col2, change_col2]:
                    listofMoves.append((row + change_row, col + change_col))
            listofMoves = self.filterMoves(listofMoves, color)

        elif type == 'Q' or type == 'R' or type == 'B':
            if type != 'B':
                for dir in [-1, 1]:
                    change_row = row
                    while True:
                        change_row = change_row + dir
                        if 0 <= change_row <= 7:
                            if not self.isSqrOccupied(change_row, col):
                                listofMoves.append((change_row, col))
                            else:
                                if self.isSqrOccupiedby(change_row, col, opp_color):
                                    listofMoves.append((change_row, col))
                                break
                        else:
                            break

                for dir2 in [-1, 1]:
                    change_col = col
                    while True:
                        change_col = change_col + dir2
                        if 0 <= change_col <= 7:
                            if not self.isSqrOccupied(row, change_col):
                                listofMoves.append((row, change_col))
                            else:
                                if self.isSqrOccupiedby(row, change_col, opp_color):
                                    listofMoves.append((row, change_col))
                                break
                        else:
                            break
            if type != 'R':  # Fazer BISPO
                for dir_row in [-1, 1]:
                    for dir_col in [-1, 1]:
                        change_row = row
                        change_col = col
                        while True:
                            change_row = change_row + dir_row
                            change_col = change_col + dir_col
                            if 0 <= change_row <= 7 and 0 <= change_col <= 7:
                                if not self.isSqrOccupied(change_row, change_col):
                                    listofMoves.append((change_row, change_col))
                                else:
                                    if self.isSqrOccupiedby(change_row, change_col, opp_color):
                                        listofMoves.append((change_row, change_col))
                                    break
                            else:
                                break

        elif type == 'K':
            for change_row in [-1, 0, 1]:
                for change_col in [-1, 0, 1]:
                    listofMoves.append((row + change_row, col + change_col))
            listofMoves = self.filterMoves(listofMoves, color)
            if self.toMove == 'w':
                if self.WCastleK:
                    if not self.isSqrOccupied(7, 5) and not self.isSqrOccupied(7, 6):
                        listofMoves.append((7, 6))
                if self.WCastleQ:
                    if not self.isSqrOccupied(7, 3) and not self.isSqrOccupied(7, 2) and not self.isSqrOccupied(7, 1):
                        listofMoves.append((7, 2))
            if self.toMove == 'b':
                if self.BCastleK:
                    if not self.isSqrOccupied(0, 5) and not self.isSqrOccupied(0, 6):
                        listofMoves.append((0, 6))
                if self.BCastleQ:
                    if not self.isSqrOccupied(0, 3) and not self.isSqrOccupied(0, 2) and not self.isSqrOccupied(0, 1):
                        listofMoves.append((0, 2))

        if not AttackSearch:
            legal_moves = []
            for move in listofMoves:

                row2 = move[0]
                col2 = move[1]
                state_aux = self.clone()
                move_aux = Move(row, col, row2, col2, state_aux.board)
                state_aux.makeMove(move_aux, True)
                if not state_aux.isCheck(opp_color):
                    legal_moves.append(move)
            listofMoves = legal_moves
        return listofMoves

    def filterMoves(self, listofMoves, color):
        newList = []
        for move in listofMoves:
            row = move[0]
            col = move[1]
            if 0 <= row <= 7 and 0 <= col <= 7 and not self.isSqrOccupiedby(row, col, color):
                newList.append(move)

        return newList

    def isSquareAttackedby(self, sqr_row, sqr_col):
        board = self.board
        color = self.opp
        listofAttackedSqrs = []
        for row in range(8):
            for col in range(8):
                if board[row][col] != 0 and board[row][col][0] == color:
                    listofAttackedSqrs.extend(self.validMoves(row, col, self.toMove, True))
        return (sqr_row, sqr_col) in listofAttackedSqrs

    def LookforPiece(self, piece):
        listofLocations = []
        board = self.board

        for row in range(8):
            for col in range(8):
                if board[row][col] == piece:
                    listofLocations.append((row, col))
        return listofLocations

    def LookforColorPieces(self, color):
        listofLocations = []
        board = self.board

        for row in range(8):
            for col in range(8):
                if self.isSqrOccupiedby(row, col, color):
                    listofLocations.append((row, col))
        return listofLocations

    def LookforPawn(self, color):
        if color == 'w':
            piece = 'wp'
        else:
            piece = 'bp'
        listofLocations = []
        board = self.board

        for row in range(8):
            for col in range(8):
                if board[row][col] == piece:
                    listofLocations.append((row, col))
        return listofLocations

    def allvalidMoves(self, opp_color):
        color = self.toMove
        Sqrs = self.LookforColorPieces(color)
        moves = []
        for Sqr in Sqrs:
            row, col = Sqr
            attacks = self.validMoves(row, col, opp_color)
            for attack in attacks:
                moves.append([Sqr, attack])
        return moves

    def isCheck(self, opp_color):
        if opp_color == 'b':
            (row, col) = self.WKingPos
        else:
            (row, col) = self.BKingPos
        list = self.isSquareAttackedby(row, col)
        return list

    def isCheckmate(self, opp_color):
        if self.isCheck(opp_color) and self.allvalidMoves(opp_color) == []:
            return True
        return False

    def isStalemate(self, opp_color):
        if not self.isCheck(opp_color) and self.allvalidMoves(opp_color) == []:
            return True
        return False

    def pos2key(self):

        board = self.board
        boardTuple = []
        for row in board:
            boardTuple.append(tuple(row))
        boardTuple = tuple(boardTuple)
        rights = ([self.WCastleK, self.WCastleQ], [self.BCastleK, self.BCastleQ])
        tuplerights = (tuple(rights[0]), tuple(rights[1]))
        # Generate the key, which is a tuple that also takes into account the side to play:
        key = (boardTuple, self.toMove,
               tuplerights)
        return key

    def eval(self):
        if self.isCheckmate('b'):
            return -20000
        if self.isCheckmate('w'):
            return 20000
        board = self.board
        flatboard = [x for row in board for x in row]
        c = Counter(flatboard)
        wQ = c['wQ']
        bQ = c['bQ']
        wR = c['wR']
        bR = c['bR']
        wB = c['wB']
        bB = c['bB']
        wN = c['wN']
        bN = c['bN']
        wp = c['wp']
        bp = c['bp']

        whiteMaterial = 9 * wQ + 5 * wR + 3 * wN + 3 * wB + wp
        blackMaterial = 9 * bQ + 5 * bR + 3 * bN + 3 * bB + bp
        numofmoves = len(self.moveLog)
        gamephase = 'opening'
        if numofmoves > 40 or (whiteMaterial < 14 and blackMaterial < 14):
            gamephase = 'ending'

        wD = self.doubledPawns('w')
        bD = self.doubledPawns('b')
        wS = self.blockedPawns('w')
        bS = self.blockedPawns('b')
        wI = self.isolatedPawns('w')
        bI = self.isolatedPawns('b')

        evaluation1 = 900 * (wQ - bQ) + 500 * (wR - bR) + 330 * (wB - bB) + 320 * (wN - bN) + 100 * (wp - bp) + (
            -30) * (wD - bD + wS - bS + wI - bI)
        evaluation2 = ValuebyPieceSqr(flatboard, gamephase)
        evaluation = evaluation1 + evaluation2
        print(evaluation1, evaluation2)
        return evaluation

    def doubledPawns(self, color):
        listofpawnspos = self.LookforPawn(color)
        doubled = 0
        temp = []
        for pawnpos in listofpawnspos:
            if pawnpos[1] in temp:
                doubled += 1
            else:
                temp.append(pawnpos[1])
        return doubled

    def blockedPawns(self, color):
        listofpawnspos = self.LookforPawn(color)
        blocked = 0
        for pawnpos in listofpawnspos:
            if ((color == 'w' and self.isSqrOccupiedby(pawnpos[0] - 1, pawnpos[1], 'b')) or (
                    color == 'b' and self.isSqrOccupiedby(pawnpos[0] + 1, pawnpos[1], 'w'))):
                blocked += 1
        return blocked

    def isolatedPawns(self, color):  # TO DO
        listofpawnspos = self.LookforPawn(color)
        ylist = [y for (x, y) in listofpawnspos]
        isolated = 0
        for y in ylist:
            if y != 0 and y != 7:
                if y - 1 not in ylist and y + 1 not in ylist:
                    isolated += 1
            elif y == 0 and 1 not in ylist:
                isolated += 1
            elif y == 7 and 6 not in ylist:
                isolated += 1
        return isolated


class Move():
    def __init__(self, startRow, startCol, endRow, endCol, board):
        self.startRow = startRow
        self.startCol = startCol
        self.endRow = endRow
        self.endCol = endCol
        self.pieceMoved = board[self.startRow][self.startCol]
        self.colorMoved = board[self.startRow][self.startCol][0]
        self.typeMoved = board[self.startRow][self.startCol][1]


def ValuebyPieceSqr(flatboard, gamephase):
    score = 0
    for i in range(64):
        if flatboard[i] == 0:
            continue
        piece = flatboard[i][1]
        color = flatboard[i][0]
        sign = 1
        if color == 'b':
            i = (7 - (i // 8)) * 8 + (i % 8)  # TO DO
            sign = -1
        if piece == 'p':
            score += sign * pawn_table[i]
        elif piece == 'N':
            score += sign * knight_table[i]
        elif piece == 'B':
            score += sign * bishop_table[i]
        elif piece == 'R':
            score += sign * rook_table[i]
        elif piece == 'Q':
            score += sign * queen_table[i]
        elif piece == 'K':
            if gamephase == 'opening':
                score += sign * king_table[i]
            else:
                score += sign * king_endgame_table[i]

    return score


pawn_table = [0, 0, 0, 0, 0, 0, 0, 0,
              50, 50, 50, 50, 50, 50, 50, 50,
              10, 10, 20, 30, 30, 20, 10, 10,
              5, 5, 10, 25, 25, 10, 5, 5,
              0, 0, 0, 20, 20, 0, 0, 0,
              5, -5, -10, 0, 0, -10, -5, 5,
              5, 10, 10, -20, -20, 10, 10, 5,
              0, 0, 0, 0, 0, 0, 0, 0]

knight_table = [-50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -90, -30, -30, -30, -30, -90, -50]

bishop_table = [-20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -90, -10, -10, -90, -10, -20]

rook_table = [0, 0, 0, 0, 0, 0, 0, 0,
              5, 10, 10, 10, 10, 10, 10, 5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              0, 0, 0, 5, 5, 0, 0, 0]

queen_table = [-20, -10, -10, -5, -5, -10, -10, -20,
               -10, 0, 0, 0, 0, 0, 0, -10,
               -10, 0, 5, 5, 5, 5, 0, -10,
               -5, 0, 5, 5, 5, 5, 0, -5,
               0, 0, 5, 5, 5, 5, 0, -5,
               -10, 5, 5, 5, 5, 5, 0, -10,
               -10, 0, 5, 0, 0, 0, 0, -10,
               -20, -10, -10, 70, -5, -10, -10, -20]

king_table = [-30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -20, -30, -30, -40, -40, -30, -30, -20,
              -10, -20, -20, -20, -20, -20, -20, -10,
              20, 20, 0, 0, 0, 0, 20, 20,
              20, 30, 10, 0, 0, 10, 30, 20]

king_endgame_table = [-50, -40, -30, -20, -20, -30, -40, -50,
                      -30, -20, -10, 0, 0, -10, -20, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -30, 0, 0, 0, 0, -30, -30,
                      -50, -30, -30, -30, -30, -30, -30, -50]


if __name__ == "__main__":  # main
    main()
