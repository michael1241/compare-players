#! /usr/bin/env python3

import requests
import chess.pgn
import math
import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
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
'pgns/vera90-bullet-ta.pgn',
'pgns/Gholami_Orimi_A-TA.pgn',
'pgns/Fuger-blitz.pgn',
'pgns/ChessGrunt2002-bullet.pgn',
'pgns/TheFinnisher.pgn',
'pgns/MMichael.pgn']

#print(defineRep(library[1]))

def compareReps(rep1, rep2):
    def standardise(moves1, moves2):
        allmoves = set(moves1.keys()) | set(moves2.keys())
        moves1 = [moves1.get(move, 0) for move in allmoves]
        moves2 = [moves2.get(move, 0) for move in allmoves]
        return moves1, moves2

    allfens = set(rep1.keys()) | set(rep2.keys())

    score = 0
    for fen in allfens:
        moves1, moves2 = standardise(rep1.get(fen, {}), rep2.get(fen, {}))
        cos = 1 - spatial.distance.cosine(moves1, moves2)
        if not np.isnan(cos):
            score += cos
    return math.log(score)

reps = {}
for player in library:
    reps[player] = defineRep(player)
    print(f'Done {player}')

df = pd.DataFrame(columns=['p1', 'p2', 'score'])

for player1 in reps:
    for player2 in reps:
        df_add = pd.DataFrame({'p1': [player1], 'p2': [player2], 'score': [compareReps(reps[player1], reps[player2])]})
        df = df.append(df_add, ignore_index=True)

df = pd.crosstab(df.p1, df.p2, values=df.score, aggfunc=sum)

sn.heatmap(df, annot=True)
plt.show()
