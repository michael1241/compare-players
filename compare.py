#! /usr/bin/env python3

import requests
import chess.pgn
from collections import defaultdict
import time
import pickle
import os

depth = 20
desiredgames = 20

if os.path.exists('mastersdbcache'):
    with open('mastersdbcache', 'rb') as db:
        FENdict = pickle.load(db)
else:
    FENdict = {}

def FENrarity(fen, move):
    cachedfen = FENdict.get(fen)
    if cachedfen:
        r = cachedfen
    else:
        while True:
            r = requests.get(f'https://explorer.lichess.ovh/master?fen={fen}&topGames=0&moves=30')
            if r.status_code == 200:
                time.sleep(0.25)
                r = r.json()
                break
            if r.status_code == 429:
                print("waiting 5 seconds")
                time.sleep(5)
                continue
            print(r)
    FENdict[fen] = r
    pos_occur = r['white'] + r['draws'] + r['black']
    for dbmove in r['moves']:
        if dbmove['uci'] == move:
            mov_occur = dbmove['white'] + dbmove['draws'] + dbmove['black']
            rarity =  pos_occur / mov_occur #bigger is rarer
            return(min(rarity, 1000))
    return 500 #guess at rare move

#print(checkFEN('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR', 'e7e5'))

def defineReps(pgnfilepath):
    
    pgn = open(pgnfilepath)
    players = defaultdict(int)
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        players[game.headers['White']] += 1
        players[game.headers['Black']] += 1
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
        for n, move in enumerate(game.main_line()):
            storedfen = " ".join(board.fen().split()[:2])
            board.push(move)
            if (n + player_colour) % 2 != 0: #skip opponents' moves
                continue
            player_moves[(storedfen, move.uci())] += 1
            if n > depth:
                break
    return player_moves

rep1 = defineReps('pgns/lichess_somethingpretentious_2020-01-16.pgn')
#rep1 = defineReps('pgns/lichess_bufferunderrun_2020-01-15.pgn')
#rep2 = defineReps('pgns/lichess_bufferunderrun_2020-01-15.pgn')
#rep2 = defineReps('pgns/lichess_somethingpretentious_2020-01-15.pgn')
rep2 = defineReps('pgns/lichess_somethingpretentious_2020-01-15.pgn')

def compareReps(rep1, rep2):
    score = 0
    rarities = []
    for move in rep1.keys():
        rarity = FENrarity(move[0], move[1])
        rarities.append(rarity)
        p2score = rep2.get(move)
        if p2score:
            p1score = rep1[move]
            score += min(p1score, p2score) * min(p1score, p2score) * rarity
    potential = sum([x*x*y for x, y in zip(rep1.values(), rarities)])
    return((1000*score)/potential) 

print(compareReps(rep1, rep2))

with open('mastersdbcache', 'wb') as db:
    pickle.dump(FENdict, db)
