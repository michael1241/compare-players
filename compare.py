#! /usr/bin/env python3

import requests
import chess.pgn
import numpy as np
import pandas as pd
from collections import defaultdict
from scipy import spatial

depth = 10
desiredgames = 100


def defineRep(pgnfilepath):
    
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

    pos_dict = {}
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
            if pos_dict.get(storedfen):
                if pos_dict[storedfen].get(move.uci()):
                    pos_dict[storedfen][move.uci()] += 1
                else:
                    pos_dict[storedfen][move.uci()] = 1
            else:
                pos_dict[storedfen] = {move.uci(): 1}
            if n > depth:
                break
    return pos_dict

library = [
'pgns/lichess_somethingpretentious_2020-01-17_100games.pgn',
'pgns/Gholami_Orimi_A-TA.pgn',
'pgns/ChessGrunt2002-bullet.pgn',
'pgns/lichess_TheFinnisher_2020-01-17.pgn',
'pgns/lichess_MMichael_2020-01-17.pgn']

#print(defineRep(library[1]))

def compareReps(rep1, rep2):
    def standardise(moves1, moves2):
        m1 = list(moves1.keys())
        m2 = list(moves2.keys())
        m1.extend(m2)
        allmoves = list(set(m1))
        moves1 = [moves1.get(move, 0) for move in allmoves]
        moves2 = [moves2.get(move, 0) for move in allmoves]
        return moves1, moves2

    fen1 = list(rep1.keys())
    fen2 = list(rep2.keys())
    fen1.extend(fen2)
    allfens = list(set(fen1))

    score = 0
    for fen in allfens:
        moves1, moves2 = standardise(rep1.get(fen, {}), rep2.get(fen, {}))
        cos = 1 - spatial.distance.cosine(moves1, moves2)
        if not np.isnan(cos):
            score += cos
    return score

reps = {}
for player in library:
    reps[player] = defineRep(player)
    print(f'Done {player}')

for player1 in reps:
    for player2 in reps:
        print(player1, player2, compareReps(reps[player1], reps[player2]))
