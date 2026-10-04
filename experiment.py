"""experiment.py - Runs the experiments and handles result files.

Experiment 1 (depth)  : how search depth affects decisions, cost and results.
Experiment 2 (battle) : NEXUS vs TITAN, N games, starting player alternates.

All results are written to CSV files first; summaries are then computed by
*reading those files back*, not from values kept in memory.
"""

from __future__ import annotations

import csv
import os
import time
from typing import Dict, List, Optional

from agents import Agent, make_nexus, make_titan
from game import TicTacToe
from minimax import MinimaxSearch
from heuristic import HEURISTICS

RESULTS_DIR = "results"
BATTLE_FIELDS = [
    "game", "first", "winner", "moves",
    "nexus_nodes", "titan_nodes", "nexus_pruned", "titan_pruned",
    "nexus_time_s", "titan_time_s", "time_s", "move_sequence",
]


# =========================================================================== #
# Experiment 2 - the battle
# =========================================================================== #
class Experiment:
    """Plays AI-vs-AI games between two agents and records statistics."""

    def __init__(self, agent1: Agent, agent2: Agent, verbose: bool = False):
        self.agent1 = agent1   # plays the "nexus_*" columns
        self.agent2 = agent2   # plays the "titan_*" columns
        self.verbose = verbose

    def run_game(self, game_no: int, first: Agent) -> Dict:
        """Play one full game. `first` plays X and moves first."""
        second = self.agent2 if first is self.agent1 else self.agent1
        players = {"X": first, "O": second}
        self.agent1.reset_totals()
        self.agent2.reset_totals()

        game = TicTacToe()
        turn = "X"
        sequence = []
        start = time.perf_counter()
        while not game.is_terminal():
            agent = players[turn]
            move = agent.choose_move(game, turn)
            game.make_move(move, turn)
            sequence.append(f"{turn}{move[0]}{move[1]}")
            if self.verbose:
                print(f"  {agent.name} ({turn}) plays {move}")
            turn = TicTacToe.opponent(turn)
        elapsed = time.perf_counter() - start

        winner_symbol = game.check_winner()
        winner = "DRAW" if winner_symbol is None else players[winner_symbol].name
        if self.verbose:
            print(game.display())
            print(f"  Result: {winner}\n")

        return {
            "game": game_no,
            "first": first.name,
            "winner": winner,
            "moves": len(sequence),
            "nexus_nodes": self.agent1.totals.nodes_evaluated,
            "titan_nodes": self.agent2.totals.nodes_evaluated,
            "nexus_pruned": self.agent1.totals.nodes_pruned,
            "titan_pruned": self.agent2.totals.nodes_pruned,
            "nexus_time_s": round(self.agent1.think_time, 6),
            "titan_time_s": round(self.agent2.think_time, 6),
            "time_s": round(elapsed, 6),
            "move_sequence": " ".join(sequence),
        }

    def run_multiple_games(self, n_games: int = 10) -> List[Dict]:
        """Run n games, alternating the starting player (agent1 starts game 1)."""
        rows = []
        for g in range(1, n_games + 1):
            first = self.agent1 if g % 2 == 1 else self.agent2
            if self.verbose:
                print(f"Game {g}: {first.name} starts")
            rows.append(self.run_game(g, first))
        return rows

    @staticmethod
    def save_results(rows: List[Dict], path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=BATTLE_FIELDS)
            writer.writeheader()
            writer.writerows(rows)


def load_csv(path: str) -> List[Dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def summarize_battle(path: str, name1: str = "NEXUS", name2: str = "TITAN") -> Dict:
    """Read the saved battle CSV and compute the summary statistics."""
    rows = load_csv(path)
    n = len(rows)
    if n == 0:
        raise ValueError("results file is empty")

    def avg(col):
        return sum(float(r[col]) for r in rows) / n

    wins1 = sum(r["winner"] == name1 for r in rows)
    wins2 = sum(r["winner"] == name2 for r in rows)
    draws = sum(r["winner"] == "DRAW" for r in rows)

    def first_stats(first_name):
        sub = [r for r in rows if r["first"] == first_name]
        return {
            "games": len(sub),
            "first_wins": sum(r["winner"] == first_name for r in sub),
            "draws": sum(r["winner"] == "DRAW" for r in sub),
        }

    return {
        "games": n,
        f"{name1}_wins": wins1,
        f"{name2}_wins": wins2,
        "draws": draws,
        "avg_moves": avg("moves"),
        f"avg_{name1}_nodes": avg("nexus_nodes"),
        f"avg_{name2}_nodes": avg("titan_nodes"),
        f"avg_{name1}_pruned": avg("nexus_pruned"),
        f"avg_{name2}_pruned": avg("titan_pruned"),
        f"avg_{name1}_time_s": avg("nexus_time_s"),
        f"avg_{name2}_time_s": avg("titan_time_s"),
        "avg_game_time_s": avg("time_s"),
        "first_player": {name1: first_stats(name1), name2: first_stats(name2)},
    }


def print_battle_summary(summary: Dict, name1="NEXUS", name2="TITAN") -> None:
    print(f"Games played        : {summary['games']}")
    print(f"{name1} wins        : {summary[name1 + '_wins']}")
    print(f"{name2} wins        : {summary[name2 + '_wins']}")
    print(f"Draws               : {summary['draws']}")
    print(f"Average moves/game  : {summary['avg_moves']:.2f}")
    for nm in (name1, name2):
        print(f"{nm}: avg nodes evaluated {summary['avg_' + nm + '_nodes']:.1f}, "
              f"avg nodes pruned {summary['avg_' + nm + '_pruned']:.1f}, "
              f"avg think time {summary['avg_' + nm + '_time_s'] * 1000:.2f} ms/game")
    print(f"Average game time   : {summary['avg_game_time_s'] * 1000:.2f} ms")
    for nm, s in summary["first_player"].items():
        print(f"Games started by {nm}: {s['games']} -> "
              f"starter won {s['first_wins']}, draws {s['draws']}")


# =========================================================================== #
# Experiment 1 - search depth
# =========================================================================== #
DEPTH_COST_FIELDS = ["depth", "alpha_beta", "position", "nodes_evaluated",
                     "nodes_visited", "nodes_pruned", "time_s"]
DEPTH_RESULT_FIELDS = ["depth", "games", "wins", "draws", "losses",
                       "avg_nodes_evaluated", "avg_nodes_pruned", "avg_time_s"]
DEPTH_QUALITY_FIELDS = ["heuristic", "depth", "positions", "all_best_optimal",
                        "pct_all_best_optimal", "avg_best_moves"]

# A mid-game position used for the cost experiment (X to move).
MIDGAME = [["X", "", ""],
           ["", "O", ""],
           ["", "", "X"]]


def depth_cost_experiment(depths, heuristic_name: str = "H1") -> List[Dict]:
    """Cost of ONE move decision at each depth, with and without alpha-beta.

    Game, algorithm and heuristic are fixed; only the depth changes.
    """
    h = HEURISTICS[heuristic_name]
    rows = []
    positions = {"empty board (X to move)": (TicTacToe(), "X"),
                 "mid-game (O to move)": (TicTacToe(MIDGAME), "O")}
    for d in depths:
        for use_ab in (False, True):
            for pos_name, (game, player) in positions.items():
                searcher = MinimaxSearch(h, use_alpha_beta=use_ab)
                start = time.perf_counter()
                searcher.search(game.copy(), player, d)
                elapsed = time.perf_counter() - start
                rows.append({
                    "depth": d,
                    "alpha_beta": "yes" if use_ab else "no",
                    "position": pos_name,
                    "nodes_evaluated": searcher.stats.nodes_evaluated,
                    "nodes_visited": searcher.stats.nodes_visited,
                    "nodes_pruned": searcher.stats.nodes_pruned,
                    "time_s": round(elapsed, 6),
                })
    return rows


def depth_game_experiment(depths, n_games: int = 10, seed: int = 0,
                          opponent_depth: int = 3) -> List[Dict]:
    """Play the NEXUS-style agent (H1, alpha-beta) at each depth against one
    fixed reference opponent (TITAN, H2, depth `opponent_depth`).

    Only the depth of the tested agent changes between rows.
    """
    rows = []
    for d in depths:
        tested = make_nexus(depth=d, seed=seed)
        reference = make_titan(depth=opponent_depth, seed=seed + 1)
        exp = Experiment(tested, reference)
        results = exp.run_multiple_games(n_games)
        rows.append({
            "depth": d,
            "games": n_games,
            "wins": sum(r["winner"] == "NEXUS" for r in results),
            "draws": sum(r["winner"] == "DRAW" for r in results),
            "losses": sum(r["winner"] == "TITAN" for r in results),
            "avg_nodes_evaluated": sum(r["nexus_nodes"] for r in results) / n_games,
            "avg_nodes_pruned": sum(r["nexus_pruned"] for r in results) / n_games,
            "avg_time_s": sum(r["nexus_time_s"] for r in results) / n_games,
        })
    return rows


def _reachable_positions(max_pieces: int):
    """All distinct boards reachable with at most `max_pieces` moves played."""
    seen = {}
    frontier = [(TicTacToe(), "X")]
    for _ in range(max_pieces + 1):
        nxt = []
        for game, player in frontier:
            key = tuple(tuple(r) for r in game.board)
            if key in seen or game.is_terminal():
                continue
            seen[key] = (game.copy(), player)
            for m in game.get_valid_moves():
                g = game.copy()
                g.make_move(m, player)
                nxt.append((g, TicTacToe.opponent(player)))
        frontier = nxt
    return list(seen.values())


def depth_quality_experiment(depths, max_pieces: int = 4) -> List[Dict]:
    """Does deeper search change the quality of decisions?

    For every reachable non-terminal position with <= max_pieces pieces, compare
    the agent's set of best moves with the set of game-theoretically optimal
    moves (full-depth search, depth 9).  A position counts as 'all_best_optimal'
    when every move the agent might choose is optimal.
    """
    positions = _reachable_positions(max_pieces)
    perfect = MinimaxSearch(HEURISTICS["H1"], use_alpha_beta=True)
    optimal_sets = [set(perfect.search(g.copy(), p, 9)[0]) for g, p in positions]

    rows = []
    for hname, h in HEURISTICS.items():
        for d in depths:
            searcher = MinimaxSearch(h, use_alpha_beta=True)
            ok = 0
            total_best = 0
            for (g, p), opt in zip(positions, optimal_sets):
                best, _ = searcher.search(g.copy(), p, d)
                total_best += len(best)
                if set(best) <= opt:
                    ok += 1
            rows.append({
                "heuristic": hname,
                "depth": d,
                "positions": len(positions),
                "all_best_optimal": ok,
                "pct_all_best_optimal": round(100.0 * ok / len(positions), 1),
                "avg_best_moves": round(total_best / len(positions), 2),
            })
    return rows


def save_rows(rows: List[Dict], fields: List[str], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def print_table(path: str) -> None:
    """Pretty-print any results CSV."""
    rows = load_csv(path)
    if not rows:
        print("(empty)")
        return
    cols = list(rows[0].keys())
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))
