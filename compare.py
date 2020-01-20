#! /usr/bin/env python3

import requests
import chess.pgn
from collections import defaultdict
import time
import pickle
import os
import sys
from math import sqrt

def main(file1, file2, depth, desiredgames):

    if os.path.exists('mastersdbcache'):
        with open('mastersdbcache', 'rb') as db:
            FENdict = pickle.load(db)
    else:
        FENdict = {}

    def FENrarity(fen, moves):
        cachedfen = FENdict.get(fen)
        if cachedfen:
            r = cachedfen
        else:
            while True:
                payload = {'fen': fen, 'topGames': 0, 'moves': 30}
                r = requests.get(f'https://explorer.lichess.ovh/master', params=payload)
                if r.status_code == 200:
                    time.sleep(0.6)
                    r = r.json()
                    break
                if r.status_code == 429:
                    print("waiting 5 seconds")
                    time.sleep(5)
                    continue
        FENdict[fen] = r

        freqs = {}
        dbmoves = {m['uci']: m['white']+m['draws']+m['black'] for m in r['moves']}
        for move in moves:
            if move in dbmoves:
                mov_occur = dbmoves[move]
                freqs[move] = 1 / sqrt(mov_occur) #bigger is rarer
            else:
                freqs[move] = 1 #rarest possible
        return freqs

    #print(checkFEN('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR', 'e7e5'))

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

        player_moves = {}
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
                ucimove = move.uci()
                if storedfen in player_moves:
                    if ucimove in player_moves[storedfen]:
                        player_moves[storedfen][ucimove] += 1
                    else:
                        player_moves[storedfen][ucimove] = 1
                else:
                    player_moves[storedfen] = {ucimove: 1}
                if n > depth:
                    break
        return player_moves

    def compareReps(rep1, rep2):
        score = 0
        #rarities = []
        rep2lookup = {}
        for position2 in rep2:
            for move2 in rep2[position2]:
                rep2lookup[(position2, move2)] = rep2[position2][move2]
        for position, moves in rep1.items():
            rarity = FENrarity(position, moves)
            #rarities.extend(freqs.values())
            for move in moves:
                p2score = rep2lookup.get((position,move))
                if p2score:
                    p1score = rep1[position][move]
                    score += min(p1score, p2score) * min(p1score, p2score) * rarity[move]
        #potential = sum([x*x*y for x, y in zip(rep1.values(), rarities)])
        return(score) 

    with open('mastersdbcache', 'wb') as db:
        pickle.dump(FENdict, db)

    rep1 = defineReps(file1)
    rep2 = defineReps(file2)
    return (compareReps(rep1, rep2) + compareReps(rep2, rep1))/2


