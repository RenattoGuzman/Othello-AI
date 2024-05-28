
import csv
import math
import random
import time

import pandas as pd

class OthelloPlayer():
    def __init__(self, username, symbol):
        self.username = username
        self.current_symbol = symbol

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

        self.move_count = 0
        
    def MY_AI_MOVE(self, board):
        valid_moves = get_valid_moves(board, self.current_symbol)
        
        if not valid_moves:
            return None

        def minimax(board, depth, alpha, beta, maximizing_player):
            if depth == 0 or not get_valid_moves(board, self.current_symbol):
                return self.evaluate_board(board)

            if maximizing_player:
                max_eval = -math.inf
                for move in get_valid_moves(board, self.current_symbol):
                    new_board = self.make_hypothetical_move(board, move, self.current_symbol)
                    eval = minimax(new_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = math.inf
                opponent_symbol = -self.current_symbol
                for move in get_valid_moves(board, opponent_symbol):
                    new_board = self.make_hypothetical_move(board, move, opponent_symbol)
                    eval = minimax(new_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval

        best_move = None
        best_value = -math.inf
        for move in valid_moves:
            new_board = self.make_hypothetical_move(board, move, self.current_symbol)
            move_value = minimax(new_board, 4, -math.inf, math.inf, False)  # Depth of 3 for example
            if move_value > best_value:
                best_value = move_value
                best_move = move
                
        
        return best_move

    def make_hypothetical_move(self, board, move, symbol):
        new_board = [row[:] for row in board]
        self.make_move(new_board, move[0], move[1], symbol)
        return new_board

    def make_move(self, board, row, col, symbol):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        board[row][col] = symbol
        for dx, dy in directions:
            if self.check_direction(board, row, col, dx, dy, symbol):
                x, y = row + dx, col + dy
                while board[x][y] == -symbol:
                    board[x][y] = symbol
                    x += dx
                    y += dy

    def check_direction(self, board, row, col, dx, dy, symbol):
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

    def evaluate_board(self, board):
        return sum(self.static_weight_board[row][col] * board[row][col]
                   for row in range(8) for col in range(8))



    def AI_MOVE(self, board): 
       
        valid_moves = get_valid_moves(board, self.current_symbol)
        print(f"==>> valid_moves: \n{valid_moves}")
        if valid_moves:
            return random.choice(valid_moves)
        else:
            return None
        

class OthelloGame():
    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = -1
        self.current_player = 1
        self.players = []
        self.winner = 0
        self.passing_moves = 0

    def add_player(self, player):
        self.players.append(player)

    def print_board(self):
        symbols = {1: 'W', -1: 'B', 0: '.'}
        print('  0 1 2 3 4 5 6 7')
        cont = 0
        for row in self.board:
            pr = ' '.join([symbols[cell] for cell in row])
            print(f'{cont} {pr}')
            cont += 1
        print()

    def play(self):
        while True:
            #self.print_board()
            player = self.players[self.current_player == -1]
            print(f"{player.username}'s turn ({'White' if player.current_symbol == 1 else 'Black'}):")

            valid_moves = get_valid_moves(self.board, player.current_symbol)
            if not valid_moves:
                print("No valid moves available. Passing turn.")
                self.passing_moves += 1
                self.current_player *= -1
                continue

            if player.username.startswith("AI_"):
                move = player.AI_MOVE(self.board)
            elif player.username.startswith("MY_AI_"):
                move = player.MY_AI_MOVE(self.board)
            else:
                while True:
                    row, col = map(int, input('Enter row and column (0-7): ').split())
                    if (row, col) in valid_moves:
                        move = (row, col)
                        break
                    else:
                        print("Invalid move, try again.")

            row, col = move
            if move:
                self.make_move(row, col, player.current_symbol)
                self.current_player *= -1

            if all(cell != 0 for row in self.board for cell in row):
                break

        #self.print_board()
        self.print_winner()
        print("Game over!")

    def make_move(self, row, col, symbol):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.board[row][col] = symbol
        for dx, dy in directions:
            if self.check_direction(row, col, dx, dy, symbol):
                x, y = row + dx, col + dy
                while self.board[x][y] == -symbol:
                    self.board[x][y] = symbol
                    x += dx
                    y += dy

    def check_direction(self, row, col, dx, dy, symbol):
        x, y = row + dx, col + dy
        if not (0 <= x < 8 and 0 <= y < 8) or self.board[x][y] != -symbol:
            return False
        x += dx
        y += dy
        while 0 <= x < 8 and 0 <= y < 8:
            if self.board[x][y] == symbol:
                return True
            if self.board[x][y] == 0:
                return False
            x += dx
            y += dy
        return False

    def print_winner(self):
        white_count = sum(cell == 1 for row in self.board for cell in row)
        black_count = sum(cell == -1 for row in self.board for cell in row)
        print(f"Final Score - White: {white_count}, Black: {black_count}")
        if white_count > black_count:
            print("White wins!")
            self.winner = 1
        elif black_count > white_count:
            print("Black wins!")
            self.winner = -1
        else:
            print("It's a tie!")
            self.winner = 0

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

def get_valid_moves(board, player):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(board, player, row, col):
                valid_moves.append((row, col))

    return valid_moves


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

# if __name__ == '__main__':
    
#     colors = [-1,1]
#     color1 = random.choice(colors)
#     color2 = color1 * -1
    
#     player1 = OthelloPlayer("MY_AI_Player1", color1)
#     player2 = OthelloPlayer("AI_Player2", color2)

#     game = OthelloGame()
#     game.add_player(player1)
#     game.add_player(player2)


#     game.play()

#     mycolor = "Black" if color1 == -1 else "White"

#     print(mycolor," IS MY AI IS COLOR")


if __name__ == '__main__':
    num_games = 15
    results = []

    for _ in range(num_games):
        colors = [-1, 1]
        color1 = random.choice(colors)
        color2 = color1 * -1

        player1 = OthelloPlayer("MY_AI_Player1", color1)
        player2 = OthelloPlayer("AI_Player2", color2)

        game = OthelloGame()
        game.add_player(player1)
        game.add_player(player2)

        game.play()
        
        if game.passing_moves > 5:
            pass
        
        winner = game.winner
        print(f"==>> winner: \n{winner}")
        win = True if winner == color1 else False
        
        results.append({'win':win, 'color1': color1, 'win_color': winner, 'color2': color2})

    # Create a DataFrame from the results list
    df = pd.DataFrame(results)
    print(f"==>> df: \n{df}")

    # Save the DataFrame to a CSV file
    df.to_csv('minimax.csv', index=False)
