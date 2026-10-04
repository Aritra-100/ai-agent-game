# AI Agent Battle — Tic-Tac-Toe

AI/ML Laboratory · B.Tech. 5th Semester · Assignment X_02

Two named AI agents, **NEXUS** and **TITAN**, play Tic-Tac-Toe against each other using
Minimax with Alpha-Beta pruning. They share the same search algorithm but judge unfinished
positions with *different heuristics*. The project measures how search depth, heuristics and
pruning affect decisions and computation. Everything (Minimax, Alpha-Beta, heuristics, game
engine) is written from scratch in pure Python (standard library only).

## Project structure

```
ai-agent-battle/
├── main.py          # command-line entry point
├── game.py          # TicTacToe class: board, moves, win/draw detection
├── minimax.py       # Minimax + Alpha-Beta search, node counters
├── heuristic.py     # H1 and H2 evaluation functions
├── agents.py        # Agent class; NEXUS and TITAN
├── experiment.py    # Experiment class, depth experiments, CSV save/load/summary
├── tests/test_all.py
├── results/
│   ├── results.csv        # 10-game battle (Experiment 2)
│   ├── depth_cost.csv     # cost of one decision per depth (Experiment 1a)
│   ├── depth_results.csv  # game results per depth (Experiment 1b)
│   ├── depth_quality.csv  # decision quality per depth (Experiment 1c)
│   └── run_log.txt        # console output of `python main.py all --seed 42`
├── REPORT.md        # short analysis / report
└── README.md
```

## How to run

Requires Python 3.8+; no external packages.

```bash
python main.py all            # depth experiments + 10-game battle, writes results/*.csv
python main.py battle         # only NEXUS vs TITAN (10 games)
python main.py depth          # only the search-depth experiments
python main.py demo           # one game, printing every move
python main.py summary        # recompute statistics from results/results.csv
python main.py battle --games 10 --depth-nexus 3 --depth-titan 3 --seed 42
python -m unittest discover -s tests -v    # unit tests
```

Depth, number of games and random seed are command-line options; the search depth is a
parameter of `MinimaxSearch.search(game, player, depth)` and of each `Agent`, never
hard-coded. Runs are reproducible with `--seed` (default 42); the seed only affects the
random choice among *exactly tied* moves.

## Implementation

### Game engine (`game.py`)
`TicTacToe` stores a 3×3 list of lists (`'X'`, `'O'` or `''`) and provides `display()`,
`get_valid_moves()`, `make_move()`, `undo_move()`, `check_winner()`, `is_draw()` and
`is_terminal()`. Moves are `(row, col)` tuples.

### Minimax (`minimax.py`)
Scores are always from the viewpoint of the player choosing the move:
win **+100**, draw **0**, loss **−100**. At the depth limit the heuristic estimates the
position. Depth 1 = "my move", depth 2 = "my move, opponent reply", depth 3 = "my move,
reply, my move", and so on. MAX nodes maximise and MIN nodes minimise.

### Alpha-Beta pruning
Same search with `alpha`/`beta` bounds; a branch is cut when `beta <= alpha`. It is switched
with `use_alpha_beta`, so plain Minimax is available for comparison. The unit tests check
that Alpha-Beta returns **exactly the same best-move set and score** as plain Minimax over
1090 positions, depths 1/2/3/9 and both heuristics. At the root, ties are kept exact (each
root move is searched with `alpha = best_so_far − 1`) so random tie-breaking is fair.

Counters recorded per search:

| Counter | Meaning |
|---|---|
| `nodes_evaluated` | leaf positions scored (game over or depth limit reached) |
| `nodes_visited` | all positions visited (internal + leaf) |
| `nodes_pruned` | sibling **branches** skipped by an Alpha-Beta cutoff (each is a whole subtree, so this is a lower bound on work saved) |

### Heuristics (`heuristic.py`)
Both return an integer from the player's viewpoint, clamped to ±99 so a real win/loss
(±100) always dominates an estimate.

* **H1 – Line Threat** (used by NEXUS): over the 8 lines, a line containing pieces of both
  players is dead (0). Otherwise own line with 2 pieces `+10` (threat), with 1 piece `+1`;
  the same for the opponent with a negative sign.
* **H2 – Positional** (used by TITAN): square values (centre 4, corner 2, edge 1) for own
  pieces minus the opponent's, `+3` for each line still open to me / `−3` for each open to the
  opponent, and `+8 / −8` for a threat (two pieces on an open line).

### Agents (`agents.py`)

| Agent | Algorithm | Heuristic | Depth (battle) |
|---|---|---|---|
| **NEXUS** | Minimax + Alpha-Beta | H1 (line threat) | 3 |
| **TITAN** | Minimax + Alpha-Beta | H2 (positional) | 3 |

Neither agent is weakened. When several moves have exactly the same score, one is chosen at
random (so different games can differ without making either agent weaker).

### Experiments (`experiment.py`)
* `Experiment.run_game()`, `run_multiple_games()`, `save_results()` – battle; games
  alternate the starting player (game 1: NEXUS starts, game 2: TITAN, …).
* Results are written to CSV first; `summarize_battle()` then **reads the CSV back** to
  compute wins, draws, averages, so nothing depends on printed values or hard-coded results.

## Results

All numbers below come from `python main.py all --seed 42` (files in `results/`).
Wall-clock times vary by machine; node counts are deterministic for a given seed.

### Experiment 2 – NEXUS (H1, depth 3) vs TITAN (H2, depth 3), 10 games

| Game | First | Winner | Moves | NEXUS nodes | TITAN nodes | NEXUS pruned | TITAN pruned |
|---|---|---|---|---|---|---|---|
| 1 | NEXUS | DRAW | 9 | 279 | 197 | 254 | 144 |
| 2 | TITAN | DRAW | 9 | 198 | 300 | 139 | 217 |
| 3 | NEXUS | DRAW | 9 | 314 | 242 | 215 | 120 |
| 4 | TITAN | DRAW | 9 | 195 | 286 | 146 | 239 |
| 5 | NEXUS | DRAW | 9 | 269 | 188 | 224 | 140 |
| 6 | TITAN | DRAW | 9 | 218 | 284 | 140 | 197 |
| 7 | NEXUS | DRAW | 9 | 279 | 197 | 254 | 144 |
| 8 | TITAN | DRAW | 9 | 222 | 304 | 136 | 201 |
| 9 | NEXUS | DRAW | 9 | 279 | 197 | 254 | 144 |
| 10 | TITAN | DRAW | 9 | 218 | 284 | 140 | 197 |

**Summary (computed from `results.csv`):** NEXUS 0 wins, TITAN 0 wins, **10 draws**.
Average nodes evaluated per game: NEXUS 247.1, TITAN 247.9. Average nodes pruned: NEXUS 190.2,
TITAN 174.3. Average think time per game: NEXUS 1.62 ms, TITAN 1.86 ms. Full per-game
times and move sequences are in `results/results.csv`.

### Experiment 1 – Does deeper thinking help?

Fixed: game, Minimax + Alpha-Beta, heuristic H1. Only the depth changes.

**(a) Cost of one decision from the empty board** (`depth_cost.csv`; times on the run machine)

| Depth | Nodes evaluated (plain Minimax) | Nodes evaluated (Alpha-Beta) | Nodes pruned (Alpha-Beta) | Time plain | Time Alpha-Beta |
|---|---|---|---|---|---|
| 1 | 9 | 9 | 0 | 0.09 ms | 0.05 ms |
| 2 | 72 | 36 | 36 | 0.50 ms | 0.22 ms |
| 3 | 504 | 137 | 163 | 3.2 ms | 0.95 ms |
| 4 | 3,024 | 600 | 651 | 20.4 ms | 4.2 ms |
| 5 | 15,120 | 2,106 | 1,748 | 87.9 ms | 13.7 ms |
| 6 | 56,160 | 3,686 | 4,881 | 343 ms | 26.4 ms |
| 7 | 154,944 | 10,610 | 8,941 | 873 ms | 66.0 ms |
| 8 | 255,168 | 10,768 | 12,050 | 1,342 ms | 70.4 ms |
| 9 | 255,168 | 11,758 | 11,329 | 1,225 ms | 76.3 ms |

**(b) Game results: H1 agent at depth d vs. a fixed reference opponent (TITAN, H2, depth 3), 10 games per depth** (`depth_results.csv`)

| Depth | Result (W/D/L) | Avg nodes evaluated / game | Avg nodes pruned / game | Avg think time / game |
|---|---|---|---|---|
| 1 | 0 / 10 / 0 | 22.5 | 0.0 | 0.16 ms |
| 2 | 0 / 10 / 0 | 76.4 | 44.1 | 0.52 ms |
| 3 | 0 / 10 / 0 | 247.1 | 190.2 | 1.65 ms |
| 4 | 0 / 10 / 0 | 689.7 | 676.9 | 4.84 ms |
| 5 | 0 / 10 / 0 | 1,837.4 | 1,537.1 | 12.6 ms |

**(c) Decision quality vs. perfect play** (`depth_quality.csv`): across the 1090 positions reachable
with ≤ 4 pieces on the board, percentage of positions where *every* move the agent might choose is a
game-theoretically optimal move (optimal = depth-9 search).

| Depth | H1 | H2 |
|---|---|---|
| 1 | 88.8 % | 87.3 % |
| 2 | 93.0 % | 92.7 % |
| 3 | 95.2 % | 98.9 % |
| 4 | 97.4 % | 97.4 % |
| 5 | 97.8 % | 99.3 % |
| 6 | 100 % | 100 % |

See **REPORT.md** for the full analysis, observations and conclusion.

## Rules compliance

* Python only; Minimax, Alpha-Beta and heuristics implemented from scratch (no AI/game libraries).
* Two agents with different heuristics; both genuinely search (no random-move agent).
* 10 AI-vs-AI games, starting player alternates; results saved to `results/results.csv`
  and summaries computed from the saved file; nothing hard-coded.
* Depth experiment performed; nodes evaluated, nodes pruned and time recorded.
* OOP: `TicTacToe`, `MinimaxSearch`, `Agent`, `Experiment`.
