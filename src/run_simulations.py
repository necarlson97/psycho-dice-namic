#!/usr/bin/env python3
"""
Main simulation runner for Psycho-Dice-Namic
"""

import os
import sys
import json
import argparse
try:
    import yaml  # type: ignore
    HAS_YAML = True
except Exception:
    yaml = None
    HAS_YAML = False
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import re

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_engine import GameEngine
from archetypes import (
    TabulaRasa,
    Hedonist,
    Physiognomist,
    Rationalist,
    Fatalist,
    Transcendentalist,
    Puritan,
    Machiavalian,
    Absurdist,
    Stoic,
    Nihilist,
)
from simulators import ArchetypeSimulator, HandTester, DefenseSimulator
from simulators import SynergySimulator, BiasEmotionSimulator


def setup_templates():
    """Setup Jinja2 environment"""
    template_dir = Path(__file__).parent.parent / "templates"
    return Environment(loader=FileSystemLoader(template_dir))


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip('-')
    return s


def asset_filename_from_title(title: str) -> str:
    """Return lowercase-with-spaces filename for assets, with known corrections."""
    base = title.strip().lower()
    # Known filename corrections for uploaded assets
    corrections = {
        "the machiavalian": "the machiavellian",
        "the transcendentalist": "the transendentalist",
    }
    normalized = corrections.get(base, base)
    return f"{normalized}.svg"


def ensure_output_dir() -> Path:
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_data(basename: str, data: dict) -> Path:
    output_dir = ensure_output_dir()
    if HAS_YAML:
        path = output_dir / f"{basename}.yaml"
        with open(path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)
        return path
    else:
        path = output_dir / f"{basename}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path


def load_data(basename: str) -> dict:
    output_dir = ensure_output_dir()
    ypath = output_dir / f"{basename}.yaml"
    jpath = output_dir / f"{basename}.json"
    if ypath.exists() and HAS_YAML:
        with open(ypath) as f:
            return yaml.safe_load(f) or {}
    if jpath.exists():
        with open(jpath) as f:
            return json.load(f)
    return {}


def build_card_data_archetypes() -> list:
    archs = [
        TabulaRasa(), Hedonist(), Physiognomist(), Rationalist(), Fatalist(),
        Transcendentalist(), Puritan(), Machiavalian(), Absurdist(), Stoic(), Nihilist()
    ]
    # Special dice -> rule text mapping
    DIE_RULE_TEXT = {
        "Bliss": "On rolling a 6, immediately heal 1.",
        "Comedown": "On rolling a 6, immediately take 1 damage. You may take forgiveness tokens instead of healing.",
        "High-Minded": "If a banked insult contains a 6, add one echo die to that insult, as a 6.",
        "Spite": "On rolling a 6, immediately deal 1 damage to an opponent.",
        "Inebriation": "On rolling a 6, you may take 1 Regret to give 1 Neurosis to an opponent.",
        "Grounded": "When banked as part of a one-pair, add one echo die to that insult, as a 1.",
        "Nostalgia": "When banking, create an echo die that persists to the next roll with the same value.",
        "Penance": "If this die is banked as a 4+, for this debate, damage from or to you is doubled.",
        "Acedic": "On a 6: heal 1; if you have 0 Regret, gain 1 Regret.",
        "Pilfer": "If both Pilfer dice roll 6, at the start of next round steal an opponent's die for that round.",
        "Catastrophize": "If you roll a 1, you fumble; if you bank a 6, gain fumble-protection.",
        "Aporic": "If you roll a 1, you fumble; if you bank a 6, gain fumble-protection.",
        "Ridicule": "On 6: if you have 0 Regret, gain 1; else transfer 1 Regret to opponent.",
        "Nausea": "On 6: if you have 0 Regret, gain 1; else transfer 1 Regret to opponent.",
        "Apathetic": "If banked, gain 2 health.",
        "Abyssal": "After banking an insult, add this die to it copying the insult's highest die value.",
        "Choleric": "Yellow humor die.",
        "Melancholic": "Gray humor die.",
        "Phlegmatic": "Green humor die.",
        "Sanguine": "Red humor die.",
    }

    def rules_for_archetype(a) -> str:
        # Count dice by name, preserving encounter order
        order = []
        counts = {}
        for d in a.dice:
            n = getattr(d, 'name', 'Dice')
            counts[n] = counts.get(n, 0) + 1
            if n not in order:
                order.append(n)

        # Format lines like: "1x Bliss Die:" then its rule; and include Normal Dice without rules text
        def display_label(name: str, count: int) -> str:
            # Always use "Die" for singular, "Dice" for plural
            suffix = "Die" if count == 1 else "Dice"
            # Normal should always be "Normal Dice"
            if name == "Normal":
                return f"{count}x Normal Dice"
            return f"{count}x {name} {suffix}"

        lines = []
        for n in order:
            c = counts[n]
            # Header line
            header = display_label(n, c)
            if n != "Normal":
                header += ":"
            lines.append(f"<b>{header}</b>")
            # Rule line (if any and not Normal)
            if n != "Normal":
                rule = DIE_RULE_TEXT.get(n, "")
                if rule:
                    lines.append(rule)

        return "<br>".join(lines)

    cards = []
    for a in archs:
        rules = rules_for_archetype(a)
        cards.append({
            "name": a.name,
            "subtitle": "Archetype",
            "type": "archetype",
            "rules_html": rules,
            "quote": "",
            "image_src": f"../assets/{asset_filename_from_title(a.name)}"
        })
    return cards


def build_card_data_defense() -> list:
    from archetypes import DEFENSE_DICE_DEFINITIONS, DEFENSE_DICE_DESCRIPTIONS
    cards = []
    for name, faces in DEFENSE_DICE_DEFINITIONS.items():
        desc = DEFENSE_DICE_DESCRIPTIONS.get(name, {"subtitle": "Defense Die", "psych": "", "som": ""})
        rules = f"<b>Psychological:</b> {desc['psych']}<br><b>Somatic:</b> {desc['som']}<br><br><small>Faces: {faces}</small>"
        cards.append({
            "name": name,
            "subtitle": desc.get("subtitle", "Defense Die"),
            "type": "defense",
            "rules_html": rules,
            "quote": "",
            "image_src": f"../assets/{slugify(name)}.svg"
        })
    return cards


def build_card_data_emotions() -> list:
    # Build printable cards for emotions from markdown
    from emotions import EMOTION_DEFINITIONS

    def md_to_html(md: str) -> str:
        # Lightweight markdown to HTML for card bodies
        html = md.strip()
        # Bold **x**
        html = html.replace('**', '<b>').replace('<b><b>', '</b>').replace('</b><b>', '</b><b>')
        # Italic _x_
        # naive: replace underscores around words with <i>
        import re
        html = re.sub(r"_(.*?)_", r"<i>\1</i>", html)
        # Newlines to <br>
        html = html.replace("\r\n", "\n").replace("\n\n", "\n\n").replace("\n", "<br>")
        return html

    cards = []
    for e in EMOTION_DEFINITIONS:
        cards.append({
            "name": e["name"],
            "subtitle": "Emotion",
            "type": "emotion",
            "rules_html": md_to_html(e["markdown"]),
            "quote": "",
            "image_src": f"../assets/{slugify(e['name'])}.svg",
        })
    return cards


def run_archetype_simulation():
    """Run archetype vs archetype simulation"""
    print("🎲 Running Archetype vs Archetype Simulation...")

    game_engine = GameEngine()
    simulator = ArchetypeSimulator(game_engine)

    # Create archetypes
    tabula_rasa = TabulaRasa()
    euphoria = Hedonist()

    # Run simulation
    results = simulator.simulate_matches(tabula_rasa, euphoria, num_matches=5000)

    print(f"Results: {results['archetype1']} vs {results['archetype2']}")
    print(f"Win rates: {results['win_rate1']:.1%} vs {results['win_rate2']:.1%}")
    print(f"Ties: {results['tie_rate']:.1%}")
    print(f"Average rounds: {results['avg_rounds']:.1f}")

    save_data("archetypes_testing_pair", results)
    return results
def run_archetype_tournament():
    """Run a tournament across all archetypes and aggregate win/tie rates per archetype"""
    print("🎲 Running Archetype Tournament...")

    game_engine = GameEngine()
    simulator = ArchetypeSimulator(game_engine)

    archetypes = [
        TabulaRasa(), Hedonist(), Physiognomist(), Rationalist(), Fatalist(),
        Transcendentalist(), Puritan(), Machiavalian(), Absurdist(), Stoic(), Nihilist()
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

    results = {
        "names": sorted_names,
        "win_rates": win_rates,
        "tie_rates": tie_rates,
        "arch_stats": arch_stats,
    }
    save_data("archetypes_testing_tournament", results)
    return results



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

    combined = {
        "test_results": test_results,
        "performance_ranking": performance_ranking,
        "pure_results": pure_results,
    }
    save_data("hand_testing", combined)
    return test_results, performance_ranking, pure_results


def run_defense_testing():
    print("🎲 Running Defense Dice Testing...")
    game_engine = GameEngine()
    sim = DefenseSimulator(game_engine)

    # Build archetype list
    archetypes = [
        TabulaRasa(), Hedonist(), Physiognomist(), Rationalist(), Fatalist(),
        Transcendentalist(), Puritan(), Machiavalian(), Absurdist(), Stoic(), Nihilist()
    ]

    # Import defense definitions and SpecialFaceDice
    from archetypes import DEFENSE_DICE_DEFINITIONS
    from archetypes import SpecialFaceDice

    results = {}
    for name, faces in DEFENSE_DICE_DEFINITIONS.items():
        print(f"Testing defense die: {name} {faces}")
        # psychological
        d_die = SpecialFaceDice(faces, name)
        psych = sim.simulate_defense(name, d_die, 'psychological', archetypes, num_matches=500)
        # somatic
        d_die2 = SpecialFaceDice(faces, name)
        som = sim.simulate_defense(name, d_die2, 'somatic', archetypes, num_matches=500)
        results[name] = {"psychological": psych, "somatic": som}

    return results


def run_synergy_testing():
    print("🎲 Running Synergy Testing...")
    game_engine = GameEngine()
    # engine not needed, but keeping structure consistent
    archs = [
        TabulaRasa(), Hedonist(), Physiognomist(), Rationalist(), Fatalist(),
        Transcendentalist(), Puritan(), Machiavalian(), Absurdist(), Stoic(), Nihilist()
    ]
    sim = SynergySimulator()
    averages = sim.simulate(archs, num_games=1000)
    keyword_freq = sim.keyword_frequencies(archs, num_games=1000)
    # Print summary sorted by avg synergies desc
    print("Synergy Averages (per game):")
    for name, val in sorted(averages.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  - {name}: {val:.3f}")
    # Print keyword distribution
    print("Synergy Keyword Representation (share of overlaps):")
    for k, v in sorted(keyword_freq.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  - {k}: {v:.3f}")
    payload = {"averages": averages, "keyword_freq": keyword_freq}
    save_data("synergy_testing", payload)
    return averages, keyword_freq


def run_bias_emotion_testing():
    print("🎲 Running Bias + Emotion Testing...")
    game_engine = GameEngine()
    archs = [
        TabulaRasa(), Hedonist(), Physiognomist(), Rationalist(), Fatalist(),
        Transcendentalist(), Puritan(), Machiavalian(), Absurdist(), Stoic(), Nihilist()
    ]
    sim = BiasEmotionSimulator(game_engine)
    results = sim.simulate(archs, num_games_per_arch=1000)
    save_data("bias_emotion_testing", results)
    return results


def generate_reports(archetype_results, hand_test_results, performance_ranking, tournament_results, pure_results, defense_results, synergy_avgs, synergy_keyword_freq, bias_emotion_results):
    """Generate HTML reports using Jinja2 templates"""
    print("📊 Generating Reports...")

    env = setup_templates()

    # Ensure output directory exists regardless of CWD
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate archetype comparison report (tournament) if available
    if isinstance(tournament_results, dict) and "names" in tournament_results:
        archetype_template = env.get_template("archetypes_testing.j2")
        # Synergy data aligned to tournament names order
        synergy_values = [synergy_avgs.get(n, 0) for n in tournament_results["names"]]
        # Prepare keyword chart (top 20)
        # Filter out very generic keywords from chart
        kw_filtered = [(k, v) for k, v in synergy_keyword_freq.items() if k not in {'token', 'bank'}]
        kw_sorted = sorted(kw_filtered, key=lambda kv: kv[1], reverse=True)
        kw_top = kw_sorted[:20]
        kw_names = [k for k, _ in kw_top]
        kw_vals = [v for _, v in kw_top]

        archetype_html = archetype_template.render(
            arch_names=tournament_results["names"],
            arch_win_rates=tournament_results["win_rates"],
            arch_tie_rates=tournament_results["tie_rates"],
            arch_synergies=synergy_values,
            synergy_keyword_names=kw_names,
            synergy_keyword_values=kw_vals
        )

        with open(output_dir / "archetypes_testing.html", "w") as f:
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

    # Defense testing report (only if results available)
    if isinstance(defense_results, dict) and defense_results and all(isinstance(v, dict) for v in defense_results.values()):
        defense_template = env.get_template("defense_testing.j2")
        d_names = list(defense_results.keys())
        d_names.sort(key=lambda n: defense_results[n]["psychological"].get("triggers_per_game", 0), reverse=True)
        psych_win = [defense_results[n]["psychological"]["win_rate"] for n in d_names]
        psych_tie = [defense_results[n]["psychological"]["tie_rate"] for n in d_names]
        som_win = [defense_results[n]["somatic"]["win_rate"] for n in d_names]
        som_tie = [defense_results[n]["somatic"]["tie_rate"] for n in d_names]
        trig_game_psych = [defense_results[n]["psychological"].get("triggers_per_game", 0) for n in d_names]
        trig_game_som = [defense_results[n]["somatic"].get("triggers_per_game", 0) for n in d_names]
        trig_round_psych = [defense_results[n]["psychological"].get("triggers_per_round", 0) for n in d_names]
        trig_round_som = [defense_results[n]["somatic"].get("triggers_per_round", 0) for n in d_names]
        defense_html = defense_template.render(
            names=d_names,
            psych_win=psych_win,
            psych_tie=psych_tie,
            som_win=som_win,
            som_tie=som_tie,
            triggers_per_game_psych=trig_game_psych,
            triggers_per_game_som=trig_game_som,
            triggers_per_round_psych=trig_round_psych,
            triggers_per_round_som=trig_round_som
        )
        with open(output_dir / "defense_testing.html", "w") as f:
            f.write(defense_html)

    # Ensure assets dir exists for images (relative path used by HTML)
    assets_dir = project_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Generate printable cards
    cards_template = env.get_template("cards_print.j2")
    arch_cards = build_card_data_archetypes()
    def_cards = build_card_data_defense()
    emo_cards = build_card_data_emotions()

    with open(output_dir / "archetypes_print.html", "w") as f:
        f.write(cards_template.render(title="Archetype Cards", cards=arch_cards))
    with open(output_dir / "defense_print.html", "w") as f:
        f.write(cards_template.render(title="Defense Dice Cards", cards=def_cards))
    with open(output_dir / "emotions_print.html", "w") as f:
        f.write(cards_template.render(title="Emotion Cards", cards=emo_cards))

    # Bias + Emotion testing report
    bet = env.get_template("bias_emotion_testing.j2")
    # Prepare stats arrays
    def to_stacked_arrays_sorted(stat_map):
        items = list(stat_map.items())
        items.sort(key=lambda kv: (kv[1].get('win_rate',0) + kv[1].get('tie_rate',0), kv[0]), reverse=True)
        names = [k for k,_ in items]
        win = [v.get('win_rate', 0) for _,v in items]
        tie = [v.get('tie_rate', 0) for _,v in items]
        return names, win, tie
    emotion_names, emotion_win, emotion_tie = to_stacked_arrays_sorted(bias_emotion_results.get('emotion_stats', {}))
    bias_names, bias_win, bias_tie = to_stacked_arrays_sorted(bias_emotion_results.get('bias_stats', {}))
    arch_names2, arch_win, arch_tie = to_stacked_arrays_sorted(bias_emotion_results.get('archetype_stats', {}))
    # Top 30 pairings by win+tie
    pairs = bias_emotion_results.get('pair_stats', {})
    pair_sorted = sorted(pairs.items(), key=lambda kv: (kv[1].get('win_rate', 0)+kv[1].get('tie_rate',0)), reverse=True)[:30]
    pair_names = [k for k,_ in pair_sorted]
    pair_win = [v.get('win_rate',0) for _,v in pair_sorted]
    pair_tie = [v.get('tie_rate',0) for _,v in pair_sorted]
    loops = bias_emotion_results.get('loops', {})
    loop_labels = list(loops.keys())
    loop_counts = [loops[k] for k in loop_labels]
    with open(output_dir / "bias_emotion_testing.html", "w") as f:
        f.write(bet.render(
            emotion_names=emotion_names,
            emotion_win=emotion_win,
            emotion_tie=emotion_tie,
            bias_names=bias_names,
            bias_win=bias_win,
            bias_tie=bias_tie,
            arch_names=arch_names2,
            arch_win=arch_win,
            arch_tie=arch_tie,
            pair_names=pair_names,
            pair_win=pair_win,
            pair_tie=pair_tie,
            loop_labels=loop_labels,
            loop_counts=loop_counts,
        ))

    print("📊 Reports generated:")
    print("  - output/archetypes_testing.html")
    print("  - output/hand_testing.html")
    print("  - output/defense_testing.html")
    print("  - output/archetypes_print.html")
    print("  - output/defense_print.html")
    print("  - output/emotions_print.html")


def main():
    """Main simulation runner"""
    parser = argparse.ArgumentParser(description="Psycho-Dice-Namic Simulation Suite")
    parser.add_argument("--run", nargs="*", default=[], help="Which tasks to run: archetypes hand defense synergy bias reports")
    parser.add_argument("--save-only", action="store_true", help="Run selected sims and save YAML, but do not generate reports")
    args = parser.parse_args()

    tasks = set([t.lower() for t in args.run])
    if not tasks:
        tasks = {"archetypes", "hand", "defense", "synergy", "reports"}

    print("🎲 Psycho-Dice-Namic Simulation Suite")
    print("=" * 50)

    archetype_results = None
    tournament_results = None
    hand_test_results = None
    performance_ranking = None
    pure_results = None
    defense_results = None
    synergy_avgs = None
    synergy_keyword_freq = None
    bias_emotion_results = None

    if "archetypes" in tasks:
        archetype_results = run_archetype_simulation()
        tournament_results = run_archetype_tournament()
        print()
    else:
        archetype_results = load_data("archetypes_testing_pair") or load_data("archetype_pair")
        tournament_results = load_data("archetypes_testing_tournament") or load_data("archetype_tournament")

    if "hand" in tasks:
        hand_test_results, performance_ranking, pure_results = run_hand_testing()
        print()
    else:
        hand_payload = load_data("hand_testing")
        hand_test_results = hand_payload.get("test_results", {})
        performance_ranking = hand_payload.get("performance_ranking", [])
        pure_results = hand_payload.get("pure_results", {})

    if "defense" in tasks:
        defense_results = run_defense_testing()
        print()
    else:
        defense_results = load_data("defense_testing")

    if "synergy" in tasks:
        synergy_avgs, synergy_keyword_freq = run_synergy_testing()
    else:
        synergy_payload = load_data("synergy_testing") or load_data("synergy")
        synergy_avgs = synergy_payload.get("averages", {})
        synergy_keyword_freq = synergy_payload.get("keyword_freq", {})

    if "bias" in tasks:
        bias_emotion_results = run_bias_emotion_testing()
    else:
        bias_emotion_results = load_data("bias_emotion_testing") or load_data("bias_emotion")

    if "reports" in tasks and not args.save_only:
        generate_reports(
            archetype_results,
            hand_test_results,
            performance_ranking,
            tournament_results,
            pure_results,
            defense_results,
            synergy_avgs,
            synergy_keyword_freq,
            bias_emotion_results,
        )

    print("✅ All simulations complete!")


if __name__ == "__main__":
    main()
