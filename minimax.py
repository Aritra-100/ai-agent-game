"""minimax.py - Minimax search with optional Alpha-Beta pruning.

The search depth and heuristic are *parameters*; nothing is hard-coded.

Scoring (always from the point of view of the player who is choosing a move,
called the root player):
    root player wins  -> +100
    draw              ->    0
    root player loses -> -100
    depth limit hit   -> heuristic(board, root_player)

Depth counting: depth 1 = "my move" only, depth 2 = "my move, opponent reply",
depth 3 = "my move, reply, my move" ...

Counters
--------
nodes_evaluated : leaf positions that were scored (terminal or depth limit)
nodes_visited   : every position expanded or scored (internal + leaf nodes)
nodes_pruned    : number of sibling *branches* skipped by an alpha-beta cutoff
                  (each skipped branch would have been a whole sub-tree).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Tuple

from game import TicTacToe, Move

WIN_SCORE = 100
LOSS_SCORE = -100
DRAW_SCORE = 0


@dataclass
class SearchStats:
    nodes_evaluated: int = 0
    nodes_visited: int = 0
    nodes_pruned: int = 0

    def add(self, other: "SearchStats") -> None:
        self.nodes_evaluated += other.nodes_evaluated
        self.nodes_visited += other.nodes_visited
        self.nodes_pruned += other.nodes_pruned


class MinimaxSearch:
    """Minimax search; set use_alpha_beta=False for plain Minimax."""

    def __init__(self, heuristic: Callable, use_alpha_beta: bool = True):
        self.heuristic = heuristic
        self.use_alpha_beta = use_alpha_beta
        self.stats = SearchStats()

    # ------------------------------------------------------------------ #
    def search(self, game: TicTacToe, player: str, depth: int
               ) -> Tuple[List[Move], int]:
        """Find the best move(s) for `player`.

        Returns (best_moves, best_score) where best_moves lists *every* move that
        achieves the best score (ties are kept so the caller can break them).
        Statistics for this call are in `self.stats` (reset at the start).
        """
        if depth < 1:
            raise ValueError("depth must be >= 1")
        moves = game.get_valid_moves()
        if not moves:
            raise ValueError("no legal moves")

        self.stats = SearchStats()
        opponent = TicTacToe.opponent(player)
        best_score = -math.inf
        best_moves: List[Move] = []

        for move in moves:
            game.make_move(move, player)
            # alpha = best_score - 1 lets moves that *tie* with the current best
            # return their exact value (scores are integers), while strictly
            # worse moves are still cut off.  So tie-breaking stays correct.
            alpha = best_score - 1 if self.use_alpha_beta else -math.inf
            score = self._minimax(game, depth - 1, alpha, math.inf,
                                  False, player, opponent)
            game.undo_move(move)

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return best_moves, int(best_score)

    # ------------------------------------------------------------------ #
    def _minimax(self, game: TicTacToe, depth: int, alpha: float, beta: float,
                 maximizing: bool, root_player: str, to_move: str) -> int:
        stats = self.stats
        stats.nodes_visited += 1

        # ---- terminal positions -------------------------------------- #
        winner = game.check_winner()
        if winner is not None:
            stats.nodes_evaluated += 1
            return WIN_SCORE if winner == root_player else LOSS_SCORE
        moves = game.get_valid_moves()
        if not moves:
            stats.nodes_evaluated += 1
            return DRAW_SCORE

        # ---- depth limit: fall back to the heuristic ------------------ #
        if depth == 0:
            stats.nodes_evaluated += 1
            return self.heuristic(game.board, root_player)

        next_player = TicTacToe.opponent(to_move)

        if maximizing:
            value = -math.inf
            for i, move in enumerate(moves):
                game.make_move(move, to_move)
                value = max(value, self._minimax(game, depth - 1, alpha, beta,
                                                 False, root_player, next_player))
                game.undo_move(move)
                if self.use_alpha_beta:
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        stats.nodes_pruned += len(moves) - i - 1
                        break
            return value

        value = math.inf
        for i, move in enumerate(moves):
            game.make_move(move, to_move)
            value = min(value, self._minimax(game, depth - 1, alpha, beta,
                                             True, root_player, next_player))
            game.undo_move(move)
            if self.use_alpha_beta:
                beta = min(beta, value)
                if beta <= alpha:
                    stats.nodes_pruned += len(moves) - i - 1
                    break
        return value
