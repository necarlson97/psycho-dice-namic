"""
Archetype definitions for Psycho-Dice-Namic
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from dice import (
    Dice, NormalDice, BlissDice, ComedownDice, BlankDice,
    HighMindedDice, SpiteDice, InebriationDice, GroundedDice, NostalgiaDice,
    PenanceDice, AcedicDice, PilferDice, CatastrophizeDice, RidiculeDice,
    CholericDie, MelancholicDie, PhlegmaticDie, SanguineDie,
    AporicDice, NauseaDice, ApatheticDice, AbyssalDice
)

# Centralized game constants
MAX_HEALTH = 12


@dataclass
class Player:
    """Represents a player in the game"""
    name: str
    health: int = MAX_HEALTH
    forgiveness_tokens: int = 0
    neurosis_tokens: int = 0
    regret_tokens: int = 0
    eureka_tokens: int = 0
    breakthrough_tokens: int = 0
    rehash_tokens: int = 0
    fumble_shields: int = 0
    bust_protection: bool = False
    penance_double_active: bool = False
    pending_pilfer_next_round: bool = False
    pending_echo_values: List[int] = None
    totems: Dict[str, Any] = None
    emotions: List[Any] = None
    win_counter: int = 0
    force_commit: bool = False
    dice: List[Dice] = None

    def __post_init__(self):
        if self.dice is None:
            self.dice = []
        if self.pending_echo_values is None:
            self.pending_echo_values = []
        if self.totems is None:
            self.totems = {}
        if self.emotions is None:
            self.emotions = []

    def take_damage(self, amount: int) -> int:
        """Take damage, return actual damage taken"""
        actual_damage = min(amount, self.health)
        self.health -= actual_damage
        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal, return actual healing done"""
        actual_healing = min(amount, MAX_HEALTH - self.health)
        self.health += actual_healing
        return actual_healing

    def add_forgiveness_token(self):
        """Add a forgiveness token"""
        self.forgiveness_tokens += 1

    def add_neurosis_tokens(self, amount: int = 1):
        """Add neurosis tokens"""
        if amount > 0:
            self.neurosis_tokens += amount

    def add_regret_tokens(self, amount: int = 1):
        """Add regret tokens"""
        if amount > 0:
            self.regret_tokens += amount

    def use_forgiveness_token(self) -> bool:
        """Use a forgiveness token to heal 1, return True if used"""
        if self.forgiveness_tokens > 0:
            self.forgiveness_tokens -= 1
            self.heal(1)
            return True
        return False


class Archetype:
    """Base class for player archetypes"""

    def __init__(self, name: str, dice: List[Dice]):
        self.name = name
        self.dice = dice

    def create_player(self, player_name: str) -> Player:
        """Create a new player with this archetype's dice"""
        return Player(
            name=player_name,
            dice=[dice for dice in self.dice]  # Create copies
        )

    def apply_special_effects(self, player: Player, dice_results: List[int]) -> Dict[str, Any]:
        """Apply any special effects from rolled dice"""
        effects: Dict[str, Any] = {"heal": 0, "damage": 0, "forgiveness_tokens": 0}

        for i, result in enumerate(dice_results):
            if i < len(player.dice):
                dice_effects = player.dice[i].special_effect(result, player)
                for k, v in dice_effects.items():
                    if isinstance(v, (int, float)):
                        effects[k] = effects.get(k, 0) + v
                    else:
                        effects[k] = v

        return effects


class TabulaRasa(Archetype):
    """Tabula Rasa: 6x normal white d6"""

    def __init__(self):
        super().__init__("Tabula Rasa", [NormalDice() for _ in range(6)])


class Hedonist(Archetype):
    """The Hedonist: Bliss + Comedown + 4x normal"""

    def __init__(self):
        super().__init__("The Hedonist", [
            BlissDice(), ComedownDice(),
            NormalDice(), NormalDice(), NormalDice(), NormalDice()
        ])
class Euphoria(Archetype):
    """Euphoria: 1x Bliss Dice, 1x Comedown Dice, 4x normal d6"""

    def __init__(self):
        super().__init__("Euphoria", [
            BlissDice(),
            ComedownDice(),
            NormalDice(),
            NormalDice(),
            NormalDice(),
            NormalDice()
        ])

    def apply_special_effects(self, player: Player, dice_results: List[int]) -> Dict[str, Any]:
        """Apply Euphoria-specific special effects"""
        effects = super().apply_special_effects(player, dice_results)

        # Euphoria special rule: can take forgiveness token instead of healing
        if effects["heal"] > 0:
            # For now, always take forgiveness tokens instead of healing
            # In a real game, this would be a player choice
            effects["forgiveness_tokens"] += effects["heal"]
            effects["heal"] = 0

        return effects


class Temperance(Archetype):
    """Temperance: 1x each humor die + 2x normal d6.
    Post-commit: compute humor totals of banked dice and apply top humor effect.
    """

    def __init__(self):
        super().__init__(
            "Temperance",
            [CholericDie(), MelancholicDie(), PhlegmaticDie(), SanguineDie(), NormalDice(), NormalDice()]
        )

    def apply_special_effects(self, player: Player, dice_results: List[int]) -> Dict[str, Any]:
        # On-roll effects are none for Temperance; commit-time handled in engine future hook
        return super().apply_special_effects(player, dice_results)


class Intellectualism(Archetype):
    """Intellectualism: 2x High-minded + 4x normal. On banking a 6 from High-minded, raise combo.
    The raise is handled at bank time in engine (future hook).
    """

    def __init__(self):
        super().__init__(
            "Intellectualism",
            [HighMindedDice(), HighMindedDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


class Belligerence(Archetype):
    """Belligerence: Spite + Inebriation + 4x normal"""

    def __init__(self):
        super().__init__(
            "Belligerence",
            [SpiteDice(), InebriationDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

    def apply_special_effects(self, player: Player, dice_results: List[int]) -> Dict[str, Any]:
        effects = super().apply_special_effects(player, dice_results)
        # Interpret effects produced by dice
        # opp_damage handled in engine clash step; capture flags here for engine to read
        return effects


class Naivety(Archetype):
    """Naïvety: Simpleton + Nostalgia + 4x normal.
    - Simpleton: when banked as one-pair, raises the pair level (engine banking hook).
    - Nostalgia: creates echo die with same value until next roll (engine hook).
    """

    def __init__(self):
        super().__init__(
            "Naïvety",
            [SimpletonsDice(), NostalgiaDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


class Guilt(Archetype):
    """Guilt: Penance + Acedic + 4x normal.
    - Penance: on fumble with last roll >=4, double clash damage (engine fumble/clash hook).
    - Acedic: on 6 heal 1, and if 0 regret tokens, gain 1 regret.
    """

    def __init__(self):
        super().__init__(
            "Guilt",
            [PenanceDice(), AcedicDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


class Jealousy(Archetype):
    """Jealousy: 2x Pilfer + 4x normal.
    If both Pilfer dice roll a 6, steal a live die from opponent (engine clash/roll hook).
    """

    def __init__(self):
        super().__init__(
            "Jealousy",
            [PilferDice(), PilferDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


class Anxiety(Archetype):
    """Anxiety: Catastrophize + Ridicule + 4x normal.
    - Catastrophize: on 1 immediate bust; on 6 gain bust-protection (engine round loop hook).
    - Ridicule: on 6: if no regret, gain one; else transfer one to opponent (engine clash hook).
    """

    def __init__(self):
        super().__init__(
            "Anxiety",
            [CatastrophizeDice(), RidiculeDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


# New renamed archetypes per latest spec
class Physiognomist(Archetype):
    def __init__(self):
        super().__init__(
            "The Physiognomist",
            [CholericDie(), MelancholicDie(), PhlegmaticDie(), SanguineDie(), NormalDice(), NormalDice()]
        )

class Rationalist(Archetype):
    def __init__(self):
        super().__init__(
            "The Rationalist",
            [HighMindedDice(), HighMindedDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Fatalist(Archetype):
    def __init__(self):
        super().__init__(
            "The Fatalist",
            [SpiteDice(), InebriationDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Transcendentalist(Archetype):
    def __init__(self):
        super().__init__(
            "The Transcendentalist",
            [GroundedDice(), NostalgiaDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Puritan(Archetype):
    def __init__(self):
        super().__init__(
            "The Puritan",
            [PenanceDice(), AcedicDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Machiavalian(Archetype):
    def __init__(self):
        super().__init__(
            "The Machiavalian",
            [PilferDice(), PilferDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Absurdist(Archetype):
    def __init__(self):
        super().__init__(
            "The Absurdist",
            [AporicDice(), NauseaDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Stoic(Archetype):
    def __init__(self):
        super().__init__(
            "The Stoic",
            [ApatheticDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )

class Nihilist(Archetype):
    def __init__(self):
        super().__init__(
            "The Nihilist",
            [AbyssalDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice(), NormalDice()]
        )


# Special face dice for testing
class SpecialFaceDice(Dice):
    """Dice with custom face values for testing"""

    def __init__(self, faces: List[int], name: str = "Special"):
        super().__init__(faces, name)

    def special_effect(self, value: int, player) -> Dict[str, Any]:
        return {}


def create_special_dice(faces: List[int], name: str = "Special") -> SpecialFaceDice:
    """Create a special face dice with the given faces"""
    return SpecialFaceDice(faces, name)


# Predefined special dice for testing
SPECIAL_DICE_DEFINITIONS = {
    "normal_d6": [1, 2, 3, 4, 5, 6],  # Normal d6 for baseline
    "extra high": [1, 2, 3, 4, 6, 6],
    "extra low": [1, 1, 3, 4, 5, 6],
    "extreme": [1, 1, 1, 6, 6, 6],
    "evens": [2, 2, 4, 4, 6, 6],
    "odds": [1, 1, 3, 3, 5, 5],
    "missing 1": [None, 2, 3, 4, 5, 6],  # X, 2, 3, 4, 5, 6
    "missing 6": [1, 2, 3, 4, 5, None],  # 1, 2, 3, 4, 5, X
    "more 3s": [1, 3, 3, 3, 3, 6],
    "more middle": [1, 2, 4, 4, 5, 6],
    "all_blank": [None, None, None, None, None, None],  # X, X, X, X, X, X
    "half_blank": [1, 2, 3, None, None, None]  # 1, 2, 3, X, X, X
}

# Defense dice faces (name -> faces)
DEFENSE_DICE_DEFINITIONS: Dict[str, List[int]] = {
    "Halo-Effect": [1, 2, 3, 3, 4, 4],
    "Scapegoat": [2, 3, 4, 5, 6, 6],
    "Normalcy": [1, 2, 3, 4, 5, 6],
    "Just-World": [1, 2, 3, 4, 5, 6],
    "Victimhood": [None, 1, 2, 4, 5, 6],
    "Dunning-Kruger": [2, 3, 4, 5, 6, 6],
    "Mere-Exposure": [1, 2, 3, 4, 5, 6],
    "Egocentric": [1, 1, 2, 2, 6, 6],
    "Illusory-Control": [1, 2, 3, 4, 5, 6],
    "Bandwagon": [1, 2, 3, 4, 5, 6],
    "Narrative-Fallacy": [1, 2, 3, 4, 5, 6],
    "Groupshift": [1, 2, 3, 4, 5, 6],
}

# Human-readable defense dice descriptions
DEFENSE_DICE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Halo-Effect": {
        "subtitle": "Defense Die",
        "psych": "Triggers when this die is live, and any other of your live dice lands on a 6. Includes normal rolling, as well as manual changing.",
        "som": "Triggers when your roll contains zero 6s."
    },
    "Scapegoat": {
        "subtitle": "Defense Die",
        "psych": "If this die is live during a fumble, roll a d6: triggers that many times.",
        "som": "If you successfully commit 3 separate insults in a single debate, gain a eureka token."
    },
    "Normalcy": {
        "subtitle": "Defense Die",
        "psych": "Triggers when banked as part of a one-pair.",
        "som": "Trigger after rolling only odd faces."
    },
    "Just-World": {
        "subtitle": "Defense Die",
        "psych": "Trigger when banking four or more dice in a single insult.",
        "som": "Trigger after rolling only even faces."
    },
    "Victimhood": {
        "subtitle": "Defense Die",
        "psych": "Whenever you take more than 3 damage, roll a d6. If the result is < the damage you took, gain a breakthrough token.",
        "som": "Whenever you lose a debate, gain a eureka token."
    },
    "Dunning-Kruger": {
        "subtitle": "Defense Die",
        "psych": "Triggers when you bank an insult of only 1s.",
        "som": "Whenever you fumble, gain 1 fumble-shield token and 1 breakthrough token. (Prevented fumbles do not activate 'when you fumble' triggers)"
    },
    "Mere-Exposure": {
        "subtitle": "Defense Die",
        "psych": "Triggers any time you bank an insult that contains a 1.",
        "som": "Every time you roll a '1', place a counter on this card. When it reaches 6, remove it, and trigger this 3 times."
    },
    "Egocentric": {
        "subtitle": "Defense Die",
        "psych": "Trigger every time you deal exactly 1 damage.",
        "som": "At the start of each round, triggers twice for every debate that has passed."
    },
    "Illusory-Control": {
        "subtitle": "Defense Die",
        "psych": "Triggers every time you receive a token (not by its imbued emotion).",
        "som": "Triggers every time you decrement a token (but not 'clearing' tokens)."
    },
    "Bandwagon": {
        "subtitle": "Defense Die",
        "psych": "Triggers any time an echo die is summoned by yourself or opponents (not by its imbued emotion).",
        "som": "Increase your max live die count by 1. You can convert one of your somatic dice back to psychological, and roll it alongside your default 6. (Bandwagon Die has no somatic trigger)"
    },
    "Narrative-Fallacy": {
        "subtitle": "Defense Die",
        "psych": "Triggers when banking a straight.",
        "som": "Triggers every roll, if every live die has the normal faces [1, 2, 3, 5, 6]."
    },
    "Groupshift": {
        "subtitle": "Defense Die",
        "psych": "If you bank 5 or more dice, and still lose the debate, gain a eureka token.",
        "som": "If you bank 3 or less dice, and win the debate, gain a breakthrough token."
    },
}
