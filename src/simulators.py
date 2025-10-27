"""
Simulation engines for Psycho-Dice-Namic
"""

from typing import List, Dict, Any, Tuple
import random
from collections import defaultdict, Counter
import statistics

from game_engine import GameEngine
from dice import NormalDice
from archetypes import SpecialFaceDice
from archetypes import Archetype, TabulaRasa, Euphoria, SPECIAL_DICE_DEFINITIONS, create_special_dice, Player, MAX_HEALTH


class ArchetypeSimulator:
    """Simulates archetype vs archetype matches"""

    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine

    def simulate_matches(self, archetype1: Archetype, archetype2: Archetype,
                        num_matches: int = 1000) -> Dict[str, Any]:
        """Simulate multiple matches between two archetypes"""
        results = {
            "archetype1": archetype1.name,
            "archetype2": archetype2.name,
            "wins1": 0,
            "wins2": 0,
            "ties": 0,
            "total_rounds": 0,
            "health_differences": [],
            "match_details": []
        }

        for match_num in range(num_matches):
            # Create fresh players for each match
            player1 = archetype1.create_player(f"{archetype1.name}_Player")
            player2 = archetype2.create_player(f"{archetype2.name}_Player")

            # Play the debate
            debate_result = self.game_engine.play_debate(player1, archetype1, player2, archetype2)

            # Record results
            results["total_rounds"] += len(debate_result.rounds) // 2  # Two players per round
            results["health_differences"].append(
                debate_result.final_health[player1.name] - debate_result.final_health[player2.name]
            )

            if debate_result.winner == player1.name:
                results["wins1"] += 1
            elif debate_result.winner == player2.name:
                results["wins2"] += 1
            else:
                results["ties"] += 1

            # Store detailed match info (sample only)
            if match_num < 10:  # Store details for first 10 matches
                results["match_details"].append({
                    "match": match_num + 1,
                    "winner": debate_result.winner,
                    "final_health": debate_result.final_health,
                    "rounds": len(debate_result.rounds) // 2
                })

        # Calculate statistics
        results["win_rate1"] = results["wins1"] / num_matches
        results["win_rate2"] = results["wins2"] / num_matches
        results["tie_rate"] = results["ties"] / num_matches
        results["avg_rounds"] = results["total_rounds"] / num_matches
        results["avg_health_diff"] = statistics.mean(results["health_differences"])
        results["std_health_diff"] = statistics.stdev(results["health_differences"]) if len(results["health_differences"]) > 1 else 0

        return results

    def simulate_tournament(self, archetypes: List[Archetype],
                           matches_per_pair: int = 100) -> Dict[str, Any]:
        """Simulate a round-robin tournament between multiple archetypes"""
        results = {
            "archetypes": [arch.name for arch in archetypes],
            "match_results": {},
            "win_rates": {},
            "total_matches": 0
        }

        # Initialize results
        for arch in archetypes:
            results["win_rates"][arch.name] = 0
            results["match_results"][arch.name] = {}

        # Play all pairs
        for i, arch1 in enumerate(archetypes):
            for j, arch2 in enumerate(archetypes):
                if i < j:  # Avoid duplicate matches
                    match_result = self.simulate_matches(arch1, arch2, matches_per_pair)
                    results["match_results"][arch1.name][arch2.name] = match_result
                    results["match_results"][arch2.name][arch1.name] = {
                        "archetype1": arch2.name,
                        "archetype2": arch1.name,
                        "wins1": match_result["wins2"],
                        "wins2": match_result["wins1"],
                        "ties": match_result["ties"],
                        "win_rate1": match_result["win_rate2"],
                        "win_rate2": match_result["win_rate1"],
                        "tie_rate": match_result["tie_rate"]
                    }
                    results["total_matches"] += matches_per_pair

        # Calculate overall win rates
        for arch in archetypes:
            total_wins = 0
            total_matches = 0
            for other_arch in archetypes:
                if arch.name != other_arch.name:
                    if arch.name in results["match_results"] and other_arch.name in results["match_results"][arch.name]:
                        match_data = results["match_results"][arch.name][other_arch.name]
                        total_wins += match_data["wins1"]
                        total_matches += match_data["wins1"] + match_data["wins2"] + match_data["ties"]
            results["win_rates"][arch.name] = total_wins / total_matches if total_matches > 0 else 0

        return results


class HandTester:
    """Tests arbitrary hands against normal hands"""

    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine

    def test_special_dice(self, special_faces: List[int], num_tests: int = 1000) -> Dict[str, Any]:
        """Test a special dice against normal dice"""
        results = {
            "special_faces": special_faces,
            "damage_differences": [],
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "avg_damage_special": 0,
            "avg_damage_normal": 0,
            "max_damage_special": 0,
            "max_damage_normal": 0,
            "min_damage_special": float('inf'),
            "min_damage_normal": float('inf')
        }

        special_damages = []
        normal_damages = []
        debate_results = []

        for _ in range(num_tests):
            # Create test archetypes

            # Create 2 special dice with the given faces + 4 normal d6s
            special_dice = [SpecialFaceDice(special_faces, "Special"), SpecialFaceDice(special_faces, "Special")] + [NormalDice() for _ in range(4)]

            # Create archetypes
            special_archetype = Archetype("Special", special_dice)
            normal_archetype = TabulaRasa()

            # Create players
            special_player = Player("Special", health=MAX_HEALTH, dice=special_dice)
            normal_player = Player("Normal", health=MAX_HEALTH, dice=normal_archetype.dice)

            # Simulate the full debate
            debate_result = self.game_engine.play_debate(special_player, special_archetype, normal_player, normal_archetype)
            debate_results.append(debate_result)

            # Calculate damage from final health
            special_damage = MAX_HEALTH - normal_player.health
            normal_damage = MAX_HEALTH - special_player.health
            net_damage = special_damage - normal_damage

            special_damages.append(special_damage)
            normal_damages.append(normal_damage)
            results["damage_differences"].append(net_damage)

            if debate_result.winner == "Special":
                results["wins"] += 1
            elif debate_result.winner == "Normal":
                results["losses"] += 1
            else:
                results["ties"] += 1

        # Calculate statistics
        results["avg_damage_special"] = statistics.mean(special_damages)
        results["avg_damage_normal"] = statistics.mean(normal_damages)
        results["max_damage_special"] = max(special_damages)
        results["max_damage_normal"] = max(normal_damages)
        results["min_damage_special"] = min(special_damages)
        results["min_damage_normal"] = min(normal_damages)
        results["win_rate"] = results["wins"] / num_tests
        results["loss_rate"] = results["losses"] / num_tests
        results["tie_rate"] = results["ties"] / num_tests
        results["avg_net_damage"] = statistics.mean(results["damage_differences"])
        results["std_net_damage"] = statistics.stdev(results["damage_differences"]) if len(results["damage_differences"]) > 1 else 0

        return results

    def test_all_special_dice(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Test all predefined special dice"""
        results = {}

        for name, faces in SPECIAL_DICE_DEFINITIONS.items():
            print(f"Testing {name}: {faces}")
            results[name] = self.test_special_dice(faces, num_tests)

        return results

    def test_special_dice_pure(self, special_faces: List[int], num_tests: int = 1000) -> Dict[str, Any]:
        """Pure one-roll hand vs hand: 2x special + 4x normal vs 6x normal, no AI, no tokens."""
        results = {
            "special_faces": special_faces,
            "wins": 0,
            "losses": 0,
            "ties": 0,
        }

        import random
        for _ in range(num_tests):
            # Roll 2 special dice by choosing from faces (can include None)
            s1 = random.choice(special_faces)
            s2 = random.choice(special_faces)
            special_hand = [s1, s2] + [random.randint(1, 6) for _ in range(4)]
            normal_hand = [random.randint(1, 6) for _ in range(6)]

            match_result = self.game_engine.play_hand_vs_hand(special_hand, normal_hand)
            net = match_result["net_damage1"]
            if net > 0:
                results["wins"] += 1
            elif net < 0:
                results["losses"] += 1
            else:
                results["ties"] += 1

        results["win_rate"] = results["wins"] / num_tests
        results["tie_rate"] = results["ties"] / num_tests
        results["loss_rate"] = results["losses"] / num_tests
        return results

    def test_all_special_dice_pure(self, num_tests: int = 1000) -> Dict[str, Any]:
        """Pure one-roll for all predefined special dice"""
        results = {}
        for name, faces in SPECIAL_DICE_DEFINITIONS.items():
            results[name] = self.test_special_dice_pure(faces, num_tests)
        return results

    def compare_dice_performance(self, test_results: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Compare performance of different special dice.
        Sort by (win_rate + tie_rate) descending; ties broken by avg_net_damage.
        """
        performance = []

        for name, results in test_results.items():
            score = results["win_rate"] + results["tie_rate"] + (results["avg_net_damage"] / 1000)
            face_values = str(results["special_faces"])  # Display as faces array
            performance.append((face_values, score))

        return sorted(performance, key=lambda x: x[1], reverse=True)
