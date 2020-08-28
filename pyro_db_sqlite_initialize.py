# Erases and creates the game database with all the necessary tables and fields
#
# The table are:
#    user: name, password
#
#    game: players, goal, state, ts, turns
#       One line for each game.
#       players = max number of players in the game
#       goal = score (or number of rounds)
#       state = 0=adding players, 1=game in progress, 2=game over
#       ts = timestamp of last player added to game
#       turns = text representation of the game history (who played what each turn)
#
#    player: game_id, user_name, score, playing, paddles
#       One line for each player in each game.
#       game_id = unique game number for all players in game.  Same as row_id for the game table.
#       user_name = user name
#       score = player's score
#       playing = 0=left game, 1=in game
#       paddles = text representation of which paddles are left to play (e.g. "12_4_67")
#
import sqlite3

connection = sqlite3.connect('pyro_game.db')

connection.execute('DROP TABLE IF EXISTS user')
connection.execute('DROP TABLE IF EXISTS game')
connection.execute('DROP TABLE IF EXISTS player')

connection.execute('''
CREATE TABLE user (
 name VARCHAR(64) NOT NULL PRIMARY KEY,
 password VARCHAR(64) NOT NULL
)
''')

connection.execute('''
CREATE TABLE game (
 players INTEGER,
 goal INTEGER,
 state INTEGER DEFAULT 0,
 ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 turns VARCHAR(4096) DEFAULT '[]'
)
''')

connection.execute('''
CREATE TABLE player (
 game_id INTEGER,
 user_name VARCHAR(64),
 score INTEGER DEFAULT 0,
 playing INTEGER DEFAULT 1,
 paddles VARCHAR(9),
 UNIQUE (game_id, user_name)
)
''')

connection.commit()
