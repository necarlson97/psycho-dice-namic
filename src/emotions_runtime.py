"""
Runtime emotion system: base classes with auto-registry and hooks.
"""

from typing import Dict, Any, List, Optional, Type


class EmotionContext:
    def __init__(self, engine, self_player, opponent, round_num: int = 0, data: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.self = self_player
        self.opponent = opponent
        self.round_num = round_num
        self.data = data or {}

    # convenience helpers
    def deal_self(self, dmg: int):
        if dmg > 0:
            self.self.take_damage(dmg)

    def deal_opponent(self, dmg: int):
        if dmg > 0:
            self.opponent.take_damage(dmg)

    def heal_self(self, amt: int):
        if amt > 0:
            self.self.heal(amt)

    def add_token(self, token: str, amt: int = 1):
        token = token.lower()
        if token == 'eureka':
            self.self.eureka_tokens += amt
        elif token == 'breakthrough':
            self.self.breakthrough_tokens += amt
        elif token == 'rehash':
            self.self.rehash_tokens += amt
        elif token == 'forgiveness':
            self.self.forgiveness_tokens += amt
        elif token == 'neurosis':
            self.self.neurosis_tokens += amt
        elif token == 'regret':
            self.self.regret_tokens += amt
        elif token == 'fumble-shield':
            self.self.fumble_shields += amt

    def add_token_opponent(self, token: str, amt: int = 1):
        token = token.lower()
        if token == 'eureka':
            self.opponent.eureka_tokens += amt
        elif token == 'breakthrough':
            self.opponent.breakthrough_tokens += amt
        elif token == 'rehash':
            self.opponent.rehash_tokens += amt
        elif token == 'forgiveness':
            self.opponent.forgiveness_tokens += amt
        elif token == 'neurosis':
            self.opponent.neurosis_tokens += amt
        elif token == 'regret':
            self.opponent.regret_tokens += amt
        elif token == 'fumble-shield':
            self.opponent.fumble_shields += amt

    def add_totem(self, key: str, payload: Any = True):
        self.self.totems[key] = payload

    def remove_totem(self, key: str):
        if key in self.self.totems:
            del self.self.totems[key]


_AUTO_REGISTRY: Dict[str, Type["Emotion"]] = {}


def _camel_to_title(name: str) -> str:
    out = []
    prev_lower = False
    for ch in name:
        if ch.isupper() and prev_lower:
            out.append(' ')
        out.append(ch)
        prev_lower = ch.islower()
    return ''.join(out)


class Emotion:
    rules_text: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ == 'Emotion':
            return
        key_class = cls.__name__.lower()
        key_title = _camel_to_title(cls.__name__).lower()
        _AUTO_REGISTRY[key_class] = cls
        _AUTO_REGISTRY[key_title] = cls

    @property
    def name(self) -> str:
        return _camel_to_title(self.__class__.__name__)

    def on_debate_start(self, ctx: EmotionContext):
        pass

    def on_round_start(self, ctx: EmotionContext):
        pass

    def on_after_roll(self, ctx: EmotionContext):
        pass

    def on_bank(self, ctx: EmotionContext):
        pass

    def on_fumble(self, ctx: EmotionContext):
        pass

    def on_commit(self, ctx: EmotionContext):
        pass

    def on_clash_end(self, ctx: EmotionContext):
        pass

    def on_debate_end(self, ctx: EmotionContext):
        pass

    # explicit trigger
    def on_trigger(self, ctx: EmotionContext):
        pass


class Foreboding(Emotion):
    rules_text = "When triggered, gain 1 fumble-shield (or convert one to heal 1 + gain 1 rehash)."

    def on_trigger(self, ctx: EmotionContext):
        # default: gain a fumble-shield
        ctx.add_token('fumble-shield', 1)


class Catalepsy(Emotion):
    rules_text = "On trigger, choose an opponent live die; make it waxy for this round."
    # Requires selecting an opponent live die to make waxy; engine integration TBD
    pass


class Tantrum(Emotion):
    rules_text = "On trigger, both players take 1 damage."

    def on_trigger(self, ctx: EmotionContext):
        ctx.deal_self(1)
        ctx.deal_opponent(1)


class PersecutoryDelusions(Emotion):
    rules_text = "On trigger, you may take 1 Regret; if you do, opponent gains 2 Regret."

    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('regret', 1)
        ctx.add_token_opponent('regret', 2)


class Absolution(Emotion):
    rules_text = "On trigger, remove 1 Neurosis from self → +1 Forgiveness; else remove 1 from opponent → +2 Forgiveness."

    def on_trigger(self, ctx: EmotionContext):
        if ctx.self.neurosis_tokens > 0:
            ctx.self.neurosis_tokens -= 1
            ctx.add_token('forgiveness', 1)
        elif ctx.opponent.neurosis_tokens > 0:
            ctx.opponent.neurosis_tokens -= 1
            ctx.add_token('forgiveness', 2)


class CognitiveDissonance(Emotion):
    rules_text = "After roll, you may flip one of your live dice to its opposite face."

    def on_after_roll(self, ctx: EmotionContext):
        pool = ctx.data.get('pool') or []
        # Evaluate no-flip vs flipping each eligible die; keep the flip that maximizes the best combo score.
        def extract_vals(p):
            return [v for (v, _d) in p]

        def score_for(vals):
            # Use engine's combo detector to evaluate best combo and score by (len+echo, len, damage)
            combos = ctx.engine.combo_detector.find_combos(vals)
            if not combos:
                return (0, 0, 0)
            c = combos[0]
            return (len(c.dice) + getattr(c, 'echo_dice', 0), len(c.dice), getattr(c, 'damage', 0))

        base_vals = extract_vals(pool)
        best_score = score_for(base_vals)
        best_change = None  # (index, new_val)

        for i, (v, dobj) in enumerate(pool):
            if isinstance(v, int) and 1 <= v <= 6:
                flipped = 7 - v
                if flipped == v:
                    continue
                cand_vals = list(base_vals)
                cand_vals[i] = flipped
                cand_score = score_for(cand_vals)
                if cand_score > best_score:
                    best_score = cand_score
                    best_change = (i, flipped)

        if best_change is not None:
            i, new_v = best_change
            _old_v, dobj = pool[i]
            pool[i] = (new_v, dobj)


class Outburst(Emotion):
    rules_text = "On trigger, place a counter; at 3, deal 3 damage to an opponent and reset."

    def __init__(self):
        self._counters = 0

    def on_trigger(self, ctx: EmotionContext):
        self._counters += 1
        if self._counters >= 3:
            self._counters = 0
            ctx.deal_opponent(3)


class Chivalry(Emotion):
    rules_text = "On trigger, immediately commit, gain 1 rehash, and heal 1."

    def on_trigger(self, ctx: EmotionContext):
        ctx.self.force_commit = True
        ctx.add_token('rehash', 1)
        ctx.heal_self(1)


class MarxistAccelerationism(Emotion):
    rules_text = "On trigger, highest health players lose 2; lowest heal 2 (all ties)."

    def on_trigger(self, ctx: EmotionContext):
        h_self = ctx.self.health
        h_opp = ctx.opponent.health
        hi = max(h_self, h_opp)
        lo = min(h_self, h_opp)
        if h_self == hi:
            ctx.deal_self(2)
        if h_opp == hi:
            ctx.deal_opponent(2)
        if h_self == lo:
            ctx.heal_self(2)
        if h_opp == lo:
            ctx.opponent.heal(2)


class MasochisticRapture(Emotion):
    rules_text = "On trigger, self takes 2 damage; at 6 counters, increment your wins by 1 (reset)."

    def __init__(self):
        self._counters = 0

    def on_trigger(self, ctx: EmotionContext):
        ctx.deal_self(2)
        self._counters += 1
        if self._counters >= 6:
            self._counters = 0
            ctx.self.win_counter += 1

# auto-registered via __init_subclass__


# Additional emotions
class Schadenfreude(Emotion):
    rules_text = "On trigger, gain 1 Neurosis. Also: when any opponent fumbles, gain 1 Eureka."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('neurosis', 1)
    def on_fumble(self, ctx: EmotionContext):
        if ctx.data.get('opponent_fumbled'):
            ctx.add_token('eureka', 1)


class OppositionalDefiance(Emotion):
    rules_text = "On trigger, gain 1 Neurosis. Also: whenever you would take exactly 1 damage, assign it to an opponent instead."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('neurosis', 1)
        ctx.self.totems['deflect_one_damage'] = True


class Codependence(Emotion):
    rules_text = "On trigger, gain 1 Neurosis. If no totem, place a totem linked to an opponent; if they cause you to lose health, they lose the same and remove the totem."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('neurosis', 1)
        if not ctx.self.totems.get('codependence_active'):
            ctx.self.totems['codependence_active'] = {'target': ctx.opponent.name}


class Hypervigilance(Emotion):
    rules_text = "On trigger, gain 2 Neurosis and place a totem. While active: on taking damage, you may negate and take that many Regret instead."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('neurosis', 2)
        ctx.self.totems['hypervigilance'] = True


class UndueCertainty(Emotion):
    rules_text = "On trigger, you may set aside up to 2 live dice; gain 2 Regret."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('regret', 2)
        ctx.self.totems['set_aside_limit'] = 2


class SmolderingResentment(Emotion):
    rules_text = "On trigger, place a totem: if you deal damage, +2 extra (opponent may remove 1 Regret), then remove totem. If still active next debate end: take 2 damage and gain 1 Regret."
    def on_trigger(self, ctx: EmotionContext):
        ctx.self.totems['smoldering'] = True


class PathologicalEnvy(Emotion):
    rules_text = "On trigger, if an opponent has more Eureka, steal 1; otherwise gain 1 Neurosis."
    def on_trigger(self, ctx: EmotionContext):
        if ctx.opponent.eureka_tokens > ctx.self.eureka_tokens and ctx.opponent.eureka_tokens > 0:
            ctx.opponent.eureka_tokens -= 1
            ctx.add_token('eureka', 1)
        else:
            ctx.add_token('neurosis', 1)


class IntrusiveThought(Emotion):
    rules_text = "On trigger, reroll all live dice next roll; gain 1 Neurosis for any die landing on 1."
    def on_trigger(self, ctx: EmotionContext):
        # mark to reroll all live dice next after-roll
        ctx.self.totems['intrusive_reroll'] = True
    def on_after_roll(self, ctx: EmotionContext):
        if ctx.self.totems.get('intrusive_reroll'):
            pool = ctx.data.get('pool') or []
            import random as _r
            for i,(v,dobj) in enumerate(pool):
                if isinstance(v,int) and 1<=v<=6:
                    nv = _r.randint(1,6)
                    pool[i] = (nv,dobj)
                    if nv == 1:
                        ctx.add_token('neurosis',1)
            ctx.self.totems.pop('intrusive_reroll', None)


class Habituation(Emotion):
    rules_text = "On trigger, spend 1 Eureka to set a live die to any face (mark waxy), or gain 1 Rehash."
    def on_trigger(self, ctx: EmotionContext):
        if ctx.self.eureka_tokens > 0:
            ctx.self.eureka_tokens -= 1
            # set highest die to 6 and mark waxy
            pool = ctx.data.get('pool') or []
            best_idx=-1; best_val=-1
            for i,(v,dobj) in enumerate(pool):
                if isinstance(v,int) and v>best_val:
                    best_val=v; best_idx=i
            if best_idx>=0:
                v,dobj = pool[best_idx]
                pool[best_idx] = (6,dobj)
                ctx.self.totems['waxy_indices'] = (ctx.self.totems.get('waxy_indices') or set()); ctx.self.totems['waxy_indices'].add(best_idx)
        else:
            ctx.add_token('rehash',1)


class Overstimulated(Emotion):
    rules_text = "On trigger, remove 1 Rehash to remove 1 token of any other type."
    def on_trigger(self, ctx: EmotionContext):
        if ctx.self.rehash_tokens>0:
            ctx.self.rehash_tokens-=1
            # remove any one other token if present (pref neurosis)
            if ctx.self.neurosis_tokens>0:
                ctx.self.neurosis_tokens-=1
            elif ctx.self.regret_tokens>0:
                ctx.self.regret_tokens-=1


class Projection(Emotion):
    rules_text = "On trigger, transfer 1 token (prefers Neurosis, then Regret, then Forgiveness) to another player."
    def on_trigger(self, ctx: EmotionContext):
        # transfer one token in priority order
        if ctx.self.neurosis_tokens>0:
            ctx.self.neurosis_tokens-=1; ctx.add_token_opponent('neurosis',1)
        elif ctx.self.regret_tokens>0:
            ctx.self.regret_tokens-=1; ctx.add_token_opponent('regret',1)
        elif ctx.self.forgiveness_tokens>0:
            ctx.self.forgiveness_tokens-=1; ctx.add_token_opponent('forgiveness',1)


class PlaceboEffect(Emotion):
    rules_text = "On trigger, convert all Neurosis to placebo tokens until end of debate, then convert back."
    def on_trigger(self, ctx: EmotionContext):
        # move neurosis to placebo bucket for the round
        n = ctx.self.neurosis_tokens
        ctx.self.neurosis_tokens = 0
        ctx.self.totems['placebo_tokens'] = ctx.self.totems.get('placebo_tokens',0)+n
    def on_debate_end(self, ctx: EmotionContext):
        # convert back after round
        n = ctx.self.totems.pop('placebo_tokens',0)
        ctx.self.neurosis_tokens += n


class SuperegoShield(Emotion):
    rules_text = "On trigger, gain 1 Forgiveness and place a totem with restrictions on spending/removing tokens."
    def on_trigger(self, ctx: EmotionContext):
        ctx.add_token('forgiveness',1)
        ctx.self.totems['superego_shield'] = True


# auto-registered via __init_subclass__


def create_emotions(names: List[str]) -> List[Emotion]:
    out: List[Emotion] = []
    for n in names:
        key = (n or '').strip().lower()
        cls = _AUTO_REGISTRY.get(key)
        if cls:
            out.append(cls())
        else:
            out.append(Emotion())
    return out


