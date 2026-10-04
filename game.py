"""game.py - Tic-Tac-Toe board and rules.

The board is a 3x3 list of lists holding 'X', 'O' or '' (empty).
Moves are (row, col) tuples with 0-based indices.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

Move = Tuple[int, int]

# All 8 winning lines as lists of (row, col) cells.
WIN_LINES: List[List[Move]] = (
    [[(r, c) for c in range(3)] for r in range(3)]                 # rows
    + [[(r, c) for r in range(3)] for c in range(3)]               # columns
    + [[(i, i) for i in range(3)], [(i, 2 - i) for i in range(3)]]  # diagonals
)

EMPTY = ""


class TicTacToe:
    """A Tic-Tac-Toe game state with make/undo support for fast search."""

    def __init__(self, board: Optional[List[List[str]]] = None):
        if board is None:
            self.board = [[EMPTY] * 3 for _ in range(3)]
        else:
            self.board = [row[:] for row in board]

    # ------------------------------------------------------------------ #
    # Basic helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def opponent(player: str) -> str:
        return "O" if player == "X" else "X"

    def copy(self) -> "TicTacToe":
        return TicTacToe(self.board)

    def display(self) -> str:
        """Return a printable string of the board."""
        rows = []
        for r in range(3):
            cells = [self.board[r][c] or "." for c in range(3)]
            rows.append(" " + " | ".join(cells))
        return "\n---+---+---\n".join(rows)

    def print_board(self) -> None:
        print(self.display())

    # ------------------------------------------------------------------ #
    # Game rules
    # ------------------------------------------------------------------ #
    def get_valid_moves(self) -> List[Move]:
        """Return all empty cells (row-major order)."""
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == EMPTY]

    def make_move(self, move: Move, player: str) -> None:
        r, c = move
        if player not in ("X", "O"):
            raise ValueError(f"Invalid player: {player!r}")
        if not (0 <= r < 3 and 0 <= c < 3):
            raise ValueError(f"Move {move} is outside the board")
        if self.board[r][c] != EMPTY:
            raise ValueError(f"Cell {move} is already occupied")
        self.board[r][c] = player

    def undo_move(self, move: Move) -> None:
        r, c = move
        self.board[r][c] = EMPTY

    def check_winner(self) -> Optional[str]:
        """Return 'X' or 'O' if that player has three in a line, else None."""
        b = self.board
        for line in WIN_LINES:
            (r0, c0), (r1, c1), (r2, c2) = line
            v = b[r0][c0]
            if v != EMPTY and v == b[r1][c1] == b[r2][c2]:
                return v
        return None

    def is_board_full(self) -> bool:
        return all(cell != EMPTY for row in self.board for cell in row)

    def is_draw(self) -> bool:
        return self.check_winner() is None and self.is_board_full()

    def is_terminal(self) -> bool:
        return self.check_winner() is not None or self.is_board_full()

    def __str__(self) -> str:
        return self.display()
