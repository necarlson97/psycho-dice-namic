"""
Dice system for Psycho-Dice-Namic
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import random


@dataclass
class Combo:
    """Represents a dice combination"""
    name: str
    dice: List[int]
    echo_dice: int = 0
    damage: int = 0

    def __post_init__(self):
        """Calculate damage based on dice values"""
        self.damage = sum(self.dice)


class Dice(ABC):
    """Abstract base class for dice"""

    def __init__(self, faces: List[int], name: str = "Dice"):
        self.faces = faces
        self.name = name
        self.last_value: Optional[int] = None

    def roll(self) -> int:
        """Roll the dice and return the result"""
        self.last_value = random.choice(self.faces)
        return self.last_value

    def can_roll(self) -> bool:
        """Check if this dice can be rolled (not blank)"""
        return True

    @abstractmethod
    def special_effect(self, value: int, player) -> Dict[str, Any]:
        """Apply special effects when this value is rolled"""
        pass


class NormalDice(Dice):
    """Standard d6"""

    def __init__(self):
        super().__init__([1, 2, 3, 4, 5, 6], "Normal")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class BlissDice(Dice):
    """Bliss Dice: 2, 3, 4, 5, 6, 6 - Heals on 6"""

    def __init__(self):
        super().__init__([2, 3, 4, 5, 6, 6], "Bliss")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"heal": 1}
        return {}


class ComedownDice(Dice):
    """Comedown Dice: 2, 2, 2, 4, 4, 6 - Damage on 6, forgiveness tokens"""

    def __init__(self):
        super().__init__([2, 2, 2, 4, 4, 6], "Comedown")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"damage": 1}
        return {}


class HighMindedDice(Dice):
    """High-minded Dice: 1,1,2,3,4,6 - on bank 6 raise combo (handled at bank time)"""

    def __init__(self):
        super().__init__([1, 1, 2, 3, 4, 6], "High-Minded")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class SpiteDice(Dice):
    """Spite Dice: X, X, 1, 1, 6, 6 - on 6 deal 1 opp damage"""

    def __init__(self):
        super().__init__([None, None, 1, 1, 6, 6], "Spite")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"opp_damage": 1}
        return {}


class InebriationDice(Dice):
    """Inebriation Dice: X,X,1,1,6,6 - on 6: take 1 regret to give 1 neurosis"""

    def __init__(self):
        super().__init__([None, None, 1, 1, 6, 6], "Inebriation")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"self_regret": 1, "opp_neurosis": 1}
        return {}


class GroundedDice(Dice):
    """Grounded Dice: X,1,2,3,4,4 - pair grants echo 1 to the insult (handled at bank time)"""

    def __init__(self):
        super().__init__([None, 1, 2, 3, 4, 4], "Grounded")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class NostalgiaDice(Dice):
    """Nostalgia Dice: X,1,2,3,4,4 - creates echo at banking (handled later)"""

    def __init__(self):
        super().__init__([None, 1, 2, 3, 4, 4], "Nostalgia")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class PenanceDice(Dice):
    """Penance Dice: 1..6 - on fumble with last roll >=4 doubles incoming damage (handled on fumble)"""

    def __init__(self):
        super().__init__([1, 2, 3, 4, 5, 6], "Penance")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class AcedicDice(Dice):
    """Acedic Dice: X,1,2,3,6,6 - on 6 heal 1 and if no regret, take one"""

    def __init__(self):
        super().__init__([None, 1, 2, 3, 6, 6], "Acedic")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            add_regret = 1 if getattr(player, "regret_tokens", 0) == 0 else 0
            eff: Dict[str, Any] = {"heal": 1}
            if add_regret:
                eff["self_regret"] = 1
            return eff
        return {}


class PilferDice(Dice):
    """Pilfer Dice: 1,1,2,3,6,6 - if both pilfers roll 6, steal (handled later)"""

    def __init__(self):
        super().__init__([1, 1, 2, 3, 6, 6], "Pilfer")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"pilfer_six": 1}
        return {}


class CatastrophizeDice(Dice):
    """Catastrophize Dice: 1,3,4,6,6,6 - on 1 immediate bust; on 6 grants bust-protection (later)"""

    def __init__(self):
        super().__init__([1, 3, 4, 6, 6, 6], "Catastrophize")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 1:
            return {"force_fumble": 1}
        return {}


class AporicDice(CatastrophizeDice):
    """Alias of Catastrophize with different display name"""

    def __init__(self):
        super().__init__()
        self.name = "Aporic"


class RidiculeDice(Dice):
    """Ridicule Dice: 1..6 - on 6: if no regret, gain one; else transfer one to opponent"""

    def __init__(self):
        super().__init__([1, 2, 3, 4, 5, 6], "Ridicule")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        if value == 6:
            return {"ridicule_six": 1}
        return {}


class NauseaDice(RidiculeDice):
    def __init__(self):
        super().__init__()
        self.name = "Nausea"


class CholericDie(Dice):
    def __init__(self):
        super().__init__([2, 2, 3, 4, 5, 6], "Choleric")
        self.color = "yellow"

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class MelancholicDie(Dice):
    def __init__(self):
        super().__init__([2, 2, 3, 4, 5, 6], "Melancholic")
        self.color = "gray"

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class PhlegmaticDie(Dice):
    def __init__(self):
        super().__init__([2, 2, 3, 4, 5, 6], "Phlegmatic")
        self.color = "green"

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class SanguineDie(Dice):
    def __init__(self):
        super().__init__([2, 2, 3, 4, 5, 6], "Sanguine")
        self.color = "red"

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class BlankDice(Dice):
    """Dice with blank faces (X)"""

    def __init__(self, faces: List[int]):
        # Replace None with a special marker for blank faces
        processed_faces = [face if face is not None else -1 for face in faces]
        super().__init__(processed_faces, "Blank")

    def can_roll(self) -> bool:
        """Blank dice cannot be rolled"""
        return False

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class ApatheticDice(Dice):
    """Apathetic Dice: X,X,X,6,6,6 - if banked, heal 2 (handled at bank time)"""

    def __init__(self):
        super().__init__([None, None, None, 6, 6, 6], "Apathetic")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


class AbyssalDice(Dice):
    """Abyssal Dice: X,X,X,X,X,X - after banking, can be added copying lowest die (handled at bank time)"""

    def __init__(self):
        super().__init__([None, None, None, None, None, None], "Abyssal")

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}

    def get_rules_text(self) -> str:
        return "After banking an insult, this die can be added to it, copying the value of that insult's lowest die"


class ComboDetector:
    """Detects and scores dice combinations"""

    @staticmethod
    def find_combos(dice_values: List[int]) -> List[Combo]:
        """Find the single best combination using a score = natural dice + echo dice."""
        dice_values = [d for d in dice_values if d is not None and d != -1]

        if not dice_values:
            return []

        # Count occurrences of each value
        counts: Dict[int, int] = {}
        for value in dice_values:
            counts[value] = counts.get(value, 0) + 1

        candidates: List[Combo] = []

        # 6 of a kind
        for value, count in counts.items():
            if count >= 6:
                candidates.append(Combo("Astonishing", [value] * 6, echo_dice=4))

        # straights helper
        def add_straights(min_len: int, name: str, echo: int):
            if len(dice_values) >= min_len:
                sorted_values = sorted(set(dice_values))
                for i in range(len(sorted_values) - (min_len - 1)):
                    if all(sorted_values[i + j] == sorted_values[i] + j for j in range(min_len)):
                        straight_dice = [sorted_values[i] + j for j in range(min_len)]
                        candidates.append(Combo(name, straight_dice, echo_dice=echo))

        # 6-straight (Surprising +1)
        add_straights(6, "Surprising", 1)

        # 5 of a kind
        for value, count in counts.items():
            if count >= 5:
                candidates.append(Combo("Distressing", [value] * 5, echo_dice=3))

        # 5-straight (Solid +0)
        add_straights(5, "Solid", 0)

        # two triplets (Surprising +1)
        trip_values = [v for v, c in counts.items() if c >= 3]
        if len(trip_values) >= 2:
            trip_values_sorted = sorted(trip_values, reverse=True)[:2]
            combo_dice = [trip_values_sorted[0]] * 3 + [trip_values_sorted[1]] * 3
            candidates.append(Combo("Surprising", combo_dice, echo_dice=1))

        # quadruplet + pair (Surprising +1)
        quad_values = [v for v, c in counts.items() if c >= 4]
        pair_values = [v for v, c in counts.items() if c >= 2]
        for qv in quad_values:
            for pv in pair_values:
                if pv != qv:
                    candidates.append(Combo("Surprising", [qv] * 4 + [pv] * 2, echo_dice=1))

        # 4 of a kind (Shocking +2)
        for value, count in counts.items():
            if count >= 4:
                candidates.append(Combo("Shocking", [value] * 4, echo_dice=2))

        # 4-straight, 3-straight
        add_straights(4, "Solid", 0)
        add_straights(3, "Solid", 0)

        # single triplet (Surprising +1)
        for value, count in counts.items():
            if count >= 3:
                candidates.append(Combo("Surprising", [value] * 3, echo_dice=1))

        # pairs (Solid +0) - pick all distinct pairs as candidates
        for value, count in counts.items():
            if count >= 2:
                candidates.append(Combo("Solid", [value] * 2, echo_dice=0))

        # single die (Solid +0) - highest die
        candidates.append(Combo("Solid", [max(dice_values)], echo_dice=0))

        # Score candidates: total dice won = len + echo; break ties by len then damage then higher faces
        def score(c: Combo) -> Tuple[int, int, int]:
            return (len(c.dice) + c.echo_dice, len(c.dice), c.damage)

        best = max(candidates, key=score) if candidates else None
        return [best] if best else []

    @staticmethod
    def can_make_combo(dice_values: List[int]) -> bool:
        """Check if any combo can be made with the given dice"""
        combos = ComboDetector.find_combos(dice_values)
        return len(combos) > 0 and any(combo.name != "Slighting" or len(combo.dice) > 0 for combo in combos)
