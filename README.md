# Zork I: The Great Underground Empire - Python Implementation

A faithful Python implementation of the classic text adventure game Zork I, originally created by Infocom. This version maintains the spirit of the original while being written in modern Python 3.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-playable-green.svg)

## Overview

> You are standing in an open field west of a white house, with a boarded front door.

This Python implementation of Zork includes the complete above-ground and underground areas of the original game, featuring all the classic puzzles, treasures, and memorable encounters that made Zork a defining game of the interactive fiction genre.

## Features

### 🗺️ Complete Game World
- **60+ fully implemented rooms** including:
  - The iconic white house and surrounding forest
  - The Great Underground Empire with its mazes and caverns
  - Special areas: Dam, Temple, Land of the Dead, Coal Mine
  - Hidden locations and secret passages

### 👹 All Original NPCs
- **The Troll** - Guards the passages with his bloody axe
- **The Thief** - Randomly appears to relieve you of treasures
- **The Cyclops** - Guards the treasure room, fears his father's name
- **Evil Spirits** - Block the entrance to Hades
- **Vampire Bat** - Fears garlic, guards the jade figurine

### 💎 20+ Treasures to Discover
- Jewel-encrusted egg with golden canary
- Platinum bar
- Crystal trident
- Pot of gold at the end of the rainbow
- Ivory torch
- Ancient coins
- And many more valuable artifacts

### 🧩 Classic Puzzles
- **Dam Control** - Manipulate water levels to reveal treasures
- **Rainbow Solidification** - Use the sceptre to cross the rainbow
- **Mirror Room** - Break the mirror to connect passages
- **Exorcism Ritual** - Bell, book, and candles to banish spirits
- **Coal to Diamond** - Transform coal in the machine
- **Rope and Dome** - Navigate vertical passages

### 🎮 Game Mechanics
- **Inventory management** with weight limits
- **Light/darkness system** with limited lamp battery
- **Combat system** for fighting enemies
- **Death and resurrection** - Return as a spirit
- **Score tracking** with ranks from Beginner to Master Adventurer
- **Save/restore** functionality with full game state preservation

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies required (uses only Python standard library)

### Quick Start

1. **Clone or download the game**
```bash
git clone https://github.com/yourusername/zork-python.git
cd zork-python
```

2. **Run the game**
```bash
python3 zork_expanded.py
```

3. **Enter your name when prompted**
```
What is your name, adventurer? > Your Name
```

## How to Play

### Basic Commands

#### Movement
- `north`, `south`, `east`, `west` (or `n`, `s`, `e`, `w`)
- `northeast`, `northwest`, `southeast`, `southwest` (or `ne`, `nw`, `se`, `sw`)
- `up`, `down` (or `u`, `d`)
- `in`, `out`, `enter`, `exit`

#### Object Interaction
- `take [object]` or `get [object]` - Pick up an item
- `drop [object]` - Put down an item
- `examine [object]` or `x [object]` - Look at something closely
- `open [object]` - Open doors, containers, etc.
- `close [object]` - Close doors, containers, etc.
- `put [object] in [container]` - Place items in containers

#### Game Actions
- `look` or `l` - Describe current location
- `inventory` or `i` - List what you're carrying
- `score` - Check your current score
- `save` - Save your game
- `restore` - Load a saved game
- `quit` - Exit the game

#### Special Actions
- `light lamp` - Turn on the brass lantern
- `turn off lamp` - Turn off the lamp
- `move rug` - Might reveal something...
- `tie rope to [object]` - Secure rope for climbing
- `ring bell` - Ring the brass bell
- `dig` - If you have a shovel...
- `pray` - At the altar...
- `attack [enemy] with [weapon]` - Combat

### Tips for New Players

1. **Explore thoroughly** - Examine everything, try different commands
2. **Draw a map** - The underground can be confusing
3. **Save often** - Before dangerous situations
4. **Manage your lamp** - It has limited battery life (330 turns)
5. **Some treasures need care** - The egg is fragile!
6. **Read carefully** - Descriptions contain important clues
7. **The thief is tricky** - He can steal your treasures
8. **Death isn't the end** - You'll resurrect at the starting location

### Scoring System

- Maximum score: **350 points**
- Points are earned by:
  - Finding treasures
  - Depositing treasures in the trophy case
  - Solving certain puzzles

#### Ranks
- 0-24 points: **Beginner**
- 25-49 points: **Amateur Adventurer**
- 50-99 points: **Novice Adventurer**
- 100-199 points: **Junior Adventurer**
- 200-299 points: **Adventurer**
- 300-329 points: **Master**
- 330-349 points: **Wizard**
- 350 points: **Master Adventurer**

## Game Architecture

### Core Components

```python
# Main game components
ZorkGame          # Main game controller
Room              # Room/location class
GameObject        # Items and objects
Actor             # NPCs (troll, thief, etc.)
ParsedCommand     # Command parsing result

# Enumerations
Direction         # Movement directions
VerbType         # Action verbs
ObjectFlag       # Object properties
RoomFlag         # Room properties
```

### File Structure
```
zork-python/
├── zork_expanded.py     # Complete game implementation
├── README.md            # This file
├── saves/               # Saved games directory
└── docs/               # Additional documentation
```

## Differences from Original

This implementation stays faithful to the original while adding some modern conveniences:

### Enhancements
- **Character naming** - Personalize your adventure
- **Improved parser** - More flexible command recognition
- **Better save system** - JSON-based saves with full state
- **Death counter** - Track your mortality
- **Extended descriptions** - Some areas have richer descriptions

### Maintained Original Features
- All original puzzles and solutions
- Same treasure values and locations
- Original room connections and maze layout
- Classic combat and NPC behaviors
- Original score system and ranks

## Known Issues

- The parser is simpler than Infocom's original
- Some complex command combinations may not work
- No built-in hints system (as in later Infocom games)

## Development

### Extending the Game

The modular design makes it easy to add new content:

```python
# Add a new room
self.rooms["new_room"] = Room(
    id="new_room",
    name="New Room",
    description="Description here...",
    flags=RoomFlag.LIT.value,
    exits={Direction.NORTH: "other_room"}
)

# Add a new item
self.objects["new_item"] = GameObject(
    id="new_item",
    name="widget",
    description="strange widget",
    examine_text="It's a strange widget.",
    flags=ObjectFlag.TAKEABLE.value,
    location="new_room"
)
```

### Contributing

Contributions are welcome! Areas for improvement:
- Parser enhancements
- Additional NPC interactions
- Sound effects support
- Graphics/mapping integration
- Mobile-friendly interface

## Troubleshooting

### Common Issues

**"You can't see in the dark"**
- You need a light source. Find and light the brass lantern.

**"Your load is too heavy"**
- Drop some items. You can only carry 7 items at once.

**"The troll blocks your way"**
- Defeat him with a weapon or pay him with a treasure.

**Save/Load not working**
- Ensure the script has write permissions in its directory.

## Credits

### Original Creators
- **Tim Anderson** - Original designer
- **Marc Blank** - Original designer  
- **Bruce Daniels** - Original designer
- **Dave Lebling** - Original designer
- **Infocom** - Original publisher

### Python Implementation
- Based on the C version translated from FORTRAN
- Inspired by various open-source Zork implementations
- Created with love for the interactive fiction community

## License

This implementation is released under the MIT License. The original Zork game design and text are the property of Activision (who acquired Infocom's assets).

## Resources

### Related Projects
- [Zork Map Editor](https://github.com/yourusername/zork-map-editor) - Visual editor for game maps
- [Original Zork Source](https://github.com/MITDDC/zork) - Historical MDL source code
- [Frotz](https://davidgriffith.gitlab.io/frotz/) - Z-machine interpreter

### Learning More
- [Infocom Documentation](http://infodoc.plover.net/)
- [Interactive Fiction Archive](https://www.ifarchive.org/)
- [IFDB - Interactive Fiction Database](https://ifdb.org/)

---

*"It is pitch black. You are likely to be eaten by a grue."*

Happy adventuring! May you find all the treasures and achieve the rank of Master Adventurer!