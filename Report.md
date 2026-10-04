# Short Analysis Report — AI Agent Battle (Tic-Tac-Toe)

**Setup.** NEXUS = Minimax + Alpha-Beta + heuristic H1 (line threats), depth 3.
TITAN = Minimax + Alpha-Beta + heuristic H2 (square values + open lines + threats), depth 3.
Scores: win +100, draw 0, loss −100; heuristics estimate unfinished positions (clamped to ±99).
Ties between exactly equal moves are broken randomly (seed 42). 10 games, starting player
alternating. Raw data: `results/*.csv`; everything below is read from those files.

## Results at a glance

| Experiment | Outcome |
|---|---|
| Battle, 10 games | NEXUS 0 wins · TITAN 0 wins · **10 draws** |
| Avg nodes evaluated / game | NEXUS 247.1 · TITAN 247.9 |
| Avg think time / game | NEXUS 1.62 ms · TITAN 1.86 ms |
| Depth 1 → 9 on the empty board (Alpha-Beta) | 9 → 11,758 nodes evaluated; plain Minimax needs up to 255,168 |

## Experiment 1: depth

**1. Did deeper search change the AI's decisions?** Yes, but the choice of the *first* move did
not change: on the empty board both heuristics pick the centre at every depth 1–4. Differences appear
in other positions. Over the 1090 positions with ≤ 4 pieces, the share of positions where every
candidate move is game-theoretically optimal rose from 88.8 % (depth 1) to 93.0 %, 95.2 %, 97.4 %,
97.8 % and 100 % (depth 6) for H1. For H2: 87.3 %, 92.7 %, 98.9 %, 97.4 %, 99.3 %, 100 %.
So depth generally improves decisions, but **not monotonically**: H2 at depth 3 (98.9 %) was
better than at depth 4 (97.4 %), because at a depth cut-off the heuristic's guess can be wrong, and
one more ply moves the cut-off to a different (not necessarily better-judged) position.

**2. Did execution time increase with depth?** Yes. Without pruning, one opening decision
took 0.09 ms at depth 1 and 1.2–1.3 s at depth 8–9. With Alpha-Beta: 0.05 ms → 76 ms.
Timings are machine dependent; the node counts are the reliable measure.

**3. Did the number of evaluated nodes increase?** Yes, steeply at first (plain Minimax:
9, 72, 504, 3,024, 15,120, 56,160, 154,944), then it flattens at 255,168 for depth 8 and 9
because the game cannot last more than 9 plies (the tree has run out). In the mid-game test position the
count flattens at 520 from depth 5 for the same reason.

**4. Did Alpha-Beta reduce the nodes explored?** Yes, a lot, with identical decisions
(verified by unit tests on 1090 positions). Reduction in evaluated nodes on the empty board:
50 % at depth 2, 73 % at depth 3, 86 % at depth 5, 93 % at depth 7, 95 % at depth 9
(255,168 → 11,758). The saving grows with depth.

**Game performance vs. cost.** Against a fixed opponent (TITAN, H2, depth 3), the H1 agent drew
all 10 games at every depth from 1 to 5. Game outcome therefore **did not discriminate between
depths**: Tic-Tac-Toe is a draw with sensible play, and even the depth-1 agent (which relies on its heuristic
to value blocking) did not lose to a depth-3 opponent in our sample. Meanwhile cost
grew from 22.5 to 1,837 nodes per game (≈ 82×). In this game, extra depth buys decision quality
(the table above) but not better results, i.e. depth is not automatically "better" in
every sense — it costs more and the benefit depends on how one measures it.

## Experiment 2: NEXUS vs TITAN

**5. Did the two agents make different decisions?** Yes, but rarely at depth 3. Over the 1090
positions with ≤ 4 pieces, their best-move sets differ in 64 positions (5.9 %), and they never
disagree completely (no position where the sets are disjoint). In the 10 games there were 6 distinct
move sequences (some sequences were reached by both agents, e.g. games 1, 4, 7, 9).

**6. How did the heuristics influence behaviour?** Both open with the centre, so their play is
similar (every game began with the centre and ended in a draw). H1 values only line potential; H2 adds square values, so it breaks ties differently in
quiet positions. We observed H2 costing slightly more time per node (1.86 ms vs 1.62 ms per game for
almost the same number of nodes, 247.9 vs 247.1) — consistent with H2 doing more work per evaluation —
and different pruning counts (NEXUS 190.2 vs TITAN 174.3 pruned per game); the latter depends on the
order in which scores appear, which is heuristic-dependent. (We did not run an experiment isolating
the cause of the pruning difference, so treat that as an observation, not a proven explanation.)

**7. Did first-player advantage appear?** No. The starting player won 0 of 5 games for NEXUS and 0 of 5
for TITAN. Tic-Tac-Toe is a theoretical draw, so no advantage is expected from competent play.
A cost effect did appear: the starting agent searched more because more cells were empty
(NEXUS 284.0 nodes/game as first vs 210.2 as second; TITAN 291.6 vs 204.2).

**8. Which agent won more games?** Neither: 0–0. We cannot claim either agent is better on this evidence.

**9. Were there many draws?** All 10 games (100 %) were draws, each lasting the full 9 moves.

**10. Did the agent that won more games require more computation?** There was no
winner. Total computation was nearly equal in nodes (247.1 vs 247.9 per game); TITAN used about 15 %
more time per game (1.86 ms vs 1.62 ms).

## Conclusion

* Minimax + Alpha-Beta works as intended; Alpha-Beta gives the same decisions as Minimax with up to
  95 % fewer evaluated nodes at depth 9 (tested).
* Deeper search improves decision quality on average (e.g. H1: 88.8 % → 100 % optimal-move rate from depth 1 → 6)
  but at rapidly growing cost, and the improvement is not strictly monotonic with an imperfect heuristic.
* Two reasonable but different heuristics produced nearly identical play at depth 3 and ended
  10–0–10 in draws; in a game that is a draw under perfect play, this is the expected outcome rather than a
  failure of the experiment.
* **Limitations:** only 10 games per setting, so no statistical conclusions on win rates; timings are machine
  dependent; the depth-vs-result experiment saturates at draws, so the decision-quality measure
  (1c) is the more informative one; random tie-breaking with seed 42 fixes one particular sample of games.
