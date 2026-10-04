"""heuristic.py - Board evaluation functions for non-terminal positions.

Every heuristic has the signature  h(board, player) -> int  and returns a score
from the point of view of `player` (positive = good for `player`).
Scores are clamped to [-99, 99] so that a real win (+100) / loss (-100) always
dominates any estimate.

Two reasonable, comparable heuristics are provided:

H1 "Line Threat"  - purely line based: counts how many of the 8 lines each side
                    can still win and how close each side is to completing them.
H2 "Positional"   - mixes square values (center > corner > edge), the number of
                    still-open lines and threats.  It cares more about *where*
                    pieces sit than H1 does.
"""

from __future__ import annotations

from typing import Callable, List

from game import WIN_LINES, EMPTY

Board = List[List[str]]
Heuristic = Callable[[Board, str], int]

CLAMP = 99


def _clamp(v: int) -> int:
    return max(-CLAMP, min(CLAMP, v))


def _line_counts(board: Board, line, player: str):
    """Return (my_pieces, opp_pieces) on one line."""
    mine = theirs = 0
    for r, c in line:
        v = board[r][c]
        if v == player:
            mine += 1
        elif v != EMPTY:
            theirs += 1
    return mine, theirs


# --------------------------------------------------------------------------- #
# H1 - Line Threat heuristic
# --------------------------------------------------------------------------- #
def h1_line_threat(board: Board, player: str) -> int:
    """Score open lines by how many pieces the owner already has on them.

    Open line with 2 of my pieces (a threat)   -> +10
    Open line with 1 of my pieces              -> +1
    Same for the opponent, with a negative sign.
    A line holding pieces of both players is dead and scores 0.
    """
    score = 0
    for line in WIN_LINES:
        mine, theirs = _line_counts(board, line, player)
        if mine and theirs:
            continue  # dead line
        if mine == 2:
            score += 10
        elif mine == 1:
            score += 1
        elif theirs == 2:
            score -= 10
        elif theirs == 1:
            score -= 1
    return _clamp(score)


# --------------------------------------------------------------------------- #
# H2 - Positional heuristic
# --------------------------------------------------------------------------- #
_SQUARE_VALUE = [
    [2, 1, 2],
    [1, 4, 1],
    [2, 1, 2],
]


def h2_positional(board: Board, player: str) -> int:
    """Square values + open-line potential + threats.

    * centre = 4, corner = 2, edge = 1 for each owned square (opponent negative)
    * +3 for every line that is still open for me and has no opponent piece,
      -3 for every line open for the opponent (potential winning lines)
    * +8 / -8 for a threat (two pieces + empty cell on an open line)
    """
    opp = "O" if player == "X" else "X"
    score = 0
    for r in range(3):
        for c in range(3):
            if board[r][c] == player:
                score += _SQUARE_VALUE[r][c]
            elif board[r][c] == opp:
                score -= _SQUARE_VALUE[r][c]
    for line in WIN_LINES:
        mine, theirs = _line_counts(board, line, player)
        if theirs == 0:
            score += 3
            if mine == 2:
                score += 8
        if mine == 0:
            score -= 3
            if theirs == 2:
                score -= 8
    return _clamp(score)


HEURISTICS = {
    "H1": h1_line_threat,
    "H2": h2_positional,
}
