import requests
import random
import sys
import time

### Public IP Server
### Testing Server
host_name = 'http://ec2-3-144-219-136.us-east-2.compute.amazonaws.com:8000'

class OthelloPlayer():

    def __init__(self, username):
        ### Player username
        self.username = username
        ### Player symbol in a match
        self.current_symbol = 0
        self.static_weight_board = [
            [100, -30, 6, 2, 2, 6, -30, 100],
            [-30, -50, 0, 0, 0, 0, -50, -30],
            [6, 0, 0, 0, 0, 0, 0, 6],
            [2, 0, 0, 3, 3, 0, 0, 2],
            [2, 0, 0, 3, 3, 0, 0, 2],
            [6, 0, 0, 0, 0, 0, 0, 6],
            [-30, -50, 0, 0, 0, 0, -50, -30],
            [100, -30, 6, 2, 2, 6, -30, 100]
        ]


    def connect(self, session_name) -> bool:
        """
        :param session_name:
        :return:
        """
        new_player = requests.post(host_name + '/player/new_player?session_name=' + session_name + '&player_name=' +self.username)
        new_player = new_player.json()
        self.session_name = session_name
        print(new_player['message'])
        return new_player['status'] == 200

    def print_board(self, board):
        symbols = {1: 'W', -1: 'B', 0: '.'}
        print('  0 1 2 3 4 5 6 7')
        cont = 0
        for row in board:
            pr = ' '.join([symbols[cell] for cell in row])
            print(f'{cont} {pr}')
            cont += 1
        print()

    def play(self) -> bool:
        """
        :return:
        """
        session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
        session_info = session_info.json()

        while session_info['session_status'] == 'active':
            try:
                if (session_info['round_status'] == 'ready'):

                    match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                    match_info = match_info.json()

                    while match_info['match_status'] == 'bench':
                        print('You are benched this round. Take a rest while you wait.')
                        time.sleep(15)
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()

                    if (match_info['match_status'] == 'active'):
                        self.current_symbol = match_info['symbol']
                        if self.current_symbol == 1:
                            print('Lets play! You are the white pieces.')
                        if self.current_symbol == -1:
                            print('Lets play! You are the black pieces.')


                    while (match_info['match_status'] == 'active'):
                        turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                        turn_info = turn_info.json()
                        while not turn_info['game_over']:
                            if turn_info['turn']:
                                print('SCORE ', turn_info['score'])
                                row, col = self.AI_MOVE(turn_info['board'])
                                move = requests.post(
                                    host_name + '/player/move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +
                                    match_info['match'] + '&row=' + str(row) + '&col=' + str(col))
                                move = move.json()
                                print(move['message'])
                            time.sleep(2)
                            turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                            turn_info = turn_info.json()

                        print('Game Over. Winner : ' + turn_info['winner'])
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()


                else:
                    print('Waiting for match lottery...')
                    time.sleep(5)

            except requests.exceptions.ConnectionError:
                continue

            session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
            session_info = session_info.json()



    ### Solo modiquen esta función
    def AI_MOVE(self, board):
        
        self.print_board(board)
        
        valid_moves = get_valid_moves(board, self.current_symbol)
        my_color = self.current_symbol # 1 is white, -1 is black
        
        print(f"==>> valid_moves: \n{valid_moves}")

        if valid_moves:
            # Find the move with the highest static weight
            best_move = max(valid_moves, key=lambda move: self.static_weight_board[move[0]][move[1]])
            return best_move
        else:
            return None


def get_valid_moves(board, player):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(board, player, row, col):
                valid_moves.append((row, col))

    return valid_moves

def is_valid_move(board, player, row, col):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    if board[row][col] != 0:
        return False

    opponent = -player

    for direction in directions:
        dr, dc = direction
        r, c = row + dr, col + dc
        found_opponent = False

        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            r += dr
            c += dc
            found_opponent = True

        if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            return True

    return False


def any_direction_valid(board, row, col, symbol):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    return any(check_direction(board, row, col, dx, dy, symbol) for dx, dy in directions)

def check_direction(board, row, col, dx, dy, symbol):
    x, y = row + dx, col + dy
    if not (0 <= x < 8 and 0 <= y < 8) or board[x][y] != -symbol:
        return False
    x += dx
    y += dy
    while 0 <= x < 8 and 0 <= y < 8:
        if board[x][y] == symbol:
            return True
        if board[x][y] == 0:
            return False
        x += dx
        y += dy
    return False


if __name__ == '__main__':
    script_name = sys.argv[0]
    # The rest of the arguments start from sys.argv[1]
    ### The first argument is the session id you want to join
    session_id = sys.argv[1]
    ### The second argument is the username you want to have
    player_id = sys.argv[2]

    print('Bienvenido ' + player_id + '!')
    othello_player = OthelloPlayer(player_id)
    if othello_player.connect(session_id):
        othello_player.play()
    print('Hasta pronto!')