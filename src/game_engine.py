"""
Core game engine for Psycho-Dice-Namic
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import random

from dice import ComboDetector, Combo
from archetypes import Player, Archetype
from emotions_runtime import EmotionContext
from dice import HighMindedDice, GroundedDice, NostalgiaDice, PenanceDice, PhlegmaticDie, CholericDie, MelancholicDie, SanguineDie


@dataclass
class RoundResult:
    """Result of a single round"""
    player_name: str
    insults: List[Combo]
    fumbled: bool
    total_damage: int
    special_effects: Dict[str, Any]
    initial_live_values: List[int] = None
    insults_banked_count: int = 0
    damage_to_opponent: int = 0
    damage_from_opponent: int = 0
    echo_summoned_count: int = 0
    rolled_only_odds: bool = False
    rolled_only_evens: bool = False
    contained_any_one: bool = False


@dataclass
class DebateResult:
    """Result of a complete debate"""
    winner: str
    rounds: List[RoundResult]
    final_health: Dict[str, int]


class GameEngine:
    """Core game engine for Psycho-Dice-Namic"""

    def __init__(self):
        self.combo_detector = ComboDetector()

    def roll_dice(self, player: Player) -> List[int]:
        """Roll all of a player's dice"""
        results = []
        for dice in player.dice:
            if dice.can_roll():
                results.append(dice.roll())
            else:
                results.append(-1)  # Blank face
        return results

    def _roll_live_pool(self, player: Player, archetype: Archetype) -> Tuple[List[Tuple[int, object]], Dict[str, Any]]:
        """Roll dice, return live pool of (value, die_obj) and on-roll effects"""
        values = self.roll_dice(player)
        live_pool: List[Tuple[int, object]] = [(values[i], player.dice[i]) for i in range(len(values))]
        round_effects = archetype.apply_special_effects(player, [v for v, _ in live_pool])
        # Immediate effects
        if round_effects.get("heal", 0) > 0:
            player.heal(round_effects.get("heal", 0))
        if round_effects.get("damage", 0) > 0:
            player.take_damage(round_effects.get("damage", 0))
        if round_effects.get("forgiveness_tokens", 0) > 0:
            player.forgiveness_tokens += round_effects.get("forgiveness_tokens", 0)
        # Inject one-roll echoes if present, then clear the pending list
        if getattr(player, "pending_echo_values", None):
            for ev in player.pending_echo_values:
                live_pool.append((ev, None))
            player.pending_echo_values = []
        return live_pool, round_effects

    def _bank_from_live_pool(self, player: Player, archetype: Archetype, live_pool: List[Tuple[int, object]]) -> RoundResult:
        """Greedy banking with bank-time effects (HighMinded, Grounded, Nostalgia, Penance, Apathetic, Abyssal, humor commit)."""
        insults: List[Combo] = []
        insult_sources: List[List] = []
        special_effects: Dict[str, Any] = {"heal": 0, "damage": 0, "forgiveness_tokens": 0}
        # Build a mutable values list
        live_dice = [v for v, _ in live_pool]
        initial_values = live_dice.copy()
        used_abyssal = False
        # Banking loop
        while True:
            possible_combos = self.combo_detector.find_combos(live_dice)
            if not possible_combos or all(combo.name == "Slighting" and len(combo.dice) == 0 for combo in possible_combos):
                # Fumble via banking phase shouldn't happen since we only start when we have dice; treat as break
                break

            best_combo = max(possible_combos, key=lambda c: c.damage)
            used_sources: List[object] = []
            for die_value in best_combo.dice:
                idx = next((i for i, (v, dobj) in enumerate(live_pool) if v == die_value), None)
                if idx is not None:
                    _, dobj = live_pool.pop(idx)
                    used_sources.append(dobj)
                    if die_value in live_dice:
                        live_dice.remove(die_value)

            # Bank-time effects
            # Catastrophize/Aporic: if banked a 6, grant bust protection
            for dobj in used_sources:
                if getattr(dobj, "name", "") in ("Catastrophize", "Aporic") and getattr(dobj, "last_value", None) == 6:
                    player.bust_protection = True
            # High-minded raise
            from dice import HighMindedDice, GroundedDice, NostalgiaDice, PhlegmaticDie, PenanceDice
            if any(isinstance(d, HighMindedDice) and getattr(d, "last_value", None) == 6 for d in used_sources):
                if len(best_combo.dice) >= 1:
                    best_combo.dice.append(best_combo.dice[-1])
                    best_combo.damage = sum(best_combo.dice)
            # Grounded: if pair, add echo die of 1 into insult
            if len(best_combo.dice) == 2 and len(set(best_combo.dice)) == 1 and any(isinstance(d, GroundedDice) for d in used_sources):
                best_combo.dice.append(1)
                best_combo.damage = sum(best_combo.dice)
            # Penance: if any banked at value >=4, enable double damage for this debate for this player
            if any(isinstance(d, PenanceDice) and getattr(d, "last_value", 0) >= 4 for d in used_sources):
                player.penance_double_active = True
            # Apathetic: on bank, heal 2
            if any(getattr(d, "name", "") == "Apathetic" for d in used_sources):
                healed = player.heal(2)
                special_effects["heal"] = special_effects.get("heal", 0) + healed
            # Abyssal: after banking, add a copy of lowest die once per round
            if not used_abyssal and any(getattr(d, "name", "") == "Abyssal" for d in getattr(player, "dice", [])) and best_combo.dice:
                best_combo.dice.append(min(best_combo.dice))
                best_combo.damage = sum(best_combo.dice)
                used_abyssal = True
            # Nostalgia echo -> next roll only
            for i, dobj in enumerate(used_sources):
                if isinstance(dobj, NostalgiaDice):
                    echo_val = best_combo.dice[i] if i < len(best_combo.dice) else getattr(dobj, "last_value", 1)
                    if hasattr(player, "pending_echo_values"):
                        player.pending_echo_values.append(echo_val)

            insults.append(best_combo)
            insult_sources.append(used_sources)

            # Simple AI commit rule
            if len(insults) >= 2 or len(live_dice) < 4:
                break

        # Humor commit-time resolution (Temperance/Physiognomist)
        from archetypes import Temperance, Physiognomist
        if (isinstance(archetype, Temperance) or isinstance(archetype, Physiognomist)) and insult_sources:
            humor_sums = {"sanguine": 0, "phlegmatic": 0, "melancholic": 0, "choleric": 0}
            for combo, sources in zip(insults, insult_sources):
                for val, dobj in zip(combo.dice, sources + [None] * (len(combo.dice) - len(sources))):
                    if dobj is None:
                        continue
                    color = getattr(dobj, "color", None)
                    if color in ("red", "purple"):
                        humor_sums["sanguine"] += val
                    elif color in ("green", "blue"):
                        humor_sums["phlegmatic"] += val
                    elif color == "gray":
                        humor_sums["melancholic"] += val
                    elif color in ("yellow", "orange"):
                        humor_sums["choleric"] += val
            sorted_humors = sorted(humor_sums.items(), key=lambda kv: kv[1], reverse=True)
            top_value = sorted_humors[0][1] if sorted_humors else 0
            chosen = [h for h, v in sorted_humors if v == top_value][:2] if top_value > 0 else []
            for h in chosen:
                if h == "sanguine":
                    player.heal(1)
                elif h == "melancholic":
                    special_effects["opp_neurosis"] = special_effects.get("opp_neurosis", 0) + 1
                elif h == "phlegmatic":
                    # reroll one phlegmatic die value in-place
                    done = False
                    for ci, (combo, sources) in enumerate(zip(insults, insult_sources)):
                        for si, dobj in enumerate(sources):
                            if isinstance(dobj, PhlegmaticDie):
                                new_val = dobj.roll()
                                combo.dice[si] = new_val
                                combo.damage = sum(combo.dice)
                                done = True
                                break
                        if done:
                            break
                elif h == "choleric":
                    special_effects["opp_regret"] = special_effects.get("opp_regret", 0) + 2

        total_damage = sum(c.damage for c in insults)
        rr = RoundResult(
            player_name=player.name,
            insults=insults,
            fumbled=False,
            total_damage=total_damage,
            special_effects=special_effects,
            initial_live_values=initial_values,
            insults_banked_count=len(insults),
            echo_summoned_count=0,
            rolled_only_odds=all((v % 2 == 1) for v in initial_values if isinstance(v,int) and v>0),
            rolled_only_evens=all((v % 2 == 0) for v in initial_values if isinstance(v,int) and v>0),
            contained_any_one=any(v==1 for v in initial_values)
        )
        return rr

    def play_round(self, player: Player, archetype: Archetype) -> RoundResult:
        """Play a single round for a player"""
        insults: List[Combo] = []
        insult_sources: List[List] = []  # parallel to insults: list of die objects used per insult
        values = self.roll_dice(player)
        # Build live pool (value, die_obj). Echo dice will use die_obj=None
        live_pool: List[Tuple[int, object]] = [(values[i], player.dice[i]) for i in range(len(values))]
        live_dice = values.copy()
        special_effects: Dict[str, Any] = {"heal": 0, "damage": 0, "forgiveness_tokens": 0}

        while True:
            # Find all possible combos
            possible_combos = self.combo_detector.find_combos(live_dice)

            # If no combos possible, fumble
            if not possible_combos or all(combo.name == "Slighting" and len(combo.dice) == 0 for combo in possible_combos):
                # Apply regret tokens on fumble
                if player.regret_tokens > 0:
                    player.take_damage(player.regret_tokens)
                    player.regret_tokens = 0
                return RoundResult(
                    player_name=player.name,
                    insults=[],
                    fumbled=True,
                    total_damage=0,
                    special_effects=special_effects
                )

            # For now, always take the best combo (highest damage)
            best_combo = max(possible_combos, key=lambda c: c.damage)

            # Map combo dice to actual dice objects and remove from pools
            used_sources: List[object] = []
            for die_value in best_combo.dice:
                # find first matching value in live_pool
                idx = next((i for i,(v,dobj) in enumerate(live_pool) if v == die_value), None)
                if idx is not None:
                    val, dobj = live_pool.pop(idx)
                    used_sources.append(dobj)
                    # remove one occurrence from live_dice
                    if die_value in live_dice:
                        live_dice.remove(die_value)

            # Bank-time effects
            # Catastrophize: if any Catastrophize die banked a 6, grant bust protection
            for dobj in used_sources:
                if getattr(dobj, "name", "") == "Catastrophize" and getattr(dobj, "last_value", None) == 6:
                    player.bust_protection = True
            # High-minded: if a 6 from HighMinded die was banked, raise group by adding another same value
            if any(isinstance(d, HighMindedDice) and getattr(d, "last_value", None) == 6 for d in used_sources):
                if len(best_combo.dice) >= 1:
                    best_combo.dice.append(best_combo.dice[-1])
                    best_combo.damage = sum(best_combo.dice)
            # Simpleton: if combo is a pair and includes Simpleton die, raise to triplet
            if len(best_combo.dice) == 2 and len(set(best_combo.dice)) == 1 and any(isinstance(d, SimpletonsDice) for d in used_sources):
                best_combo.dice.append(best_combo.dice[0])
                best_combo.damage = sum(best_combo.dice)
            # Nostalgia: create echo die of same value for each Nostalgia die used (persists to next selection)
            for i, dobj in enumerate(used_sources):
                if isinstance(dobj, NostalgiaDice):
                    echo_val = best_combo.dice[i] if i < len(best_combo.dice) else getattr(dobj, "last_value", 1)
                    live_pool.append((echo_val, None))
                    live_dice.append(echo_val)

            insults.append(best_combo)
            insult_sources.append(used_sources)

            # Add echo dice
            for _ in range(best_combo.echo_dice):
                live_dice.append(1)  # Echo dice are always 1s

            # Apply special effects from this roll
            round_effects = archetype.apply_special_effects(player, [v for v,_ in live_pool])
            # Immediate effects
            if round_effects.get("heal", 0) > 0:
                player.heal(round_effects.get("heal", 0))
            if round_effects.get("damage", 0) > 0:
                player.take_damage(round_effects.get("damage", 0))
            if round_effects.get("forgiveness_tokens", 0) > 0:
                player.forgiveness_tokens += round_effects.get("forgiveness_tokens", 0)
            # Acedic adds regret if healed on 6 and had 0 regret
            for k in ("opp_damage", "opp_neurosis", "self_regret", "force_fumble", "ridicule_six", "pilfer_six"):
                if round_effects.get(k):
                    special_effects[k] = special_effects.get(k, 0) + round_effects.get(k)

            # Simple AI: commit if we have good combos or few dice left
            # Commit when we have fewer than 4 live dice remaining
            if round_effects.get("force_fumble") and not getattr(player, "bust_protection", False):
                break
            if len(insults) >= 2 or len(live_dice) < 4:
                break

        # Temperance commit-time humor resolution
        from archetypes import Temperance
        if isinstance(archetype, Temperance) and insult_sources:
            humor_sums = {"sanguine":0, "phlegmatic":0, "melancholic":0, "choleric":0}
            # compute sums based on banked dice and their values
            for combo, sources in zip(insults, insult_sources):
                for val, dobj in zip(combo.dice, sources + [None]*(len(combo.dice)-len(sources))):
                    if dobj is None:
                        continue
                    color = getattr(dobj, "color", None)
                    if color in ("red", "purple"):
                        humor_sums["sanguine"] += val
                    elif color in ("green", "blue"):
                        humor_sums["phlegmatic"] += val
                    elif color == "gray":
                        humor_sums["melancholic"] += val
                    elif color in ("yellow", "orange"):
                        humor_sums["choleric"] += val
            # pick top humors
            sorted_humors = sorted(humor_sums.items(), key=lambda kv: kv[1], reverse=True)
            top_value = sorted_humors[0][1] if sorted_humors else 0
            chosen = [h for h,v in sorted_humors if v == top_value][:2] if top_value>0 else []
            for h in chosen:
                if h == "sanguine":
                    special_effects["heal"] = special_effects.get("heal",0) + 1
                    player.heal(1)
                elif h == "melancholic":
                    special_effects["opp_neurosis"] = special_effects.get("opp_neurosis",0) + 1
                elif h == "phlegmatic":
                    # reroll one phlegmatic die value in-place
                    done = False
                    for ci,(combo,sources) in enumerate(zip(insults, insult_sources)):
                        for si,dobj in enumerate(sources):
                            if isinstance(dobj, PhlegmaticDie):
                                new_val = dobj.roll()
                                combo.dice[si] = new_val
                                combo.damage = sum(combo.dice)
                                done = True
                                break
                        if done:
                            break
                elif h == "choleric":
                    special_effects["opp_regret"] = special_effects.get("opp_regret",0) + 2

        # Calculate total damage
        total_damage = sum(combo.damage for combo in insults)

        return RoundResult(
            player_name=player.name,
            insults=insults,
            fumbled=False,
            total_damage=total_damage,
            special_effects=special_effects
        )

    def calculate_damage(self, attacker_insults: List[Combo], defender_insults: List[Combo]) -> int:
        """Calculate damage after blocking using optimal greedy matching.
        Matches each smallest attacking die with the smallest defending die that can block it.
        """
        # Collect all attacking dice
        attacking_dice = []
        for insult in attacker_insults:
            attacking_dice.extend(insult.dice)

        # Collect all defending dice
        defending_dice = []
        for insult in defender_insults:
            defending_dice.extend(insult.dice)

        # Sort both lists ascending
        attacking_dice.sort()
        defending_dice.sort()

        # Two-pointer sweep to block attacks with the smallest sufficient defender
        unblocked_damage = 0
        i = 0  # index for attacking_dice
        j = 0  # index for defending_dice
        while i < len(attacking_dice):
            attack_die = attacking_dice[i]
            # Advance defender pointer until we find a defender that can block
            while j < len(defending_dice) and defending_dice[j] < attack_die:
                j += 1
            if j < len(defending_dice):
                # defender_dice[j] blocks attack_die; consume defender
                j += 1
            else:
                # No defender can block; add damage
                unblocked_damage += attack_die
            i += 1

        return unblocked_damage

    def play_debate(self, player1: Player, archetype1: Archetype,
                   player2: Player, archetype2: Archetype,
                   max_rounds: int = 5) -> DebateResult:
        """Play a complete debate between two players"""
        rounds = []

        # Emotion: debate start hooks
        for emo in (getattr(player1, 'emotions', []) or []):
            try:
                emo.on_debate_start(EmotionContext(self, player1, player2, 0, {}))
            except Exception:
                pass
        for emo in (getattr(player2, 'emotions', []) or []):
            try:
                emo.on_debate_start(EmotionContext(self, player2, player1, 0, {}))
            except Exception:
                pass

        for round_num in range(max_rounds):
            # Joint round: roll both, handle pilfer stealing, then bank
            pool1, effects1 = self._roll_live_pool(player1, archetype1)
            pool2, effects2 = self._roll_live_pool(player2, archetype2)

            # Emotion: after roll hooks
            for emo in (getattr(player1, 'emotions', []) or []):
                try:
                    emo.on_after_roll(EmotionContext(self, player1, player2, round_num, {"pool": pool1}))
                except Exception:
                    pass
            for emo in (getattr(player2, 'emotions', []) or []):
                try:
                    emo.on_after_roll(EmotionContext(self, player2, player1, round_num, {"pool": pool2}))
                except Exception:
                    pass

            # Catastrophize immediate bust
            fumble1 = bool(effects1.get("force_fumble") and not getattr(player1, "bust_protection", False))
            fumble2 = bool(effects2.get("force_fumble") and not getattr(player2, "bust_protection", False))

            # Pilfer: deferred steal from previous round at start of this round
            if getattr(player1, "pending_pilfer_next_round", False) and pool2:
                cands2 = [(i, v, d) for i, (v, d) in enumerate(pool2) if isinstance(v, int) and v > 0]
                if cands2:
                    idx, val, dobj = sorted(cands2, key=lambda x: x[1])[-1]
                    pool2.pop(idx)
                    pool1.append((val, dobj))
                player1.pending_pilfer_next_round = False
            if getattr(player2, "pending_pilfer_next_round", False) and pool1:
                cands1 = [(i, v, d) for i, (v, d) in enumerate(pool1) if isinstance(v, int) and v > 0]
                if cands1:
                    idx, val, dobj = sorted(cands1, key=lambda x: x[1])[-1]
                    pool1.pop(idx)
                    pool2.append((val, dobj))
                player2.pending_pilfer_next_round = False

            # Set up pending pilfer for next round if both pilfer dice rolled 6 this round
            if effects1.get("pilfer_six", 0) >= 2:
                player1.pending_pilfer_next_round = True
            if effects2.get("pilfer_six", 0) >= 2:
                player2.pending_pilfer_next_round = True

            if not fumble1:
                round1 = self._bank_from_live_pool(player1, archetype1, pool1)
            else:
                # Emotion: notify self/opponent fumble
                for emo in (getattr(player1, 'emotions', []) or []):
                    try:
                        emo.on_fumble(EmotionContext(self, player1, player2, round_num, {"self_fumbled": True}))
                    except Exception:
                        pass
                for emo in (getattr(player2, 'emotions', []) or []):
                    try:
                        emo.on_fumble(EmotionContext(self, player2, player1, round_num, {"opponent_fumbled": True}))
                    except Exception:
                        pass
                # Apply regret damage on fumble now
                if player1.regret_tokens > 0:
                    player1.take_damage(player1.regret_tokens)
                    player1.regret_tokens = 0
                round1 = RoundResult(
                    player_name=player1.name,
                    insults=[],
                    fumbled=True,
                    total_damage=0,
                    special_effects={},
                    initial_live_values=[],
                    insults_banked_count=0,
                    damage_to_opponent=0,
                    damage_from_opponent=0,
                    echo_summoned_count=0,
                    rolled_only_odds=False,
                    rolled_only_evens=False,
                    contained_any_one=False
                )

            if not fumble2:
                round2 = self._bank_from_live_pool(player2, archetype2, pool2)
            else:
                # Emotion: notify self/opponent fumble
                for emo in (getattr(player2, 'emotions', []) or []):
                    try:
                        emo.on_fumble(EmotionContext(self, player2, player1, round_num, {"self_fumbled": True}))
                    except Exception:
                        pass
                for emo in (getattr(player1, 'emotions', []) or []):
                    try:
                        emo.on_fumble(EmotionContext(self, player1, player2, round_num, {"opponent_fumbled": True}))
                    except Exception:
                        pass
                if player2.regret_tokens > 0:
                    player2.take_damage(player2.regret_tokens)
                    player2.regret_tokens = 0
                round2 = RoundResult(
                    player_name=player2.name,
                    insults=[],
                    fumbled=True,
                    total_damage=0,
                    special_effects={},
                    initial_live_values=[],
                    insults_banked_count=0,
                    damage_to_opponent=0,
                    damage_from_opponent=0,
                    echo_summoned_count=0,
                    rolled_only_odds=False,
                    rolled_only_evens=False,
                    contained_any_one=False
                )

            rounds.extend([round1, round2])

            # Apply special effects
            if round1.special_effects.get("heal", 0) > 0:
                player1.heal(round1.special_effects.get("heal", 0))
            if round1.special_effects.get("damage", 0) > 0:
                player1.take_damage(round1.special_effects.get("damage", 0))

            if round2.special_effects.get("heal", 0) > 0:
                player2.heal(round2.special_effects.get("heal", 0))
            if round2.special_effects.get("damage", 0) > 0:
                player2.take_damage(round2.special_effects.get("damage", 0))

            # Calculate damage exchange
            if not round1.fumbled and not round2.fumbled:
                damage1_to_2 = self.calculate_damage(round1.insults, round2.insults)
                damage2_to_1 = self.calculate_damage(round2.insults, round1.insults)
                # Penance: if active, double both directions for that player
                if getattr(player1, "penance_double_active", False):
                    damage1_to_2 *= 2
                    damage2_to_1 *= 2
                if getattr(player2, "penance_double_active", False):
                    damage1_to_2 *= 2
                    damage2_to_1 *= 2

                player2.take_damage(damage1_to_2)
                player1.take_damage(damage2_to_1)
                round1.damage_to_opponent = damage1_to_2
                round2.damage_from_opponent = damage1_to_2
                round2.damage_to_opponent = damage2_to_1
                round1.damage_from_opponent = damage2_to_1
            elif round1.fumbled and not round2.fumbled:
                # Only player2 attacks
                damage2_to_1 = self.calculate_damage(round2.insults, [])
                if getattr(player2, "penance_double_active", False):
                    damage2_to_1 *= 2
                player1.take_damage(damage2_to_1)
                damage1_to_2 = 0
                round2.damage_to_opponent = damage2_to_1
                round1.damage_from_opponent = damage2_to_1
            elif round2.fumbled and not round1.fumbled:
                damage1_to_2 = self.calculate_damage(round1.insults, [])
                if getattr(player1, "penance_double_active", False):
                    damage1_to_2 *= 2
                player2.take_damage(damage1_to_2)
                damage2_to_1 = 0
                round1.damage_to_opponent = damage1_to_2
                round2.damage_from_opponent = damage1_to_2
            else:
                damage1_to_2 = damage2_to_1 = 0

                # After clash token processing (neurosis and forgiveness)
                if round1.special_effects.get("opp_damage", 0) > 0:
                    player2.take_damage(round1.special_effects["opp_damage"])
                if round2.special_effects.get("opp_damage", 0) > 0:
                    player1.take_damage(round2.special_effects["opp_damage"])

                if round1.special_effects.get("opp_neurosis", 0) > 0:
                    player2.add_neurosis_tokens(round1.special_effects["opp_neurosis"])
                if round2.special_effects.get("opp_neurosis", 0) > 0:
                    player1.add_neurosis_tokens(round2.special_effects["opp_neurosis"])

                if player1.neurosis_tokens > 0:
                    player1.take_damage(1)
                    player1.neurosis_tokens = max(0, player1.neurosis_tokens - 1)
                if player2.neurosis_tokens > 0:
                    player2.take_damage(1)
                    player2.neurosis_tokens = max(0, player2.neurosis_tokens - 1)

                if round1.special_effects.get("self_regret", 0) > 0:
                    player1.add_regret_tokens(round1.special_effects["self_regret"])
                if round2.special_effects.get("self_regret", 0) > 0:
                    player2.add_regret_tokens(round2.special_effects["self_regret"])

                # Ridicule transfer: if player has regret, transfer to opp else gain one
                if round1.special_effects.get("ridicule_six"):
                    if player1.regret_tokens > 0:
                        player1.regret_tokens -= 1
                        player2.add_regret_tokens(1)
                    else:
                        player1.add_regret_tokens(1)
                if round2.special_effects.get("ridicule_six"):
                    if player2.regret_tokens > 0:
                        player2.regret_tokens -= 1
                        player1.add_regret_tokens(1)
                    else:
                        player2.add_regret_tokens(1)

                # Temperance choleric opp_regret from commit stage
                if round1.special_effects.get("opp_regret",0) > 0:
                    player2.add_regret_tokens(round1.special_effects["opp_regret"])
                if round2.special_effects.get("opp_regret",0) > 0:
                    player1.add_regret_tokens(round2.special_effects["opp_regret"])

                if player1.forgiveness_tokens > 0:
                    player1.heal(1)
                    player1.forgiveness_tokens = max(0, player1.forgiveness_tokens - 1)
                if player2.forgiveness_tokens > 0:
                    player2.heal(1)
                    player2.forgiveness_tokens = max(0, player2.forgiveness_tokens - 1)

            # Check for winner (handle simultaneous KO as tie)
            if player1.health <= 0 and player2.health <= 0:
                return DebateResult(
                    winner="Tie",
                    rounds=rounds,
                    final_health={player1.name: player1.health, player2.name: player2.health}
                )
            if player1.health <= 0:
                return DebateResult(
                    winner=player2.name,
                    rounds=rounds,
                    final_health={player1.name: player1.health, player2.name: player2.health}
                )
            if player2.health <= 0:
                return DebateResult(
                    winner=player1.name,
                    rounds=rounds,
                    final_health={player1.name: player1.health, player2.name: player2.health}
                )

        # Emotion: debate end hooks
        for emo in (getattr(player1, 'emotions', []) or []):
            try:
                emo.on_debate_end(EmotionContext(self, player1, player2, max_rounds, {}))
            except Exception:
                pass
        for emo in (getattr(player2, 'emotions', []) or []):
            try:
                emo.on_debate_end(EmotionContext(self, player2, player1, max_rounds, {}))
            except Exception:
                pass

        # Determine winner by health
        if player1.health > player2.health:
            winner = player1.name
        elif player2.health > player1.health:
            winner = player2.name
        else:
            winner = "Tie"

        # Clear per-debate tokens (neurosis and forgiveness) per rules
        player1.neurosis_tokens = 0
        player2.neurosis_tokens = 0
        player1.forgiveness_tokens = 0
        player2.forgiveness_tokens = 0

        return DebateResult(
            winner=winner,
            rounds=rounds,
            final_health={player1.name: player1.health, player2.name: player2.health}
        )

    def play_hand_vs_hand(self, hand1: List[int], hand2: List[int]) -> Dict[str, Any]:
        """Simulate a single hand vs hand comparison"""
        # Find combos for both hands
        combos1 = self.combo_detector.find_combos(hand1)
        combos2 = self.combo_detector.find_combos(hand2)

        # Calculate damage
        damage1_to_2 = self.calculate_damage(combos1, combos2)
        damage2_to_1 = self.calculate_damage(combos2, combos1)

        return {
            "hand1_combos": combos1,
            "hand2_combos": combos2,
            "damage1_to_2": damage1_to_2,
            "damage2_to_1": damage2_to_1,
            "net_damage1": damage1_to_2 - damage2_to_1,
            "net_damage2": damage2_to_1 - damage1_to_2
        }

