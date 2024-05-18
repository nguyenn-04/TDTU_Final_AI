import numpy as np
import regex as re
from board import Board


class Problem:
    """
    Quản lý trạng thái của game và các hàm liên quan
    """

    def __init__(self, size=8, human_player="X", opponent_factor=0.90):
        """
        Khởi tạo trạng thái game
        """
        self.board = Board(size)
        self.human_player = human_player
        self.ai_player = "O" if human_player == "X" else "X"
        self.opponent_factor = opponent_factor
        self.current_player = self.human_player

    def switch_player(self):
        """
        Đổi lượt chơi
        """
        self.current_player = (
            self.ai_player
            if self.current_player == self.human_player
            else self.human_player
        )

    def check_winner(self, player):
        """
        Kiểm tra chiến thắng của player
        """
        lines = self.board.get_all_lines()
        return np.any(["".join(line).find(player * 4) != -1 for line in lines])

    def is_game_over(self):
        """
        Kiểm tra game kết thúc (Goal state)
        """
        return (
            self.check_winner(self.human_player)
            or self.check_winner(self.ai_player)
            or self.board.is_full()
        )

    def get_valid_moves(self):
        """
        Lấy tất cả các nước đi hợp lệ
        """
        return list(zip(*np.where(self.board.board == self.board.empty)))

    def evaluate(self):
        """
        Hàm đánh giá trạng thái game
        """
        return self.calculate_heuristic(self.board.board, self.ai_player)

    def count_patterns_in_lines(self, lines, pattern):
        """
        Đếm số lần xuất hiện của pattern trong lines
        """
        compiled_pattern = re.compile(pattern)
        return sum(
            len(compiled_pattern.findall(line, overlapped=True)) for line in lines
        )

    def generate_lines(self, matrix, player):
        """
        Tạo ra tất cả các dòng, cột, đường chéo trên bàn cờ
        """
        lines = []
        trans = {player: "x", self.board.empty: "e"}

        def translate(arr):
            return "".join([trans.get(c, "b") for c in arr])

        lines = [translate(row) for row in matrix]
        lines += [translate(col) for col in matrix.T]

        for i in range(-matrix.shape[0] + 1, matrix.shape[1]):
            lines += [
                translate(np.diagonal(matrix, i)),
                translate(np.diagonal(np.fliplr(matrix), i)),
            ]

        return lines

    def calculate_heuristic(self, board, player):
        """
        Tính giá trị heuristic của trạng thái game
        """

        """
        UTILITY: giá trị đánh giá cho các trường hợp trên bàn cờ
        """
        UTILITY = {
            "FourInRow": [20000000, ["xxxx"]],
            "KillerMove": [1000000, ["exxx", "xxxe"]],
            "ThreeInRow_OpenBothEnds": [400000, ["exxxe"]],
            "ThreeInRow_OneOpenEnd": [50000, ["bxxxe", "exxxb"]],
            "TwoInRow_OpenBothEnds": [30000, ["exxe", "eexx"]],
            "TwoInRow_OneOpenEnd": [15000, ["bxxe", "eexb"]],
            "PotentialThreeInRow_OpenBothEnds": [7000, ["exexxe", "exxexe"]],
            "PotentialThreeInRow_OneOpenEnd": [
                3000,
                ["bxexxe", "bxxexe", "exxexb", "exexxb"],
            ],
            "SinglePiece_OpenBothEnds": [500, ["exee", "eeex"]],
            "SinglePiece_OneOpenEnd": [400, ["bxe", "eexb"]],
            "SinglePiece_OneOpenOneBlocked": [200, ["bxe"]],
            "PotentialTwoInRow_OpenBothEnds": [100, ["exxe"]],
            "PotentialSinglePiece_OneOpenEnd": [40, ["bxeee", "eeexb"]],
        }

        def get_sequence_score(lines):
            """
            Tính giá trị heuristic dựa trên các pattern
            """
            sequence_score = 0
            for _, (value, patterns) in UTILITY.items():
                for pattern in patterns:
                    sequence_score += value * self.count_patterns_in_lines(
                        lines, pattern
                    )
            return sequence_score

        def get_position_score(board, player):
            """
            Tính giá trị heuristic dựa trên vị trí của các quân cờ
            """
            player_board = np.where(board == player, 1, 0)
            return np.sum(player_board * self.board.HEURISTIC)

        lines = self.generate_lines(board, player)
        player_score = get_sequence_score(lines) + get_position_score(board, player)

        opponent = "O" if player == "X" else "X"
        opponent_lines = self.generate_lines(board, opponent)
        opponent_score = get_sequence_score(opponent_lines) + get_position_score(
            board, opponent
        )

        return player_score - self.opponent_factor * opponent_score

    def evaluate_move(self, move):
        """
        Đánh giá nước đi
        """
        x, y = move
        temp_board = self.board.board.copy()
        temp_board[x][y] = self.ai_player
        score = self.calculate_heuristic(temp_board, self.ai_player)
        return score

    def sort_moves(self):
        """
        Sắp xếp các nước đi tiềm năng dựa trên giá trị heuristic
        """
        moves = []
        for x in range(self.board.size):
            for y in range(self.board.size):
                if self.board.is_valid_move((x, y)):
                    moves.append((x, y, self.board.HEURISTIC[x][y]))
        moves.sort(
            key=lambda move: move[2], reverse=True
        )  # Sắp xếp theo giá trị heuristic
        return [(x, y) for x, y, _ in moves]
