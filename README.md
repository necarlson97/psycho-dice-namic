# Psycho-Dice-Namic

**Roll to see who rules the mind**

A Python simulation suite for the Psycho-Dice-Namic board game - a rogue-lite dice-builder where shattered archetypes of the psyche vie for control of the mind.

## Overview

This repository contains:
- **Game Engine**: Core mechanics for dice rolling, combo detection, and damage calculation
- **Archetypes**: Different starting loadouts (Tabula Rasa, Euphoria)
- **Simulators**: Archetype vs archetype and special dice testing
- **Visualization**: HTML reports with interactive charts using Jinja2 and Plotly

## Game Mechanics

### Basic Flow
1. Players choose archetypes with different dice loadouts
2. Each round, players simultaneously roll their dice
3. Players bank dice combos to form "insults"
4. Players can re-roll remaining dice or commit
5. Fumbling (no possible combos) loses all banked insults
6. Damage is calculated with blocking mechanics

### Combo Types
- **Astonishing** (sextuplet): +4 echo dice
- **Distressing** (quintuplet): +3 echo dice
- **Shocking** (quadruplet): +2 echo dice
- **Surprising** (triplet, two-triplets, 6-straight, quadruplet+pair): +1 echo die
- **Solid** (3-5 straights, pairs, individual dice): no bonus dice

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run simulations:**
   ```bash
   ./go.sh
   ```

## Usage

### Quick Start
The `go.sh` script will:
- Set up the virtual environment
- Install dependencies
- Run all simulations
- Generate HTML reports
- Watch for file changes and re-run

### Manual Execution
```bash
cd src
python run_simulations.py
```

### Generated Reports
- `archetype_comparison.html` - Tabula Rasa vs Euphoria analysis
- `hand_testing.html` - Special dice performance comparison

## Project Structure

```
psycho-dice-namic/
├── src/                    # Python source code
│   ├── dice.py            # Dice classes and combo detection
│   ├── archetypes.py      # Player archetypes and special dice
│   ├── game_engine.py     # Core game mechanics
│   ├── simulators.py      # Simulation engines
│   └── run_simulations.py # Main runner script
├── templates/             # Jinja2 HTML templates
│   ├── archetype_comparison.html
│   └── hand_testing.html
├── env/                   # Virtual environment
├── requirements.txt       # Python dependencies
├── go.sh                 # Development script
└── README.md
```

## Archetypes

### Tabula Rasa
- 6x Normal d6 (1,2,3,4,5,6)
- The baseline archetype

### Euphoria
- 1x Bliss Dice (1,1,1,2,2,4) - Heals on 4
- 1x Comedown Dice (2,2,2,4,4,6) - Damage on 6
- 4x Normal d6
- Can take forgiveness tokens instead of healing

## Special Dice Testing

The simulator tests various special dice configurations against normal dice:
- High 6s: [1,2,3,4,6,6]
- Low 1s: [1,1,3,4,5,6]
- Extreme: [1,1,1,6,6,6]
- Pairs: [2,2,4,4,6,6]
- Triplets: [1,1,3,3,5,5]
- And more...

## Development

The `go.sh` script uses `watchdog` to monitor file changes and automatically re-run simulations when code is modified. This provides a smooth development experience for iterating on game mechanics and balance.

## Future Enhancements

- More archetypes and special dice
- Advanced AI strategies
- Tournament mode
- Asset generation for physical game components
- Web-based interactive simulator
