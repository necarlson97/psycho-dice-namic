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


class DefenseSimulator:
    """Simulates defense dice triggers across archetypes vs Tabula Rasa."""

    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine

    def _clone_with_defense(self, archetype: Archetype, defense_die, mode: str) -> Archetype:
        # Shallow clone by constructing a new Archetype with modified dice
        dice = [d for d in archetype.dice]
        # Replace first NormalDice with defense die only for psychological
        if mode == 'psychological':
            for i, d in enumerate(dice):
                if isinstance(d, NormalDice):
                    dice[i] = defense_die
                    break
        # For somatic, we don't insert into dice pool; we attach as attribute
        new_arch = Archetype(f"{archetype.name}+Def", dice)
        setattr(new_arch, "_somatic_defense_die", defense_die if mode == 'somatic' else None)
        setattr(new_arch, "_defense_mode", mode)
        return new_arch

    def _eval_triggers(self, defense_key: str, mode: str, debate_result, rounds_p1, rounds_p2) -> Tuple[int, int]:
        # Count triggers for player1 only (defense side). Return (triggers_total, rounds_count)
        import random
        triggers = 0
        round_count = len(rounds_p1)

        # helpers
        def any_six(vals):
            vals = vals or []
            return any(v == 6 for v in vals if isinstance(v, int) and v > 0)
        def no_six(vals):
            vals = vals or []
            return not any_six(vals)
        def only_odds(vals):
            vals = vals or []
            # If no valid ints, treat as False for only-odds checks
            filtered = [v for v in vals if isinstance(v,int) and v>0]
            return bool(filtered) and all((v % 2 == 1) for v in filtered)
        def only_evens(vals):
            vals = vals or []
            filtered = [v for v in vals if isinstance(v,int) and v>0]
            return bool(filtered) and all((v % 2 == 0) for v in filtered)

        # Per-round evaluation
        insults_committed_total = 0
        passive_counter = 0
        for idx, rr in enumerate(rounds_p1):
            insults_committed_total += rr.insults_banked_count

            if defense_key == 'Halo-Effect':
                if mode == 'psychological':
                    if any_six(rr.initial_live_values):
                        triggers += 1
                else:
                    if no_six(rr.initial_live_values):
                        triggers += 1

            elif defense_key == 'Scapegoat':
                if mode == 'psychological':
                    if rr.fumbled:
                        triggers += random.randint(1, 6)
                else:
                    if insults_committed_total >= 3:
                        triggers += 3
                        insults_committed_total = -9999  # only once

            elif defense_key == 'Normalcy':
                if mode == 'psychological':
                    if any(len(c.dice) == 2 and len(set(c.dice)) == 1 for c in rr.insults):
                        triggers += 1
                else:
                    if only_odds(rr.initial_live_values):
                        triggers += 1

            elif defense_key == 'Just-World':
                if mode == 'psychological':
                    if any(len(c.dice) >= 4 for c in rr.insults):
                        triggers += 1
                else:
                    if only_evens(rr.initial_live_values):
                        triggers += 1

            elif defense_key == 'Victimhood':
                if mode == 'psychological':
                    dmg = rr.damage_from_opponent
                    if dmg > 3:
                        if random.randint(1, 6) < dmg:
                            triggers += 3  # eureka
                else:
                    if debate_result.winner and rounds_p1 and debate_result.winner != rounds_p1[0].player_name and debate_result.winner != 'Tie':
                        triggers += 3

            elif defense_key == 'Dunning-Kruger':
                if mode == 'psychological':
                    if any(all(v == 1 for v in c.dice) for c in rr.insults):
                        triggers += 1
                else:
                    if rr.fumbled:
                        triggers += 4  # 1 fumble protect (count as 1) + 3 eureka

            elif defense_key == 'Mere-Exposure':
                if mode == 'psychological':
                    if any(1 in c.dice for c in rr.insults):
                        triggers += 1
                else:
                    for v in (rr.initial_live_values or []):
                        if v == 1:
                            passive_counter += 1
                            if passive_counter >= 6:
                                passive_counter = 0
                                triggers += 3

            elif defense_key == 'Egocentric':
                if mode == 'psychological':
                    if rr.damage_to_opponent == 1:
                        triggers += 1
                else:
                    # start of round triggers twice per debate passed
                    triggers += 2 * idx

            elif defense_key == 'Illusory-Control':
                # Approximate: not enough token tracking; leave minimal count 0 for now
                pass

            elif defense_key == 'Bandwagon':
                if mode == 'psychological':
                    # Count echo dice summoned this round (approximate)
                    triggers += getattr(rr, 'echo_summoned_count', 0) or 0
                else:
                    # Somatic has no trigger
                    pass

            elif defense_key == 'Narrative-Fallacy':
                if mode == 'psychological':
                    if any(self._is_straight(c.dice) for c in rr.insults):
                        triggers += 1
                else:
                    normals = [1,2,3,5,6]
                    vals = rr.initial_live_values or []
                    if vals and all((v in normals) for v in vals if isinstance(v,int) and v>0):
                        triggers += 1

        # Groupshift: debate-level conditions (banked counts and result)
        if defense_key == 'Groupshift' and rounds_p1:
            total_banked = sum(r.insults_banked_count for r in rounds_p1)
            pname = rounds_p1[0].player_name
            if mode == 'psychological':
                if total_banked >= 5 and debate_result.winner and debate_result.winner != pname and debate_result.winner != 'Tie':
                    triggers += 3  # eureka token proxy
            else:
                if total_banked <= 3 and debate_result.winner == pname:
                    triggers += 3  # breakthrough token proxy

        return triggers, round_count

    def _is_straight(self, dice: List[int]) -> bool:
        s = sorted(set(dice))
        if len(s) < 3:
            return False
        return all(s[i+1] == s[i] + 1 for i in range(len(s)-1))

    def simulate_defense(self, defense_key: str, defense_die, mode: str, archetypes: List[Archetype], num_matches: int = 500) -> Dict[str, Any]:
        results = {"defense": defense_key, "mode": mode, "win": 0, "tie": 0, "loss": 0, "triggers": 0, "rounds": 0}
        control = TabulaRasa()
        for base in archetypes:
            test_arch = self._clone_with_defense(base, defense_die, mode)
            for _ in range(num_matches):
                p1 = test_arch.create_player('P1')
                p2 = control.create_player('P2')
                debate = self.game_engine.play_debate(p1, test_arch, p2, control)
                if debate.winner == 'P1':
                    results['win'] += 1
                elif debate.winner == 'Tie':
                    results['tie'] += 1
                else:
                    results['loss'] += 1
                # split rounds
                r1 = [r for r in debate.rounds if r.player_name == 'P1']
                r2 = [r for r in debate.rounds if r.player_name == 'P2']
                trig, rc = self._eval_triggers(defense_key, mode, debate, r1, r2)
                results['triggers'] += trig
                results['rounds'] += rc
        total = results['win'] + results['loss'] + results['tie']
        results['win_rate'] = results['win'] / total if total else 0
        results['tie_rate'] = results['tie'] / total if total else 0
        results['triggers_per_game'] = results['triggers'] / total if total else 0
        results['triggers_per_round'] = results['triggers'] / results['rounds'] if results['rounds'] else 0
        return results


class SynergySimulator:
    """Keyword-based synergy simulator per spec: maintain player keyword set; pick new items maximizing shared keywords."""

    KEYWORDS = [
        'neurosis','regret','forgiveness','eureka','breakthrough','fumble','fumble-shield',
        'rehash','echo','reroll','heal','damage','steal','token','counter','odd','even',
        'straight','pair','bank','waxy','copy','shield','commit','fumble-protection','bust'
    ]

    # No static archetype keyword mapping; derive from dice properties only

    @staticmethod
    def extract_keywords(text: str) -> set:
        t = (text or '').lower()
        kws = set()
        for k in SynergySimulator.KEYWORDS:
            if k in t:
                kws.add(k)
        if 'fumble shield' in t or 'fumbleshield' in t:
            kws.add('fumble-shield')
        if 'echo die' in t or 'echo dice' in t:
            kws.add('echo')
        return kws

    def archetype_keywords(self, arch: Archetype) -> set:
        kws = set()
        for d in getattr(arch, 'dice', []):
            name = getattr(d, 'name', '')
            # derive odd/even from faces
            faces = getattr(d, 'faces', []) or []
            nums = [v for v in faces if isinstance(v, int)]
            if nums:
                odd_count = sum(1 for v in nums if v % 2 == 1)
                even_count = sum(1 for v in nums if v % 2 == 0)
                if even_count <= 1:
                    kws.add('odd')
                if odd_count <= 1:
                    kws.add('even')
        return kws

    def simulate(self, archetypes: List[Archetype], num_games: int = 100) -> Dict[str, float]:
        from emotions import EMOTION_DEFINITIONS
        from archetypes import DEFENSE_DICE_DESCRIPTIONS, DEFENSE_DICE_DEFINITIONS
        results: Dict[str, float] = {}
        defense_items = []
        for name, desc in DEFENSE_DICE_DESCRIPTIONS.items():
            text = (desc.get('psych','') + ' ' + desc.get('som',''))
            faces = DEFENSE_DICE_DEFINITIONS.get(name, [])
            nums = [v for v in faces if isinstance(v, int)]
            if nums:
                odd_count = sum(1 for v in nums if v % 2 == 1)
                even_count = sum(1 for v in nums if v % 2 == 0)
                if even_count <= 1:
                    text += ' odd'
                if odd_count <= 1:
                    text += ' even'
            defense_items.append((name, text))
        for arch in archetypes:
            total_synergies = 0
            for _ in range(num_games):
                current_keywords = set(self.archetype_keywords(arch))
                chosen_emotions = []
                chosen_dice = []
                chosen_emotion_keywords = []
                chosen_die_keywords = []
                for _p in range(3):
                    # draw 3 emotions, 3 dice
                    e_choices = random.sample(EMOTION_DEFINITIONS, k=min(3, len(EMOTION_DEFINITIONS)))
                    d_choices = random.sample(defense_items, k=min(3, len(defense_items)))
                    # compute best individual picks against current keywords
                    def overlap_score(tags: set) -> int:
                        return len(tags & current_keywords)
                    best_e = None; best_e_kws = set(); best_e_score = -1
                    e_with_kws = []
                    for e in e_choices:
                        ek = self.extract_keywords(e['markdown'])
                        e_with_kws.append((e, ek))
                        sc = overlap_score(ek)
                        if sc > best_e_score or (sc == best_e_score and len(ek) > len(best_e_kws)):
                            best_e = e; best_e_kws = ek; best_e_score = sc
                    best_d = None; best_d_kws = set(); best_d_score = -1
                    d_with_kws = []
                    for name, txt in d_choices:
                        dk = self.extract_keywords(txt)
                        d_with_kws.append(((name, txt), dk))
                        sc = overlap_score(dk)
                        if sc > best_d_score or (sc == best_d_score and len(dk) > len(best_d_kws)):
                            best_d = (name, txt); best_d_kws = dk; best_d_score = sc
                    # if zero overlap so far, pick the largest keyword sets to seed
                    if best_e_score <= 0:
                        best_e, best_e_kws = max(e_with_kws, key=lambda x: len(x[1]))
                    if best_d_score <= 0:
                        best_d, best_d_kws = max(d_with_kws, key=lambda x: len(x[1]))
                    # keep selections and grow keyword pool
                    chosen_emotions.append(best_e)
                    chosen_emotion_keywords.append(best_e_kws)
                    current_keywords |= best_e_kws
                    chosen_dice.append(best_d)
                    chosen_die_keywords.append(best_d_kws)
                    current_keywords |= best_d_kws
                # count cross pairs (emotion, die) that share any keyword
                game_synergies = 0
                for ek in chosen_emotion_keywords:
                    for dk in chosen_die_keywords:
                        if ek & dk:
                            game_synergies += 1
                total_synergies += game_synergies
            results[arch.name] = (total_synergies / num_games) if num_games else 0.0
        return results

class BiasEmotionSimulator:
    """Simulates archetypes augmented with psychological and somatic bias dice and emotions.
    - For each run: for a given archetype, select 2 psych defense dice (replace normals), 2 somatic defense dice (bench), and 2 emotions.
    - Play a debate vs a random opponent archetype; aggregate win/tie/loss stats by emotion, by bias die, and by archetype.
    - Detect potential infinite loops by capping rounds per debate.
    """

    def __init__(self, game_engine: GameEngine, max_rounds: int = 50):
        self.game_engine = game_engine
        self.max_rounds = max_rounds

    def _clone_with_bias(self, base: Archetype, psych_dice: List[Tuple[str, List[int]]]) -> Archetype:
        from archetypes import SpecialFaceDice
        # replace two Normal dice with provided SpecialFaceDice
        normal_indices = [i for i, d in enumerate(base.dice) if getattr(d, 'name', '') == 'Normal']
        dice_copy = [d for d in base.dice]
        replace_slots = normal_indices[:len(psych_dice)]
        for slot, (name, faces) in zip(replace_slots, psych_dice):
            dice_copy[slot] = SpecialFaceDice(faces, name)
        class TempArch(Archetype):
            def __init__(self, name: str, dice):
                super().__init__(name, dice)
        return TempArch(base.name, dice_copy)

    def simulate(self, archetypes: List[Archetype], num_games_per_arch: int = 200) -> Dict[str, Any]:
        from emotions import EMOTION_DEFINITIONS
        from emotions_runtime import create_emotions
        from archetypes import DEFENSE_DICE_DEFINITIONS

        emotion_names = [e['name'] for e in EMOTION_DEFINITIONS]
        defense_list = list(DEFENSE_DICE_DEFINITIONS.items())

        emotion_stats: Dict[str, Dict[str, int]] = {}
        bias_stats: Dict[str, Dict[str, int]] = {}
        arch_stats: Dict[str, Dict[str, int]] = {}
        pair_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        loop_loadouts: Dict[str, int] = {}

        names = [a.name for a in archetypes]

        def rec_stats(d: Dict[str, Dict[str, int]], key: str, outcome: str):
            s = d.setdefault(key, {"win": 0, "loss": 0, "tie": 0, "games": 0})
            s[outcome] += 1
            s["games"] += 1

        for arch in archetypes:
            for _ in range(num_games_per_arch):
                # sample two psych dice and two somatic dice; two emotions
                psych = random.sample(defense_list, k=2)
                som = random.sample(defense_list, k=2)
                emos = random.sample(emotion_names, k=2) if len(emotion_names) >= 2 else emotion_names
                # create augmented archetype
                aug = self._clone_with_bias(arch, psych)
                # choose opponent randomly
                opp_base = random.choice([a for a in archetypes if a.name != arch.name])
                p1 = aug.create_player('P1')
                p2 = opp_base.create_player('P2')
                # metadata attach (not used by engine yet)
                p1.bias_psych = [n for n, _ in psych]  # type: ignore
                p1.bias_somatic = [n for n, _ in som]  # type: ignore
                p1.emotions = create_emotions(emos)  # type: ignore

                debate = self.game_engine.play_debate(p1, aug, p2, opp_base, max_rounds=self.max_rounds)  # type: ignore

                # Determine outcome
                if debate.winner == 'P1':
                    outcome = 'win'
                elif debate.winner == 'Tie':
                    outcome = 'tie'
                else:
                    outcome = 'loss'

                # loop detection
                looped = False
                if hasattr(debate, 'rounds') and len(debate.rounds) >= self.max_rounds:
                    looped = True
                    key = f"{arch.name}|psych:{'+'.join([n for n,_ in psych])}|som:{'+'.join([n for n,_ in som])}|emo:{'+'.join(emos)}"
                    loop_loadouts[key] = loop_loadouts.get(key, 0) + 1

                # aggregate stats
                arch_key = arch.name
                rec_stats(arch_stats, arch_key, outcome)
                for en in emos:
                    rec_stats(emotion_stats, en, outcome)
                for (bn, _faces) in psych:
                    rec_stats(bias_stats, bn, outcome)
                # pairings
                # emotion+emotion
                if len(emos) == 2:
                    tkey = tuple(sorted(emos))
                    rec_stats(pair_counts, f"emotion|{tkey[0]}+{tkey[1]}", outcome)  # type: ignore
                # bias+bias
                bpair = tuple(sorted([bn for bn,_ in psych]))
                rec_stats(pair_counts, f"bias|{bpair[0]}+{bpair[1]}", outcome)  # type: ignore
                # arch+emotion
                for en in emos:
                    rec_stats(pair_counts, f"arch_emotion|{arch.name}+{en}", outcome)
                # bias+emotion
                for bn,_ in psych:
                    for en in emos:
                        rec_stats(pair_counts, f"bias_emotion|{bn}+{en}", outcome)

        # compute summaries
        def summarize(d: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
            out: Dict[str, Dict[str, float]] = {}
            for k, v in d.items():
                games = max(1, v.get('games', 0))
                out[k] = {
                    'win_rate': v.get('win', 0) / games,
                    'tie_rate': v.get('tie', 0) / games,
                    'games': float(games),
                }
            return out

        return {
            'emotion_stats': summarize(emotion_stats),
            'bias_stats': summarize(bias_stats),
            'archetype_stats': summarize(arch_stats),
            'pair_stats': summarize(pair_counts),
            'loops': loop_loadouts,
        }

    def keyword_frequencies(self, archetypes: List[Archetype], num_games: int = 100) -> Dict[str, float]:
        from emotions import EMOTION_DEFINITIONS
        from archetypes import DEFENSE_DICE_DESCRIPTIONS, DEFENSE_DICE_DEFINITIONS
        freq: Dict[str, int] = {k: 0 for k in self.KEYWORDS}
        total_overlaps = 0
        defense_items = []
        for name, desc in DEFENSE_DICE_DESCRIPTIONS.items():
            text = (desc.get('psych','') + ' ' + desc.get('som',''))
            faces = DEFENSE_DICE_DEFINITIONS.get(name, [])
            nums = [v for v in faces if isinstance(v, int)]
            if nums:
                odd_count = sum(1 for v in nums if v % 2 == 1)
                even_count = sum(1 for v in nums if v % 2 == 0)
                if even_count <= 1:
                    text += ' odd'
                if odd_count <= 1:
                    text += ' even'
            defense_items.append((name, text))
        for arch in archetypes:
            for _ in range(num_games):
                current_keywords = set(self.archetype_keywords(arch))
                chosen_emotion_keywords = []
                chosen_die_keywords = []
                for _p in range(3):
                    e_choices = random.sample(EMOTION_DEFINITIONS, k=min(3, len(EMOTION_DEFINITIONS)))
                    d_choices = random.sample(defense_items, k=min(3, len(defense_items)))
                    def overlap_score(tags: set) -> int:
                        return len(tags & current_keywords)
                    # best emotion
                    e_with_kws = [(e, self.extract_keywords(e['markdown'])) for e in e_choices]
                    best_e, best_e_kws = max(e_with_kws, key=lambda x: (overlap_score(x[1]), len(x[1])))
                    if overlap_score(best_e_kws) <= 0:
                        best_e, best_e_kws = max(e_with_kws, key=lambda x: len(x[1]))
                    chosen_emotion_keywords.append(best_e_kws)
                    current_keywords |= best_e_kws
                    # best die
                    d_with_kws = [((name, txt), self.extract_keywords(txt)) for name, txt in d_choices]
                    best_d, best_d_kws = max(d_with_kws, key=lambda x: (overlap_score(x[1]), len(x[1])))
                    if overlap_score(best_d_kws) <= 0:
                        best_d, best_d_kws = max(d_with_kws, key=lambda x: len(x[1]))
                    chosen_die_keywords.append(best_d_kws)
                    current_keywords |= best_d_kws
                # accumulate overlaps
                for ek in chosen_emotion_keywords:
                    for dk in chosen_die_keywords:
                        inter = ek & dk
                        if inter:
                            total_overlaps += 1
                            for kw in inter:
                                freq[kw] = freq.get(kw, 0) + 1
        if total_overlaps == 0:
            return {k: 0.0 for k in freq}
        return {k: (v / total_overlaps) for k, v in freq.items()}
