"""main.py - Command-line entry point for the AI Agent Battle.

Examples
--------
    python main.py all                 # depth experiments + 10-game battle
    python main.py battle              # only the 10-game NEXUS vs TITAN battle
    python main.py battle --games 10 --depth-nexus 3 --depth-titan 3 --seed 42
    python main.py depth               # only the search-depth experiments
    python main.py demo                # one verbose game
    python main.py summary             # re-read results/results.csv and summarise
"""

from __future__ import annotations

import argparse
import os

import experiment as ex
from agents import make_nexus, make_titan
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
BATTLE_CSV = os.path.join(RESULTS_DIR, "results.csv")
DEPTH_COST_CSV = os.path.join(RESULTS_DIR, "depth_cost.csv")
DEPTH_RESULT_CSV = os.path.join(RESULTS_DIR, "depth_results.csv")
DEPTH_QUALITY_CSV = os.path.join(RESULTS_DIR, "depth_quality.csv")


def run_battle(args) -> None:
    nexus = make_nexus(depth=args.depth_nexus, seed=args.seed)
    titan = make_titan(depth=args.depth_titan, seed=args.seed + 1)
    print("=== EXPERIMENT 2: AI AGENT BATTLE ===")
    print(nexus.describe())
    print(titan.describe())
    print()
    experiment = ex.Experiment(nexus, titan, verbose=args.verbose)
    rows = experiment.run_multiple_games(args.games)
    ex.Experiment.save_results(rows, BATTLE_CSV)
    print(f"Saved {len(rows)} games to {BATTLE_CSV}\n")
    ex.print_table(BATTLE_CSV)
    print()
    ex.print_battle_summary(ex.summarize_battle(BATTLE_CSV))


def run_depth(args) -> None:
    depths_cost = list(range(1, 10))
    depths_game = [1, 2, 3, 4, 5]
    print("=== EXPERIMENT 1: DOES DEEPER THINKING HELP? ===\n")

    print("-- (a) Cost of one decision, per depth --")
    ex.save_rows(ex.depth_cost_experiment(depths_cost), ex.DEPTH_COST_FIELDS,
                 DEPTH_COST_CSV)
    ex.print_table(DEPTH_COST_CSV)

    print("\n-- (b) Game results: H1 agent at each depth vs fixed reference "
          "(TITAN, H2, depth 3), 10 games each --")
    ex.save_rows(ex.depth_game_experiment(depths_game, n_games=10, seed=args.seed),
                 ex.DEPTH_RESULT_FIELDS, DEPTH_RESULT_CSV)
    ex.print_table(DEPTH_RESULT_CSV)

    print("\n-- (c) Decision quality vs perfect play (positions with <= 4 pieces) --")
    ex.save_rows(ex.depth_quality_experiment([1, 2, 3, 4, 5, 6]),
                 ex.DEPTH_QUALITY_FIELDS, DEPTH_QUALITY_CSV)
    ex.print_table(DEPTH_QUALITY_CSV)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Agent Battle - Tic-Tac-Toe")
    parser.add_argument("command", choices=["all", "battle", "depth", "demo", "summary"],
                        nargs="?", default="all")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--depth-nexus", type=int, default=3)
    parser.add_argument("--depth-titan", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42,
                        help="random seed for tie-breaking (reproducible runs)")
    parser.add_argument("--verbose", action="store_true",
                        help="print every move of every game")
    args = parser.parse_args()

    if args.command == "demo":
        args.games, args.verbose = 1, True
        run_battle(args)
    elif args.command == "battle":
        run_battle(args)
    elif args.command == "depth":
        run_depth(args)
    elif args.command == "summary":
        ex.print_battle_summary(ex.summarize_battle(BATTLE_CSV))
    else:
        run_depth(args)
        run_battle(args)


if __name__ == "__main__":
    main()
