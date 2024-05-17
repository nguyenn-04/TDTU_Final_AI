from board import Board
from problem import Problem
from search import SearchStrategy
import os


class Game:
    def __init__(self, ai_starts=False):
        self.board = Board()
        self.problem = Problem(self.board)
        self.strategy = SearchStrategy()
        self.ai_starts = ai_starts

        if self.ai_starts:
            self.problem.current_player = self.problem.ai_player

    def play_game(self):
        while not self.problem.is_goal():
            os.system('cls' if os.name == 'nt' else 'clear')
            self.board.draw_board()
            if self.problem.current_player == self.problem.human_player:
                x, y = map(int, input("Enter your move: ").split())
                if self.board.make_move(x, y, self.problem.human_player):
                    self.problem.switch_player()
                else:
                    print("Invalid move")
            else:
                print("AI Turn")
                move = self.strategy.alpha_beta_search(self.problem)
                self.board.make_move(move[0], move[1], self.problem.ai_player)
                self.problem.switch_player()
            
        os.system('cls' if os.name == 'nt' else 'clear')
        self.board.draw_board()
        if self.problem.check_winner(self.problem.human_player):
            print("You win!")
        elif self.problem.check_winner(self.problem.ai_player):
            print("You lose!")
        else:
            print("It's a draw!")


if __name__ == "__main__":
    ai_starts = (
        input("Do you want AI to start first? (yes/no): ").strip().lower() == "yes"
    )
    game = Game(ai_starts)
    game.play_game()