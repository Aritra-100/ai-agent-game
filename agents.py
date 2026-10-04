"""agents.py - The two AI agents: NEXUS and TITAN.

Both agents use Minimax + Alpha-Beta pruning. They differ in identity and in
the heuristic they use to judge unfinished positions:

    NEXUS : heuristic H1 (line-threat based)
    TITAN : heuristic H2 (positional + open-line based)

Neither agent is weakened: both search exhaustively to their configured depth.
When several moves have exactly the same score, one is picked at random.
"""

from __future__ import annotations

import random
import time
from typing import Callable, List, Optional

from game import TicTacToe, Move
from heuristic import h1_line_threat, h2_positional
from minimax import MinimaxSearch, SearchStats


class Agent:
    """A named Minimax agent with configurable depth and heuristic."""

    def __init__(self, name: str, depth: int, heuristic: Callable,
                 heuristic_name: str = "", use_alpha_beta: bool = True,
                 seed: Optional[int] = None):
        self.name = name
        self.depth = depth
        self.heuristic = heuristic
        self.heuristic_name = heuristic_name or getattr(heuristic, "__name__", "?")
        self.use_alpha_beta = use_alpha_beta
        self.rng = random.Random(seed)
        self.search = MinimaxSearch(heuristic, use_alpha_beta)
        self.reset_totals()

    # ------------------------------------------------------------------ #
    def reset_totals(self) -> None:
        """Clear the cumulative statistics (call before each game)."""
        self.totals = SearchStats()
        self.think_time = 0.0
        self.moves_made = 0

    def evaluate(self, game: TicTacToe, player: str) -> int:
        """Heuristic value of the current board for `player`."""
        return self.heuristic(game.board, player)

    def best_moves(self, game: TicTacToe, player: str) -> List[Move]:
        """All equally-best moves (no random choice, no stats accumulated)."""
        moves, _ = self.search.search(game, player, self.depth)
        return moves

    def choose_move(self, game: TicTacToe, player: str,
                    depth: Optional[int] = None) -> Move:
        """Pick a move for `player`; depth defaults to the agent's own depth."""
        d = self.depth if depth is None else depth
        start = time.perf_counter()
        moves, _score = self.search.search(game, player, d)
        self.think_time += time.perf_counter() - start
        self.totals.add(self.search.stats)
        self.moves_made += 1
        return self.rng.choice(moves)  # random only among exactly-tied moves

    def describe(self) -> str:
        ab = "Alpha-Beta" if self.use_alpha_beta else "plain Minimax"
        return (f"{self.name}: Minimax + {ab}, depth={self.depth}, "
                f"heuristic={self.heuristic_name}")


def make_nexus(depth: int = 3, use_alpha_beta: bool = True,
               seed: Optional[int] = None) -> Agent:
    return Agent("NEXUS", depth, h1_line_threat, "H1", use_alpha_beta, seed)


def make_titan(depth: int = 3, use_alpha_beta: bool = True,
               seed: Optional[int] = None) -> Agent:
    return Agent("TITAN", depth, h2_positional, "H2", use_alpha_beta, seed)
