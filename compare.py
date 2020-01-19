#! /usr/bin/env python3

import requests
import chess.pgn
from collections import defaultdict

#API request https://lichess.org/api/games/user/{USER}?max=100&rated=true&ongoing=false&perfType=blitz,rapid,classical

depth = 20
desiredgames = 100


def defineReps(pgnfilepath):
    
    pgn = open(pgnfilepath)
    players = defaultdict(int)

    while True:
        headers = chess.pgn.read_headers(pgn)
        if not headers:
            break
        players[headers.get('White')] += 1
        players[headers.get('Black')] += 1
    player = max(players.items(), key=lambda a: a[1])[0]

    def getPlayerColour(game):
        return 0 if game.headers['White'] == player else 1

    player_moves = defaultdict(int)
    pgn = open(pgnfilepath)

    gamenum = 0
    while True:
        game = chess.pgn.read_game(pgn)
        if not game or gamenum >= desiredgames:
            break
        gamenum += 1
        board = game.board()
        player_colour = getPlayerColour(game)
        for n, move in enumerate(game.mainline_moves()):
            storedfen = board.epd()
            board.push(move)
            if (n + player_colour) % 2 != 0: #skip opponents' moves
                continue
            player_moves[(storedfen, move.uci())] += 1
            if n > depth:
                break
    return player_moves

library = [
'pgns/lichess_somethingpretentious_2020-01-17_100games.pgn',
'pgns/Gholami_Orimi_A-TA.pgn',
'pgns/ChessGrunt2002-bullet.pgn',
'pgns/lichess_TheFinnisher_2020-01-17.pgn',
'pgns/lichess_MMichael_2020-01-17.pgn']

rep1 = defineReps(library[1])
rep2 = defineReps(library[2])

def compareReps(rep1, rep2):
    score = 0
    rarities = []
    for move in rep1.keys():
        p2score = rep2.get(move)
        if p2score:
            p1score = rep1[move]
            score += min(p1score, p2score) * min(p1score, p2score)
    potential = sum([x*x for x in rep1.values()])
    return(score/potential) 

print((compareReps(rep1, rep2) + compareReps(rep2, rep1))/2)
