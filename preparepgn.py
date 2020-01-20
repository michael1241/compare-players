#! /usr/bin/env python3

import chess.pgn

maxgames = 100

players = {}

playernum = 50

threshold = 2000

def writeGame(game, playername, players):
    if players.get(playername) and players[playername]['count'] == maxgames:
        return
    if playername not in players:
        players[playername] = {'handle': open(f'pgnsplit/{playername}.pgn', 'w'), 'count': 0}
    print(game, file=players[playername]['handle'], end="\n\n")
    players[playername]['count'] += 1



pgn = open("pgns/lichess_db_standard_rated_2014-09.pgn")

need_players = 1
while True:
    game = chess.pgn.read_game(pgn)
    if not game:
        for f in players.values():
            f.close()
        print('Read all games, exiting.')
        break
    white = game.headers['White']
    black = game.headers['Black']
    try:
        rating = (int(game.headers['BlackElo']) + int(game.headers['WhiteElo']))//2
    except ValueError:
        continue
    if rating <= threshold:
        continue
    if need_players:
        writeGame(game, white, players)
        writeGame(game, black, players)
        if len(players) >= playernum:
            need_players = 0
    if not need_players and white in players:
        writeGame(game, white, players)
    if not need_players and black in players:
        writeGame(game, black, players)

