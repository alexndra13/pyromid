"""Skeleton for Pyramid game

The code below is still the same as for Rock-Paper-Scissors.
Modify to implement the Pyramid game.
"""

from pyro_db_sqlite import Game


class Pyramid(Game):
    # valid move logic goes here
    def valid_moves(self, username):
        """Return list of pairs with valid moves for this player and how to display them.

        :param username: The moves valid for this user
        :return: List of pairs

        self.players contains a list of dictionaries - one dictionary per player.
        Each dictionary has the player variables for the players in the game.

        Example:
        [
        {'name': 'a', 'score': 0, 'playing': 1, 'paddles': '13456'},
        {'name': 'b', 'score': 1, 'playing': 1, 'paddles': '12345'},
        {'name': 'c', 'score': 0, 'playing': 1, 'paddles': '12356'}
        ]
        """

        # First, get the index in the list for the dictionary that coresponds to username
        # Example: If username = 'b', index = 1
        index = self.player_index(username)

        # Now, retrieve the paddles for username
        # Example: '12345'
        paddles = self.players[index]['paddles']

        # Explode the paddles string into a list of individual characters
        # Example: [1, 2, 3, 4, 5]
        mval = list(paddles)

        return mval

    # a player just played a paddle
    def add_player_move(self, username, move):
        """Add a new move by a player to the game.

        :param username: Username of player who moves
        :param move: The value of the paddle that was played
        """
        # Discard move if Game not in play (i.e. state != 1)
        if self.state != 1:
            return

        # Find the index (position) of this player in the list of players in the game.
        # In the case of RPS games this value will be 0 or 1 since RPS always has 2 players.
        index = self.player_index(username)

        # Update the paddles for this player to remove the paddle just played.
        old_paddles = self.players[index]['paddles']
        new_paddles = old_paddles.replace(move, '')
        # Now update the player table
        self.update_player_paddles(index, new_paddles)


        # If there are no game rounds yet, or the last one is complete
        if not self.turns or not [None for m in self.turns[-1] if m is None]:  # No turns or last complete
            new_turn = [None] * len(self.players)
            new_turn[index] = move
            self.turns.append(new_turn)
            self.save_game_state()

        # If opponent(s) moved in last round but user has not
        elif self.turns[-1][index] is None:
            last_turn = self.turns[-1]
            last_turn[index] = move
            # Check if turn is complete and if so calculate scores
            if not [None for m in last_turn if m is None]:
                # First, find the max value in the list
                maxpaddle = max(last_turn)

                # Next, find the players that played the value of maxpaddle
                # The index of the winning players will be added to the winners list
                start_at = -1
                winners = []

                while True:
                    try:
                        player_index = last_turn.index(maxpaddle, start_at+1)
                    except ValueError:
                        break
                    else:
                        winners.append(player_index)
                        start_at = player_index

                # Only one winner?  If so, they get 2 points
                if len(winners) == 1:
                    self.players[winners[0]]['score'] +=2
                    self.save_score_for_player(winners[0])

                # If more than one winner, each gets 1 point
                i = 0
                if len(winners) > 1:
                    while i < len(winners):
                        self.players[winners[i]]['score'] +=1
                        self.save_score_for_player(winners[i])
                        i += 1

                # Check to see if the number of turns is greater than the goal (rounds in the game)
                if len(self.turns) == self.goal:
                    self.set_game_over()

            self.save_game_state()

    def decorated_moves(self, username):
        """Return a list of moves with formatting information.
        :param username: Player's username
        :return: Formatted list of moves
        """

        if not self.turns:
            return []

        last_turn = self.turns[-1]
        if [None for m in last_turn if m is None]:  # Everybody has not yet moved in last turn, it is incomplete
            incomplete_last_turn = last_turn
            complete_turns = self.turns[:-1]
        else:
            incomplete_last_turn = None
            complete_turns = self.turns

        #translate = {'r': 'Rock', 'p': 'Paper', 's': 'Scissors'}
        decorated_turns = []

        for turn in complete_turns:
            # decorated_turns is a list of tuples.  It looks like this:
            # [(player1_score, highlight?), (player2_score, highlight?), ...]
            # player_score is what is printed in the box
            # if highlight is true, then turn the box green
            deco_list = []
            # Find the value of the max paddle this turn
            maxpaddle = max(turn)

            for player_paddle_value in turn:
                if player_paddle_value == maxpaddle:
                    highlight = True
                else:
                    highlight = False
                deco_list.append((player_paddle_value, highlight))

            decorated_turns.append(deco_list)

        '''
        for turn in complete_turns:
            if turn in (['p', 'r'], ['s', 'p'], ['r', 's']):
                decorated_turns.append([(translate[turn[0]], True), (translate[turn[1]], False)])
            elif turn in (['r', 'p'], ['p', 's'], ['s', 'r']):
                decorated_turns.append([(translate[turn[0]], False), (translate[turn[1]], True)])
            else:
                decorated_turns.append([(translate[turn[0]], False), (translate[turn[1]], False)])
        '''

        if incomplete_last_turn:
            index = self.player_index(username)
            decorated_last_turn = []
            for i, m in enumerate(incomplete_last_turn):
                if m is None:
                    decorated_last_turn.append(('', False))
                elif i == index or incomplete_last_turn[index]:
                    decorated_last_turn.append((m, False))
                else:
                    decorated_last_turn.append(('?', False))
            decorated_turns.append(decorated_last_turn)

        return decorated_turns


    def is_players_turn(self, username):
        """Check if it is player's turn.

        :param username: Player's username
        :return: boolean
        """
        if self.state != 1:  # Game not in play
            return False
        if not self.turns:  # Nobody has made any moves yet
            return True

        latest_turn = self.turns[-1]
        if not latest_turn[self.player_index(username)]:  # User not yet moved in latest turn
            return True
        if not [None for m in latest_turn if m is None]:  # Latest turn is complete, start new turn
            return True
