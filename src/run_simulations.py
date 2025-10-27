#!/usr/bin/env python3
"""
Main simulation runner for Psycho-Dice-Namic
"""

import os
import sys
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_engine import GameEngine
from archetypes import TabulaRasa, Euphoria, Temperance, Intellectualism, Belligerence, Naivety, Guilt, Jealousy, Anxiety
from simulators import ArchetypeSimulator, HandTester


def setup_templates():
    """Setup Jinja2 environment"""
    template_dir = Path(__file__).parent.parent / "templates"
    return Environment(loader=FileSystemLoader(template_dir))


def run_archetype_simulation():
    """Run archetype vs archetype simulation"""
    print("🎲 Running Archetype vs Archetype Simulation...")

    game_engine = GameEngine()
    simulator = ArchetypeSimulator(game_engine)

    # Create archetypes
    tabula_rasa = TabulaRasa()
    euphoria = Euphoria()

    # Run simulation
    results = simulator.simulate_matches(tabula_rasa, euphoria, num_matches=5000)

    print(f"Results: {results['archetype1']} vs {results['archetype2']}")
    print(f"Win rates: {results['win_rate1']:.1%} vs {results['win_rate2']:.1%}")
    print(f"Ties: {results['tie_rate']:.1%}")
    print(f"Average rounds: {results['avg_rounds']:.1f}")

    return results
def run_archetype_tournament():
    """Run a tournament across all archetypes and aggregate win/tie rates per archetype"""
    print("🎲 Running Archetype Tournament...")

    game_engine = GameEngine()
    simulator = ArchetypeSimulator(game_engine)

    archetypes = [
        TabulaRasa(), Euphoria(), Temperance(), Intellectualism(), Belligerence(),
        Naivety(), Guilt(), Jealousy(), Anxiety()
    ]

    tresults = simulator.simulate_tournament(archetypes, matches_per_pair=5000)

    # Aggregate per-arch wins, ties, matches
    arch_stats = {}
    names = [a.name for a in archetypes]
    for a in names:
        wins = ties = matches = 0
        for b in names:
            if a == b:
                continue
            if a in tresults["match_results"] and b in tresults["match_results"][a]:
                mr = tresults["match_results"][a][b]
                wins += mr.get("wins1", 0)
                ties += mr.get("ties", 0)
                matches += mr.get("wins1", 0) + mr.get("wins2", 0) + mr.get("ties", 0)
        win_rate = wins / matches if matches else 0
        tie_rate = ties / matches if matches else 0
        arch_stats[a] = {"win_rate": win_rate, "tie_rate": tie_rate, "matches": matches}

    # Sort by win rate descending
    sorted_names = sorted(names, key=lambda n: arch_stats[n]["win_rate"], reverse=True)
    win_rates = [arch_stats[n]["win_rate"] for n in sorted_names]
    tie_rates = [arch_stats[n]["tie_rate"] for n in sorted_names]

    print("Archetype Ranking (by win rate):")
    for i, n in enumerate(sorted_names, 1):
        print(f"{i}. {n}: win {arch_stats[n]['win_rate']:.3f}, tie {arch_stats[n]['tie_rate']:.3f}")

    return {
        "names": sorted_names,
        "win_rates": win_rates,
        "tie_rates": tie_rates,
        "arch_stats": arch_stats,
    }



def run_hand_testing():
    """Run special dice vs normal dice testing"""
    print("🎲 Running Special Dice Testing...")

    game_engine = GameEngine()
    tester = HandTester(game_engine)

    # Test all special dice (full game mode)
    test_results = tester.test_all_special_dice(num_tests=1000)
    # Pure one-roll mode baseline
    pure_results = tester.test_all_special_dice_pure(num_tests=5000)

    # Get performance ranking
    performance_ranking = tester.compare_dice_performance(test_results)

    print("Performance Ranking:")
    for i, (name, score) in enumerate(performance_ranking):
        print(f"{i+1}. {name}: {score:.3f}")

    return test_results, performance_ranking, pure_results


def generate_reports(archetype_results, hand_test_results, performance_ranking, tournament_results, pure_results):
    """Generate HTML reports using Jinja2 templates"""
    print("📊 Generating Reports...")

    env = setup_templates()

    # Ensure output directory exists regardless of CWD
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate archetype comparison report (tournament)
    archetype_template = env.get_template("archetype_comparison.j2")
    archetype_html = archetype_template.render(
        arch_names=tournament_results["names"],
        arch_win_rates=tournament_results["win_rates"],
        arch_tie_rates=tournament_results["tie_rates"]
    )

    with open(output_dir / "archetype_comparison.html", "w") as f:
        f.write(archetype_html)

    # Generate hand testing report
    hand_template = env.get_template("hand_testing.j2")

    # Prepare data for hand testing template
    # Build rows from both pure (one-roll) and full-game stats
    rows = []
    for key, full in hand_test_results.items():
        pure = pure_results.get(key, {"win_rate": 0, "tie_rate": 0})
        rows.append({
            "key": key,
            "name": str(full["special_faces"]),
            "pure_win": pure["win_rate"],
            "pure_tie": pure["tie_rate"],
            "full_win": full["win_rate"],
            "full_tie": full["tie_rate"],
            "net": full["avg_net_damage"]
        })
    # Sort by pure win+tie desc; tiebreaker by full net damage
    rows.sort(key=lambda r: (r["pure_win"] + r["pure_tie"], r["net"]), reverse=True)

    dice_names = [r["name"] for r in rows]
    pure_win_rates = [r["pure_win"] for r in rows]
    pure_tie_rates = [r["pure_tie"] for r in rows]
    win_rates = [r["full_win"] for r in rows]
    tie_rates = [r["full_tie"] for r in rows]
    net_damages = [r["net"] for r in rows]

    hand_html = hand_template.render(
        test_results=hand_test_results,
        performance_ranking=performance_ranking,
        dice_names=dice_names,
        pure_win_rates=pure_win_rates,
        pure_tie_rates=pure_tie_rates,
        win_rates=win_rates,
        tie_rates=tie_rates,
        net_damages=net_damages
    )

    with open(output_dir / "hand_testing.html", "w") as f:
        f.write(hand_html)

    print("📊 Reports generated:")
    print("  - output/archetype_comparison.html")
    print("  - output/hand_testing.html")


def main():
    """Main simulation runner"""
    print("🎲 Psycho-Dice-Namic Simulation Suite")
    print("=" * 50)

    # Run archetype pair sim (kept for console output) and tournament for report
    archetype_results = run_archetype_simulation()
    tournament_results = run_archetype_tournament()
    print()

    # Run hand testing
    hand_test_results, performance_ranking, pure_results = run_hand_testing()
    print()

    # Generate reports
    generate_reports(archetype_results, hand_test_results, performance_ranking, tournament_results, pure_results)

    print("✅ All simulations complete!")


if __name__ == "__main__":
    main()
