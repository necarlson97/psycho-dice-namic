"""
Emotion card definitions and text (markdown) for Psycho-Dice-Namic
"""

from typing import List, Dict


EMOTION_DEFINITIONS: List[Dict[str, str]] = [
    {
        "name": "Foreboding",
        "markdown": (
            "When triggered, either:\n\n"
            "1. gain 1 fumble-shield.\n\n"
            "2. Or convert 1 fumble-shield to 1 health + 1 rehash token."
        ),
    },
    {
        "name": "Catalepsy",
        "markdown": (
            "When triggered, choose one of an opponent’s live dice. That die is made waxy:"
            " it is still live, but its value is frozen. It cannot be rerolled for the rest of the round."
        ),
    },
    {
        "name": "Persecutory Delusions",
        "markdown": (
            "When triggered, you may take 1 Regret token yourself. If you do, target opponent gains 2 Regret tokens."
        ),
    },
    {
        "name": "Absolution",
        "markdown": (
            "When triggered, you may:\n\n"
            "1. remove 1 Neurosis token from yourself, and gain 1 Forgiveness token.\n\n"
            "2. remove 1 Neurosis token from an opponent, and gain 2 Forgiveness tokens."
        ),
    },
    {
        "name": "Cognitive Dissonance",
        "markdown": (
            "When triggered, you may flip one of your live dice upside-down to its opposite face."
        ),
    },
    {
        "name": "Tantrum",
        "markdown": ("When triggered, you and a target opponent each immediately take 1 damage."),
    },
    {
        "name": "Schadenfreude",
        "markdown": (
            "When triggered, gain 1 Neurosis token. Also: whenever any opponent fumbles, you gain 1 Eureka token."
            " This emotion cannot be triggered by Eureka tokens."
        ),
    },
    {
        "name": "Outburst",
        "markdown": (
            "When triggered, place a counter on this card. If there are 3 or more, remove all of them"
            " to immediately deal 3 damage to an opponent of your choice."
        ),
    },
    {
        "name": "Chivalry",
        "markdown": (
            "When triggered, you may immediately stop rolling and commit this round."
            " If you do, gain 1 rehash token and heal 1."
        ),
    },
    {
        "name": "Marxist Accelerationism",
        "markdown": (
            "When triggered, the player(s) with the highest current health each lose 2, while the player(s)"
            " with the lowest health each heal 2. (all tied are affected.)"
        ),
    },
    {
        "name": "Oppositional Defiance",
        "markdown": (
            "When triggered, gain 1 Neurosis token. Also: whenever you would take exactly 1 damage,"
            " assign that damage to an opponent instead."
        ),
    },
    {
        "name": "Masochistic Rapture",
        "markdown": (
            "When triggered: 1) deal 2 damage to yourself, and place a counter on this card; 2) when you have 6 counters,"
            " remove all of them to increment your 'wins' by 1"
        ),
    },
    {
        "name": "Obsessive Hoarding",
        "markdown": (
            "When triggered you may take 3 neurosis tokens. Also: Whenever you have neurosis tokens,"
            " increase your max live die count by 1. You can convert one of your somatic dice back to psychological,"
            " and roll it alongside your default 6."
        ),
    },
    {
        "name": "Hubris",
        "markdown": (
            "When triggered, summon an echo die for your next roll. However, if you fumble, you take 3 damage."
        ),
    },
    {
        "name": "Megalomania",
        "markdown": (
            "When triggered, choose an opponent. If that opponent has any Eureka tokens, they lose 1 Eureka and gain 1 Regret."
        ),
    },
    {
        "name": "Blatant Denial",
        "markdown": (
            "When triggered, gain 2 neurosis tokens, and transfer all Regret tokens from yourself to a chosen opponent."
        ),
    },
    {
        "name": "Trauma Dumping",
        "markdown": (
            "When triggered, you may take 1 or 2 damage; if you do, deal double that to a target opponent."
        ),
    },
    {
        "name": "Catharsis",
        "markdown": ("When triggered, if you have regret tokens, remove 1 and heal 1."),
    },
    {
        "name": "Metanoia",
        "markdown": (
            "When triggered, take 1 damage for each regret token, then remove all regret tokens."
            " If you removed at least one, gain 1 Forgiveness token."
        ),
    },
    {
        "name": "Latent Sadism",
        "markdown": (
            "When triggered, place a totem on this card. When the next debate ends, remove the totem."
            " While the totem is active, whenever you deal damage to an opponent, gain 1 rehash token."
            " (Not 1 token for every point of damage, just 1 token when dealing damage.)"
        ),
    },
    {
        "name": "Hypomania",
        "markdown": (
            "When triggered, you may place a totem on this card. When you fumble or perfect-bank, remove the totem(s)."
            " When the totem is active, you may add an echo dice to every roll."
            " However: you cannot commit - you can only fumble or perfect-bank."
        ),
    },
    {
        "name": "Codependence",
        "markdown": (
            "When triggered, gain 1 Neurosis token. If this card is totem-less, place a totem on this card, and choose an opponent.\n\n"
            "If they cause you to lose health, they lose the same amount, and the totem is removed. After the next debate, the totem is removed.\n\n"
            "If you already have an active Codependence, you cannot have another - but you do still take another neurosis."
        ),
    },
    {
        "name": "Repressed Shame",
        "markdown": (
            "When triggered, place 6 counters on this card. Whenever you take damage, you may use counters"
            " to instead convert damage to regret tokens."
        ),
    },
    {
        "name": "Apocalyptic Vision",
        "markdown": ("When triggered, every player gets the option to take 1 damage and remove all tokens."),
    },
    {
        "name": "Sanguine Bravado",
        "markdown": (
            "When triggered, if you have a live or banked red dice, you may remove it, and place it on this card as a counter."
            " You may decrement this die to remove a regret token. At the end of the next debate,"
            " convert any remaining counters into neurosis tokens."
        ),
    },
    {
        "name": "Choleric Disinhibition",
        "markdown": (
            "When triggered, select one live or banked orange die to reroll.\n"
            "If the result is 3 or less: deal that much damage to yourself.\n"
            "If the result is 4 or more: deal that much damage to an opponent."
        ),
    },
    {
        "name": "Melancholic Rumination",
        "markdown": (
            "When triggered, immediately fumble, and remove all regret tokens. If at least 1 is removed,"
            " you may gain 1 Eureka or heal 2. If no Regret is removed, gain 1 Regret."
        ),
    },
    {
        "name": "Phlegmatic Detachment",
        "markdown": (
            "When triggered, you may place a totem on this card. When the next debate ends, remove the totem. While the totem is active:"
            " 1) You cannot deal damage during debates, nor gain Eureka tokens. 2) But you cannot gain Regret nor Neurosis tokens."
        ),
    },
    {
        "name": "Monomaniacal Fixation",
        "markdown": (
            "When triggered, place a totem on this card, and choose a die color. When the next debate ends, remove the totem."
            " While the totem is active: 1) Once per roll, you may re-roll a die of that color"
            " 2) You cannot summon any echo dice, neither for your live pool, nor banked insults"
        ),
    },
    {
        "name": "Hypervigilance",
        "markdown": (
            "When triggered, gain 2 Neurosis. Place a totem on this card. When the next debate ends, remove the totem."
            " While the totem is active: whenever you take damage, you may negate it, and take that many regret tokens instead."
        ),
    },
    {
        "name": "Undue Certainty",
        "markdown": (
            "When triggered, you may set-aside up to 2 live dice from your current pool. If you do, gain 2 regret tokens."
            " (These dice are not banked - but their removal may allow you to avoid a fumble / achieve a perfect-bank.)"
        ),
    },
    {
        "name": "Smoldering Resentment",
        "markdown": (
            "When triggered, place a totem on this card. If you deal damage to an opponent while the totem is active:"
            " 1) deal 2 extra, but they may remove 1 Regret. 2) remove the totem."
            " If, after the next debate, you still have the token: 1) take 2 damage and gain 1 Regret. 2) remove the totem"
        ),
    },
    {
        "name": "Pathological Envy",
        "markdown": (
            "When triggered, if an opponent has more Eureka than you, steal 1 from them."
            " If no opponent has more Eureka than you, gain 1 Neurosis instead."
        ),
    },
    {
        "name": "Mortal Agitation",
        "markdown": (
            "When triggered, if your health is 3 or less, place a totem on this card. During the next debate, add two banked"
            " echo dice, as 6s, to an insult. Afterward, take 2 damage, gain 1 Regret, and remove the totem."
        ),
    },
    {
        "name": "Cognitive Reframing",
        "markdown": (
            "When triggered, flip one of your dice to its opposite face. If the new value is lower, remove 1 Neurosis token from yourself."
        ),
    },
    {
        "name": "Pair Bonding",
        "markdown": (
            "When triggered, place a totem on this card, and choose two dice to be pair bonded. Pair bonded dice must have the same face set."
            " The totem is removed after the next debate. While the totem is active: any time the pair bonded dice are both rolled,"
            " choose one. That die copies the other's face value."
        ),
    },
    {
        "name": "Impressionable Youth",
        "markdown": (
            "When triggered, place a totem on this card, and a live die to be impressionable. The totem is removed after the next debate."
            " While the totem is active: any time the impressionable die is rolled, you may have it copy the face value"
            " of another live die (if it has the same face)."
        ),
    },
    {
        "name": "Chameleon Effect",
        "markdown": (
            "When triggered, place a totem on this card. The totem is removed after the next debate. While the totem is active:"
            " once per roll, if a die lands on a 1, you may have that die instead copy another live die's value (if it has the same face)."
        ),
    },
    {
        "name": "Identity Crisis",
        "markdown": ("When triggered, immediately reroll all live dice."),
    },
    {
        "name": "Mass Hysteria",
        "markdown": ("When triggered, choose a color. All player's live dice of that color can be rerolled."),
    },
    {
        "name": "Moral Panic",
        "markdown": ("When triggered, choose a color. All player's banked dice of that color can be rerolled."),
    },
    {
        "name": "Polyamory",
        "markdown": ("When triggered, if you have at least one live die of each color, gain 1 Forgiveness token."),
    },
    {
        "name": "Compersion",
        "markdown": ("When triggered, choose an opponent. If they currently have more banked dice than you, gain 1 Forgiveness token."),
    },
    {
        "name": "Selective Perception",
        "markdown": (
            "When triggered, gain a totem, and choose a color to be ignored. The totem is removed after the next debate."
            " While the token is active, any of your dice of the ignored color cannot trigger."
        ),
    },
    {
        "name": "Compulsive Dichotomy",
        "markdown": (
            "When triggered, choose two live or banked dice of different colors. Change one's face to its maximum,"
            " and the other's to its minimum."
        ),
    },
    {
        "name": "Forced Dialectic",
        "markdown": (
            "When triggered, choose two live or banked dice of different colors. Change one's face to its maximum,"
            " and the other's to its minimum."
        ),
    },
    {
        "name": "Narcissistic Injury",
        "markdown": (
            "When triggered, choose an opponent's banked die, and one of your live or banked dice of a different color."
            " Reroll your die. If the new value exceeds the opponent's, remove 1 Neurosis token."
        ),
    },
    {
        "name": "Cautionary Tale",
        "markdown": (
            "When triggered, choose an opponent, choose a color, and place a totem by that player. When they next roll:"
            " 1) they remove live dice of that color (not banked, not live, do not trigger) 2) they remove the totem"
        ),
    },
    {
        "name": "Petulence",
        "markdown": (
            "When triggered, you may set an insult of banked dice to their minimum value. If one or more die value was changed,"
            " create 1 forgiveness token."
        ),
    },
    {
        "name": "Imposter Syndrome",
        "markdown": ("When triggered, swap a currently banked die for an echo die at 6."),
    },
    {
        "name": "Ego Boost",
        "markdown": ("When triggered, if there are any banked echo dice, you may change one's face value."),
    },
    {
        "name": "Ego Death",
        "markdown": (
            "Any time you perfect-bank, place a totem on this card. The totem is removed at the end of each stage."
            " When triggered, if the totem is active, immediately take 6 damage, and increment your win counter"
        ),
    },
    {
        "name": "Audit Memory",
        "markdown": (
            "When triggered, you may take a previously banked die, and add it back to your live pool. If you do, take 1 regret token."
        ),
    },
    {
        "name": "Humility",
        "markdown": (
            "When triggered, all opponents may remove 1 neurosis. If any do, you may convert 1 regret token to 1 forgiveness."
        ),
    },
    {
        "name": "The Weight of Violence",
        "markdown": (
            "When triggered, place a totem on this card. While the totem is active: Any time you deal exactly 1 damage to an opponent,"
            " you may deal 2 instead, and take a regret token. You may remove the totem whenever you wish."
        ),
    },
    {
        "name": "Impulse Control",
        "markdown": (
            "When triggered, immediately gain 1 regret token, set a live die to its highest value, and mark it as waxy:"
            " cannot be rerolled this round."
        ),
    },
    {
        "name": "Pheromonic Bond",
        "markdown": (
            "When triggered, choose a target live die (yours OR an opponent's). Then choose one of your live dice to match that value"
            " (if you have a live die with the matching face). Both dice become waxy (cannot be rerolled until next round)."
        ),
    },
    {
        "name": "Contagious Idealism",
        "markdown": (
            "When triggered, choose either Regret or Neurosis. If you have a token of that type, all opponent gain 1 of the same type."
        ),
    },
    {
        "name": "Intrusive Thought",
        "markdown": ("When triggered, reroll all live dice. If any die lands on a 1, gain 1 Neurosis token."),
    },
    {
        "name": "Habituation",
        "markdown": (
            "When triggered, you may either: 1) spend 1 Eureka token to set one of your live dice to any face, then make it waxy"
            " (cannot reroll this round), or 2) gain 1 Rehash token"
        ),
    },
    {
        "name": "Overstimulated",
        "markdown": ("When triggered, remove 1 rehash token to remove 1 token of any other type."),
    },
    {
        "name": "Projection",
        "markdown": ("When triggered, transfer 1 token of any kind from yourself to another player."),
    },
    {
        "name": "Placebo Effect",
        "markdown": (
            "When triggered, convert all neurosis tokens to placebo tokens (place them on this card). After the end of this round,"
            " convert all placebo tokens back to neurosis tokens."
        ),
    },
    {
        "name": "Heavy Sobbing",
        "markdown": (
            "When triggered, gain 1 Breakthrough token and 1 neurosis token. Also: you may instead spend breakthrough tokens"
            " to 'recontemplate' your psychological/somatic dice (swapping them in/out of your live and somatic pools)."
        ),
    },
    {
        "name": "Superego Shield",
        "markdown": (
            "When triggered, gain 1 Forgiveness token, and place a totem on this card. While the totem is active:"
            " 1) You cannot spend rehash tokens to reroll 2) You can spend 1 rehash token to remove 1 neurosis token"
            " 3) You can spend 1 forgiveness token to remove 1 regret token"
        ),
    },
]


