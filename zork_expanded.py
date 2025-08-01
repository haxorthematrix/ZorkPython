#!/usr/bin/env python3
"""
Zork (Dungeon) - Python Implementation - Expanded Version
Based on the C version translated from FORTRAN by way of f2c
Original game by Tim Anderson, Marc Blank, Bruce Daniels, and Dave Lebling
Python conversion maintains the structure and functionality of the C version
This expanded version includes more rooms, treasures, NPCs, and puzzles from the original
"""

import sys
import os
import pickle
import json
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Union
import random
import textwrap

# Constants and Enumerations
class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NE = "northeast"
    NW = "northwest"
    SE = "southeast"
    SW = "southwest"
    UP = "up"
    DOWN = "down"
    IN = "in"
    OUT = "out"
    LAND = "land"

class VerbType(Enum):
    TAKE = auto()
    DROP = auto()
    OPEN = auto()
    CLOSE = auto()
    LIGHT = auto()
    EXTINGUISH = auto()
    MOVE = auto()
    ATTACK = auto()
    EXAMINE = auto()
    READ = auto()
    THROW = auto()
    PUT = auto()
    TURN = auto()
    JUMP = auto()
    INVENTORY = auto()
    QUIT = auto()
    SAVE = auto()
    RESTORE = auto()
    RESTART = auto()
    VERBOSE = auto()
    BRIEF = auto()
    SCORE = auto()
    VERSION = auto()
    LOOK = auto()
    WAIT = auto()
    AGAIN = auto()
    ENTER = auto()
    EXIT = auto()
    CLIMB = auto()
    GIVE = auto()
    DRINK = auto()
    EAT = auto()
    BREAK = auto()
    KILL = auto()
    WAVE = auto()
    RAISE = auto()
    LOWER = auto()
    TURN_ON = auto()
    TURN_OFF = auto()
    DIAGNOSE = auto()
    UNLOCK = auto()
    LOCK = auto()
    TIE = auto()
    UNTIE = auto()
    BURN = auto()
    RING = auto()
    WIND = auto()
    DIG = auto()
    FILL = auto()
    POUR = auto()
    PRAY = auto()
    PUSH = auto()
    
# Object flags
class ObjectFlag(Enum):
    VISIBLE = 0x0001
    TAKEABLE = 0x0002
    CONTAINER = 0x0008
    OPEN = 0x0010
    CLOSED = 0x0020
    LOCKED = 0x0040
    LIGHT = 0x0080
    READABLE = 0x0100
    DOOR = 0x0200
    TRANSPARENT = 0x0400
    WEAPON = 0x0800
    TURNNABLE = 0x1000
    TURNEDON = 0x2000
    EDIBLE = 0x4000
    DRINKABLE = 0x8000
    TREASURE = 0x10000
    VEHICLE = 0x20000
    SACRED = 0x40000
    TOOL = 0x80000
    FLAMMABLE = 0x100000
    
# Room flags
class RoomFlag(Enum):
    LIT = 0x0001
    DEATH = 0x0002
    SACRED = 0x0008
    NOPIRATE = 0x0010
    ONWATER = 0x0020
    
@dataclass
class GameObject:
    """Represents an object in the game"""
    id: str
    name: str
    description: str = ""
    examine_text: str = ""
    initial_text: str = ""
    flags: int = 0
    location: Optional[str] = None
    capacity: int = 0
    size: int = 0
    value: int = 0
    
    def has_flag(self, flag: ObjectFlag) -> bool:
        return bool(self.flags & flag.value)
    
    def set_flag(self, flag: ObjectFlag, value: bool = True):
        if value:
            self.flags |= flag.value
        else:
            self.flags &= ~flag.value
            
@dataclass
class Room:
    """Represents a room/location in the game"""
    id: str
    name: str
    description: str = ""
    flags: int = 0
    exits: Dict[Direction, str] = field(default_factory=dict)
    
    def has_flag(self, flag: RoomFlag) -> bool:
        return bool(self.flags & flag.value)
    
    def set_flag(self, flag: RoomFlag, value: bool = True):
        if value:
            self.flags |= flag.value
        else:
            self.flags &= ~flag.value

@dataclass
class Actor:
    """Represents an NPC in the game"""
    id: str
    name: str
    description: str
    location: Optional[str]
    health: int = 100
    hostile: bool = False
    active: bool = True
    messages: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class ParsedCommand:
    """Result of parsing user input"""
    verb: Optional[VerbType] = None
    direct_object: Optional[str] = None
    indirect_object: Optional[str] = None
    direction: Optional[Direction] = None
    raw_input: str = ""

class ZorkGame:
    """Main game class"""
    
    def __init__(self):
        # Player name
        self.player_name: str = "Adventurer"
        
        # Game state
        self.rooms: Dict[str, Room] = {}
        self.objects: Dict[str, GameObject] = {}
        self.actors: Dict[str, Actor] = {}
        self.current_room: str = "west_of_house"
        self.player_inventory: List[str] = []
        self.score: int = 0
        self.moves: int = 0
        self.verbose: bool = True
        self.game_over: bool = False
        self.visited_rooms: Set[str] = set()
        self.deaths: int = 0
        
        # Special flags
        self.lamp_on: bool = False
        self.lamp_life: int = 330  # Lamp has limited life
        self.grating_unlocked: bool = False
        self.trap_door_open: bool = False
        self.rainbow_solid: bool = False
        self.dam_open: bool = False
        self.loud_room_level: int = 4  # Water level
        self.coffin_open: bool = False
        self.bell_rung: bool = False
        self.candles_lit: bool = False
        self.book_read: bool = False
        self.spirits_released: bool = False
        self.cyclops_fled: bool = False
        self.mirror_broken: bool = False
        self.troll_payment: bool = False
        self.thief_here: bool = False
        self.treasures_deposited: int = 0
        
        # Initialize game world
        self._init_rooms()
        self._init_objects()
        self._init_actors()
        
    def _init_rooms(self):
        """Initialize all rooms"""
        
        # Above Ground Areas
        self.rooms["west_of_house"] = Room(
            id="west_of_house",
            name="West of House",
            description="You are standing in an open field west of a white house, with a boarded front door.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "north_of_house",
                Direction.SOUTH: "south_of_house",
                Direction.WEST: "forest_1",
                Direction.EAST: "west_of_house"  # Can't enter house this way
            }
        )
        
        self.rooms["north_of_house"] = Room(
            id="north_of_house",
            name="North of House",
            description="You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "west_of_house",
                Direction.EAST: "behind_house",
                Direction.NORTH: "forest_path"
            }
        )
        
        self.rooms["behind_house"] = Room(
            id="behind_house",
            name="Behind House",
            description="You are behind the white house. A path leads into the forest to the east. In one corner of the house there is a small window which is slightly ajar.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "north_of_house",
                Direction.SOUTH: "south_of_house",
                Direction.EAST: "clearing",
                Direction.WEST: "kitchen",
                Direction.IN: "kitchen"
            }
        )
        
        self.rooms["south_of_house"] = Room(
            id="south_of_house",
            name="South of House", 
            description="You are facing the south side of a white house. There is no door here, and all the windows are boarded.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "west_of_house",
                Direction.EAST: "behind_house",
                Direction.SOUTH: "forest_1"
            }
        )
        
        # Inside House
        self.rooms["kitchen"] = Room(
            id="kitchen",
            name="Kitchen",
            description="You are in the kitchen of the white house. A table seems to have been used recently for the preparation of food. A passage leads to the west and a dark staircase can be seen leading upward. A dark chimney leads down and to the east is a small window which is open.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.EAST: "behind_house",
                Direction.WEST: "living_room",
                Direction.UP: "attic",
                Direction.DOWN: "studio",
                Direction.OUT: "behind_house"
            }
        )
        
        self.rooms["living_room"] = Room(
            id="living_room",
            name="Living Room", 
            description="You are in the living room. There is a doorway to the east, a wooden door with strange gothic lettering to the west, which appears to be nailed shut, a trophy case, and a large oriental rug in the center of the room.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.EAST: "kitchen",
                Direction.WEST: "strange_passage"  # Through the door - initially blocked
            }
        )
        
        self.rooms["attic"] = Room(
            id="attic",
            name="Attic",
            description="This is the attic. The only exit is a stairway leading down.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.DOWN: "kitchen"
            }
        )
        
        # Forest
        self.rooms["forest_1"] = Room(
            id="forest_1",
            name="Forest",
            description="This is a forest, with trees in all directions. To the east, there appears to be sunlight.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "clearing",
                Direction.EAST: "forest_path",
                Direction.SOUTH: "forest_3",
                Direction.WEST: "forest_1",
                Direction.UP: "up_tree"
            }
        )
        
        self.rooms["forest_path"] = Room(
            id="forest_path",
            name="Forest Path",
            description="This is a path winding through a dimly lit forest. The path heads north-south here. One particularly large tree with some low branches stands at the edge of the path.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "north_of_house",
                Direction.NORTH: "clearing",
                Direction.UP: "up_tree"
            }
        )
        
        self.rooms["up_tree"] = Room(
            id="up_tree",
            name="Up a Tree",
            description="You are about 10 feet above the ground nestled among some large branches. The nearest branch above you is above your reach.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.DOWN: "forest_path"
            }
        )
        
        self.rooms["forest_2"] = Room(
            id="forest_2",
            name="Forest", 
            description="This is a dimly lit forest, with large trees all around.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "clearing",
                Direction.NORTH: "clearing",
                Direction.EAST: "canyon_view",
                Direction.WEST: "forest_3"
            }
        )
        
        self.rooms["forest_3"] = Room(
            id="forest_3",
            name="Forest",
            description="This is a dimly lit forest, with large trees all around.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "south_of_house",
                Direction.WEST: "forest_1",
                Direction.EAST: "forest_2",
                Direction.SOUTH: "forest_3"
            }
        )
        
        self.rooms["clearing"] = Room(
            id="clearing",
            name="Clearing",
            description="You are in a clearing, with a forest surrounding you on all sides. A path leads south.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "forest_path",
                Direction.NORTH: "forest_2",
                Direction.EAST: "canyon_view",
                Direction.WEST: "behind_house",
                Direction.DOWN: "grating_room"  # Through grating when open
            }
        )
        
        # Canyon Area
        self.rooms["canyon_view"] = Room(
            id="canyon_view",
            name="Canyon View",
            description="You are at the top of the Great Canyon on its west side. From here there is a marvelous view of the canyon and parts of the Frigid River upstream. Across the canyon, the walls of the White Cliffs join the mighty ramparts of the Flathead Mountains to the east. Following the Canyon upstream to the north, Aragain Falls may be seen, complete with rainbow. The mighty Frigid River flows out from a great dark cavern. To the west and south can be seen an immense forest, stretching for miles around. A path leads northwest. It is possible to climb down into the canyon from here.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "forest_2",
                Direction.DOWN: "rocky_ledge",
                Direction.NW: "clearing"
            }
        )
        
        self.rooms["rocky_ledge"] = Room(
            id="rocky_ledge",
            name="Rocky Ledge",
            description="You are on a ledge about halfway up the wall of the river canyon. You can see from here that the main flow from Aragain Falls twists along a passage which it is impossible for you to enter. Below you is the canyon bottom. Above you is more cliff, which appears unclimbable.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.UP: "canyon_view",
                Direction.DOWN: "canyon_bottom"
            }
        )
        
        self.rooms["canyon_bottom"] = Room(
            id="canyon_bottom",
            name="Canyon Bottom",
            description="You are beneath the walls of the river canyon which may be climbable here. The lesser part of the runoff of Aragain Falls flows by below. To the north is a narrow path.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.UP: "rocky_ledge",
                Direction.NORTH: "end_of_rainbow"
            }
        )
        
        self.rooms["end_of_rainbow"] = Room(
            id="end_of_rainbow",
            name="End of Rainbow",
            description="You are on a small, rocky beach on the continuation of the Frigid River past the Falls. The beach is narrow due to the presence of the White Cliffs. The river canyon opens here and sunlight shines in from above. A rainbow crosses over the falls to the east and a narrow path continues to the southwest.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.SW: "canyon_bottom",
                Direction.EAST: "on_the_rainbow"  # Only when rainbow solid
            }
        )
        
        self.rooms["on_the_rainbow"] = Room(
            id="on_the_rainbow",
            name="On the Rainbow",
            description="You are on top of a rainbow (I bet you never thought you would walk on a rainbow), with a magnificent view of the Falls. The rainbow travels east-west here.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.WEST: "end_of_rainbow",
                Direction.EAST: "aragain_falls"
            }
        )
        
        self.rooms["aragain_falls"] = Room(
            id="aragain_falls",
            name="Aragain Falls",
            description="You are at the top of Aragain Falls, an enormous waterfall with a drop of about 150 feet. The only safe way down is on the west side of the falls.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.WEST: "on_the_rainbow",
                Direction.UP: "on_the_rainbow",
                Direction.DOWN: "end_of_rainbow"
            }
        )
        
        # Underground - Main Areas
        self.rooms["cellar"] = Room(
            id="cellar",
            name="Cellar",
            description="You are in a dark and damp cellar with a narrow passageway leading north, and a crawlway to the south. On the west is the bottom of a steep metal ramp which is unclimbable.",
            flags=0,
            exits={
                Direction.NORTH: "troll_room",
                Direction.SOUTH: "east_of_chasm",
                Direction.WEST: "slide_room",  # One way from slide
                Direction.UP: "living_room"  # Only if trap door open
            }
        )
        
        self.rooms["troll_room"] = Room(
            id="troll_room",
            name="The Troll Room", 
            description="This is a small room with passages to the east and south and a forbidding hole leading west. Bloodstains and deep scratches (perhaps made by an axe) mar the walls.",
            flags=0,
            exits={
                Direction.SOUTH: "cellar",
                Direction.EAST: "east_west_passage",
                Direction.WEST: "maze_1"
            }
        )
        
        self.rooms["east_west_passage"] = Room(
            id="east_west_passage",
            name="East-West Passage",
            description="This is a narrow east-west passageway. There is a narrow stairway leading down at the north end of the room.",
            flags=0,
            exits={
                Direction.EAST: "round_room",
                Direction.WEST: "troll_room",
                Direction.NORTH: "chasm",
                Direction.DOWN: "chasm"
            }
        )
        
        self.rooms["round_room"] = Room(
            id="round_room",
            name="Round Room",
            description="This is a circular stone room with passages in all directions. Several of them have unfortunately been blocked by cave-ins.",
            flags=0,
            exits={
                Direction.WEST: "east_west_passage",
                Direction.NORTH: "north_south_passage",
                Direction.SOUTH: "narrow_passage",
                Direction.EAST: "loud_room",
                Direction.SE: "engravings_cave"
            }
        )
        
        self.rooms["narrow_passage"] = Room(
            id="narrow_passage",
            name="Narrow Passage",
            description="This is a long and narrow corridor where a long north-south passageway briefly narrows even further.",
            flags=0,
            exits={
                Direction.NORTH: "round_room",
                Direction.SOUTH: "mirror_room_south"
            }
        )
        
        self.rooms["mirror_room_south"] = Room(
            id="mirror_room_south",
            name="Mirror Room",
            description="You are in a large square room with tall ceilings. On the south wall is an enormous mirror which fills the entire wall. There are exits on the other three sides of the room.",
            flags=0,
            exits={
                Direction.NORTH: "narrow_passage",
                Direction.WEST: "winding_passage",
                Direction.EAST: "cave_2"
            }
        )
        
        self.rooms["cave_2"] = Room(
            id="cave_2",
            name="Cave",
            description="This is a tiny cave with entrances west and north, and a staircase leading down.",
            flags=0,
            exits={
                Direction.WEST: "mirror_room_south",
                Direction.NORTH: "mirror_room_north",
                Direction.DOWN: "entrance_to_hades"
            }
        )
        
        self.rooms["winding_passage"] = Room(
            id="winding_passage",
            name="Winding Passage",
            description="This is a winding passage. It seems that there are only exits on the east and north.",
            flags=0,
            exits={
                Direction.NORTH: "mirror_room_north",
                Direction.EAST: "mirror_room_south"
            }
        )
        
        self.rooms["mirror_room_north"] = Room(
            id="mirror_room_north",
            name="Mirror Room",
            description="You are in a large square room with tall ceilings. On the south wall is an enormous mirror which fills the entire wall. There are exits on the other three sides of the room.",
            flags=0,
            exits={
                Direction.SOUTH: "winding_passage",
                Direction.WEST: "cold_passage",
                Direction.EAST: "cave_1"
            }
        )
        
        self.rooms["cold_passage"] = Room(
            id="cold_passage",
            name="Cold Passage",
            description="This is a cold and damp corridor where a long east-west passageway turns into a southward path.",
            flags=0,
            exits={
                Direction.EAST: "mirror_room_north",
                Direction.SOUTH: "slide_room"
            }
        )
        
        self.rooms["slide_room"] = Room(
            id="slide_room",
            name="Slide Room",
            description="This is a small chamber, which appears to have been part of a coal mine. On the south wall of the chamber the letters \"Granite Wall\" are etched in the rock. To the east is a long passage, and there is a steep metal slide twisting downward. To the north is a small opening.",
            flags=0,
            exits={
                Direction.NORTH: "cold_passage",
                Direction.EAST: "mine_entrance",
                Direction.DOWN: "cellar"  # One way slide
            }
        )
        
        self.rooms["mine_entrance"] = Room(
            id="mine_entrance",
            name="Mine Entrance",
            description="You are standing at the entrance of what might have been a coal mine. The shaft enters the west wall, and there is another exit on the south end of the room.",
            flags=0,
            exits={
                Direction.WEST: "slide_room",
                Direction.SOUTH: "squeaky_room"
            }
        )
        
        self.rooms["squeaky_room"] = Room(
            id="squeaky_room",
            name="Squeaky Room",
            description="You are in a small room. Strange squeaky sounds may be heard coming from the darkness at the east end of the room.",
            flags=0,
            exits={
                Direction.NORTH: "mine_entrance",
                Direction.EAST: "bat_room"
            }
        )
        
        self.rooms["bat_room"] = Room(
            id="bat_room",
            name="Bat Room",
            description="You are in a small room which has doors only to the east and west.",
            flags=0,
            exits={
                Direction.WEST: "squeaky_room",
                Direction.EAST: "shaft_room"
            }
        )
        
        self.rooms["shaft_room"] = Room(
            id="shaft_room",
            name="Shaft Room",
            description="This is a large room, in the middle of which is a small shaft descending through the floor into darkness below. To the west and the north are exits from this room. Constructed over the top of the shaft is a metal framework to which a heavy iron chain is attached.",
            flags=0,
            exits={
                Direction.WEST: "bat_room",
                Direction.NORTH: "smelly_room",
                Direction.DOWN: "drafty_room"  # Via rope or chain
            }
        )
        
        self.rooms["smelly_room"] = Room(
            id="smelly_room",
            name="Smelly Room",
            description="This is a small nondescript room. However, from the direction of a small descending staircase a foul odor can be detected. To the south is a narrow tunnel.",
            flags=0,
            exits={
                Direction.SOUTH: "shaft_room",
                Direction.DOWN: "gas_room"
            }
        )
        
        self.rooms["gas_room"] = Room(
            id="gas_room",
            name="Gas Room",
            description="This is a small room which smells strongly of coal gas. There is a short climb up some stairs and a narrow tunnel leading east.",
            flags=0,
            exits={
                Direction.UP: "smelly_room",
                Direction.EAST: "coal_mine_1"
            }
        )
        
        self.rooms["coal_mine_1"] = Room(
            id="coal_mine_1",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.WEST: "gas_room",
                Direction.NORTH: "coal_mine_2",
                Direction.EAST: "coal_mine_3",
                Direction.SW: "timber_room"
            }
        )
        
        self.rooms["coal_mine_2"] = Room(
            id="coal_mine_2",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_1",
                Direction.NORTH: "coal_mine_4",
                Direction.SE: "coal_mine_3"
            }
        )
        
        self.rooms["coal_mine_3"] = Room(
            id="coal_mine_3",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.WEST: "coal_mine_1",
                Direction.EAST: "coal_mine_4",
                Direction.SOUTH: "ladder_top",
                Direction.NW: "coal_mine_2"
            }
        )
        
        self.rooms["coal_mine_4"] = Room(
            id="coal_mine_4",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_2",
                Direction.WEST: "coal_mine_3",
                Direction.NORTH: "dead_end_coal_mine"
            }
        )
        
        self.rooms["dead_end_coal_mine"] = Room(
            id="dead_end_coal_mine",
            name="Dead End",
            description="You have come to a dead end in the mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_4"
            }
        )
        
        self.rooms["ladder_top"] = Room(
            id="ladder_top",
            name="Ladder Top",
            description="This is a very small room. In the corner is a rickety wooden ladder, leading downward. It might be safe to descend. There is also a staircase leading upward.",
            flags=0,
            exits={
                Direction.NORTH: "coal_mine_3",
                Direction.DOWN: "ladder_bottom",
                Direction.UP: "coal_mine_3"
            }
        )
        
        self.rooms["ladder_bottom"] = Room(
            id="ladder_bottom",
            name="Ladder Bottom",
            description="This is a rather wide room. On one side is the bottom of a narrow wooden ladder. To the west and the south are passages leaving the room.",
            flags=0,
            exits={
                Direction.UP: "ladder_top",
                Direction.WEST: "timber_room",
                Direction.SOUTH: "dead_end_mine"
            }
        )
        
        self.rooms["dead_end_mine"] = Room(
            id="dead_end_mine",
            name="Dead End",
            description="You have come to a dead end in the mine.",
            flags=0,
            exits={
                Direction.NORTH: "ladder_bottom"
            }
        )
        
        self.rooms["timber_room"] = Room(
            id="timber_room",
            name="Timber Room",
            description="This is a long and narrow passage, which is cluttered with broken timbers. A wide passage comes from the east and turns at the west end of the room into a very narrow passageway. From the west comes a strong draft.",
            flags=0,
            exits={
                Direction.EAST: "ladder_bottom",
                Direction.WEST: "drafty_room",
                Direction.SOUTH: "coal_mine_1"
            }
        )
        
        self.rooms["drafty_room"] = Room(
            id="drafty_room",
            name="Drafty Room",
            description="This is a small drafty room in which is the bottom of a long shaft. To the south is a passageway and to the east a very narrow passage. In the shaft can be seen a heavy iron chain.",
            flags=0,
            exits={
                Direction.EAST: "timber_room",
                Direction.SOUTH: "machine_room",
                Direction.UP: "shaft_room"
            }
        )
        
        self.rooms["machine_room"] = Room(
            id="machine_room",
            name="Machine Room",
            description="This is a large, cold room whose sole exit is to the north. In one corner there is a machine which is reminiscent of a clothes dryer. On its face is a switch which is labelled \"START\". The switch does not appear to be manipulatable by any human hand (unless the fingers are about 1/16 by 1/4 inch). On the front of the machine is a large lid, which is closed.",
            flags=0,
            exits={
                Direction.NORTH: "drafty_room"
            }
        )
        
        # Cave Area
        self.rooms["cave_1"] = Room(
            id="cave_1",
            name="Cave",
            description="This is a tiny cave with entrances west and north, and a dark, forbidding staircase leading down.",
            flags=0,
            exits={
                Direction.WEST: "mirror_room_north",
                Direction.NORTH: "twisting_passage",
                Direction.DOWN: "entrance_to_hades"
            }
        )
        
        self.rooms["twisting_passage"] = Room(
            id="twisting_passage",
            name="Twisting Passage",
            description="This is a winding passage. It seems that there are only exits on the east and north.",
            flags=0,
            exits={
                Direction.NORTH: "mirror_room_north",
                Direction.SOUTH: "cave_1"
            }
        )
        
        # Temple Area
        self.rooms["north_south_passage"] = Room(
            id="north_south_passage",
            name="North-South Passage",
            description="This is a high north-south passage, which forks to the northeast.",
            flags=0,
            exits={
                Direction.NORTH: "chasm",
                Direction.NE: "deep_canyon",
                Direction.SOUTH: "round_room"
            }
        )
        
        self.rooms["chasm"] = Room(
            id="chasm",
            name="Chasm",
            description="A chasm runs southwest to northeast and the path follows it. You are on the south side of the chasm, where a crack opens into a passage.",
            flags=0,
            exits={
                Direction.NE: "reservoir_south",
                Direction.SW: "east_west_passage",
                Direction.SOUTH: "north_south_passage",
                Direction.DOWN: "north_south_passage"
            }
        )
        
        self.rooms["deep_canyon"] = Room(
            id="deep_canyon",
            name="Deep Canyon",
            description="You are on the south edge of a deep canyon. Passages lead off to the east, northwest and southwest. A stairway leads down. You can hear the sound of flowing water from below.",
            flags=0,
            exits={
                Direction.SW: "north_south_passage",
                Direction.EAST: "dam",
                Direction.NW: "reservoir_south",
                Direction.DOWN: "loud_room"
            }
        )
        
        self.rooms["loud_room"] = Room(
            id="loud_room",
            name="Loud Room",
            description="This is a large room with a ceiling which cannot be detected from the ground. There is a narrow passage from east to west and a stone stairway leading upward. The room is deafeningly loud with an undetermined rushing sound. The sound seems to reverberate from all of the walls, making it difficult to determine its origin (although it is louder towards the west).",
            flags=0,
            exits={
                Direction.WEST: "round_room",
                Direction.UP: "deep_canyon",
                Direction.EAST: "damp_cave"
            }
        )
        
        self.rooms["damp_cave"] = Room(
            id="damp_cave",
            name="Damp Cave",
            description="This cave has exits to the west and east, and narrows to a crack toward the south. The earth is particularly damp here.",
            flags=0,
            exits={
                Direction.WEST: "loud_room",
                Direction.EAST: "white_cliffs_beach_north"
            }
        )
        
        self.rooms["white_cliffs_beach_north"] = Room(
            id="white_cliffs_beach_north",
            name="White Cliffs Beach",
            description="You are on a narrow strip of beach which runs along the base of the White Cliffs. There is a narrow path heading south along the Cliffs and a tight passage leading west into the cliffs themselves.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.WEST: "damp_cave",
                Direction.SOUTH: "white_cliffs_beach_south"
            }
        )
        
        self.rooms["white_cliffs_beach_south"] = Room(
            id="white_cliffs_beach_south",
            name="White Cliffs Beach",
            description="You are on a rocky, narrow strip of beach beside the Cliffs. A narrow path leads north along the shore.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.NORTH: "white_cliffs_beach_north"
            }
        )
        
        # Dam Area
        self.rooms["dam"] = Room(
            id="dam",
            name="Dam",
            description="You are standing on the top of the Flood Control Dam #3, which was built in 783 GUE to harness the mighty Frigid River. The dam controls a sluice gate by which water is passed downstream. The sluice gate can be controlled by a panel of buttons on the dam. A ladder leads down to the base of the dam.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.WEST: "deep_canyon",
                Direction.NORTH: "dam_lobby",
                Direction.EAST: "dam_base",
                Direction.DOWN: "dam_base"
            }
        )
        
        self.rooms["dam_lobby"] = Room(
            id="dam_lobby",
            name="Dam Lobby",
            description="This room appears to have been the waiting room for groups touring the dam. There are open doorways here to the north and east marked \"Private\", though the doors are open, and an exit to the south.",
            flags=0,
            exits={
                Direction.SOUTH: "dam",
                Direction.NORTH: "maintenance_room",
                Direction.EAST: "maintenance_room"
            }
        )
        
        self.rooms["maintenance_room"] = Room(
            id="maintenance_room",
            name="Maintenance Room",
            description="This is what appears to have been the maintenance room for Flood Control Dam #3. Apparently, it has been many years since its last use. Most of the equipment here is in a state of disrepair. The only exit is to the south.",
            flags=0,
            exits={
                Direction.SOUTH: "dam_lobby"
            }
        )
        
        self.rooms["dam_base"] = Room(
            id="dam_base",
            name="Dam Base",
            description="You are at the base of Flood Control Dam #3, which looms above you and to the north. The River Frigid is flowing by here. Along the river are the White Cliffs which seem to form giant walls stretching from north to south along the shores of the river as it winds its way downstream.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.NORTH: "dam",
                Direction.UP: "dam"
            }
        )
        
        # Reservoir Area
        self.rooms["reservoir_south"] = Room(
            id="reservoir_south",
            name="Reservoir South",
            description="You are in a long room on the south shore of a large lake, far too deep and wide for crossing. There is a path along the stream to the east or west, a steep pathway climbing southwest along the edge of a chasm, and a path leading into a canyon to the southeast.",
            flags=0,
            exits={
                Direction.SE: "deep_canyon",
                Direction.SW: "chasm",
                Direction.WEST: "stream_view",
                Direction.EAST: "dam",
                Direction.NORTH: "reservoir"  # When drained can walk across
            }
        )
        
        self.rooms["reservoir"] = Room(
            id="reservoir",
            name="Reservoir",
            description="You are on the lake. Beaches can be seen north and south. Upstream a small stream enters the lake through a narrow cleft in the rocks. The dam can be seen downstream.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.SOUTH: "reservoir_south",
                Direction.NORTH: "reservoir_north"
            }
        )
        
        self.rooms["reservoir_north"] = Room(
            id="reservoir_north",
            name="Reservoir North",
            description="You are in a large cavernous room, north of a large lake. There is a slimy stairway leaving the room to the north.",
            flags=0,
            exits={
                Direction.SOUTH: "reservoir",
                Direction.NORTH: "atlantis_room"
            }
        )
        
        self.rooms["stream_view"] = Room(
            id="stream_view",
            name="Stream View",
            description="You are standing on a path beside a gently flowing stream. The path follows the stream, which flows from west to east.",
            flags=0,
            exits={
                Direction.EAST: "reservoir_south",
                Direction.WEST: "stream"
            }
        )
        
        self.rooms["stream"] = Room(
            id="stream",
            name="Stream",
            description="You are on the gently flowing stream. The upstream route is too narrow to navigate, and the downstream route is blocked by a dam.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.EAST: "reservoir",
                Direction.WEST: "sluice_gate"  # Only when dam open
            }
        )
        
        # Atlantis
        self.rooms["atlantis_room"] = Room(
            id="atlantis_room",
            name="Atlantis Room",
            description="This is an ancient room, long buried beneath the earth. The room is bare, but the walls are covered with decorations of great archaeological value. An exit lies to the south, and a staircase leads up.",
            flags=0,
            exits={
                Direction.SOUTH: "reservoir_north",
                Direction.UP: "cave_2"
            }
        )
        
        # Maze
        self.rooms["maze_1"] = Room(
            id="maze_1",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "troll_room",
                Direction.NORTH: "maze_1",
                Direction.SOUTH: "maze_2",
                Direction.EAST: "maze_4"
            }
        )
        
        self.rooms["maze_2"] = Room(
            id="maze_2",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.SOUTH: "maze_1",
                Direction.NORTH: "maze_4",
                Direction.EAST: "maze_3"
            }
        )
        
        self.rooms["maze_3"] = Room(
            id="maze_3",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_2",
                Direction.NORTH: "maze_4",
                Direction.UP: "maze_5"
            }
        )
        
        self.rooms["maze_4"] = Room(
            id="maze_4",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike. A skeleton, probably the remains of a luckless adventurer, lies here.",
            flags=0,
            exits={
                Direction.WEST: "maze_1",
                Direction.NORTH: "maze_2",
                Direction.SOUTH: "maze_3"
            }
        )
        
        self.rooms["maze_5"] = Room(
            id="maze_5",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.EAST: "dead_end_1",
                Direction.NORTH: "maze_6",
                Direction.DOWN: "maze_3"
            }
        )
        
        self.rooms["maze_6"] = Room(
            id="maze_6",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_7",
                Direction.EAST: "maze_7",
                Direction.WEST: "maze_7",
                Direction.UP: "maze_9"
            }
        )
        
        self.rooms["maze_7"] = Room(
            id="maze_7",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.UP: "maze_14",
                Direction.WEST: "maze_6",
                Direction.NE: "dead_end_1",
                Direction.EAST: "maze_8",
                Direction.SOUTH: "maze_15"
            }
        )
        
        self.rooms["maze_8"] = Room(
            id="maze_8",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.NE: "maze_7",
                Direction.WEST: "maze_8",
                Direction.SE: "dead_end_2"
            }
        )
        
        self.rooms["maze_9"] = Room(
            id="maze_9",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_6",
                Direction.SOUTH: "maze_10",
                Direction.EAST: "maze_12",
                Direction.WEST: "maze_13",
                Direction.NORTH: "maze_11"
            }
        )
        
        self.rooms["maze_10"] = Room(
            id="maze_10",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.EAST: "maze_9",
                Direction.WEST: "maze_13",
                Direction.UP: "maze_5"
            }
        )
        
        self.rooms["maze_11"] = Room(
            id="maze_11",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_12",
                Direction.SW: "grating_room",
                Direction.EAST: "maze_13",
                Direction.WEST: "maze_11",
                Direction.UP: "maze_9"
            }
        )
        
        self.rooms["maze_12"] = Room(
            id="maze_12",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.UP: "maze_11",
                Direction.SW: "maze_5",
                Direction.EAST: "maze_9",
                Direction.DOWN: "dead_end_1",
                Direction.NORTH: "maze_13"
            }
        )
        
        self.rooms["maze_13"] = Room(
            id="maze_13",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_12",
                Direction.WEST: "maze_11",
                Direction.NE: "grating_room",
                Direction.SOUTH: "maze_10",
                Direction.EAST: "maze_9"
            }
        )
        
        self.rooms["maze_14"] = Room(
            id="maze_14",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_15",
                Direction.NE: "maze_7",
                Direction.NW: "maze_15"
            }
        )
        
        self.rooms["maze_15"] = Room(
            id="maze_15",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_14",
                Direction.SOUTH: "cyclops_room",
                Direction.NE: "maze_7"
            }
        )
        
        self.rooms["dead_end_1"] = Room(
            id="dead_end_1",
            name="Dead End",
            description="You have come to a dead end in the maze.",
            flags=0,
            exits={
                Direction.SOUTH: "maze_11"
            }
        )
        
        self.rooms["dead_end_2"] = Room(
            id="dead_end_2",
            name="Dead End",
            description="You have come to a dead end in the maze.",
            flags=0,
            exits={
                Direction.NW: "maze_8"
            }
        )
        
        self.rooms["grating_room"] = Room(
            id="grating_room",
            name="Grating Room",
            description="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating locked with a skull-and-crossbones lock.",
            flags=0,
            exits={
                Direction.SW: "maze_11",
                Direction.NE: "maze_13",
                Direction.UP: "clearing"  # Only if grating unlocked
            }
        )
        
        # Cyclops and Treasure Room
        self.rooms["cyclops_room"] = Room(
            id="cyclops_room",
            name="Cyclops Room",
            description="This room has an exit on the west side, and a staircase leading up. A cyclops, who looks prepared to eat horses (much less mere adventurers), blocks the staircase. From his state of health, and the bloodstains on the walls, you gather that he is not very friendly, though he likes people.",
            flags=0,
            exits={
                Direction.WEST: "maze_15",
                Direction.UP: "treasure_room"  # Only if cyclops gone
            }
        )
        
        self.rooms["treasure_room"] = Room(
            id="treasure_room",
            name="Treasure Room",
            description="This is a large room, whose north wall is solid granite. A number of discarded bags, which crumble at your touch, are scattered about on the floor. There is an exit down and what appears to be a chimney in the east corner of the room.",
            flags=0,
            exits={
                Direction.DOWN: "cyclops_room",
                Direction.EAST: "strange_passage"
            }
        )
        
        self.rooms["strange_passage"] = Room(
            id="strange_passage",
            name="Strange Passage",
            description="This is a long passage. To the west is one entrance. On the east there is an old wooden door, with a large opening in it (about cyclops sized).",
            flags=0,
            exits={
                Direction.WEST: "treasure_room",
                Direction.EAST: "living_room"  # Through door
            }
        )
        
        # Gallery and Studio
        self.rooms["east_of_chasm"] = Room(
            id="east_of_chasm",
            name="East of Chasm",
            description="You are on the east edge of a chasm, the bottom of which cannot be seen. A narrow passage goes north, and the path you are on continues to the east.",
            flags=0,
            exits={
                Direction.NORTH: "cellar",
                Direction.EAST: "gallery"
            }
        )
        
        self.rooms["gallery"] = Room(
            id="gallery",
            name="Gallery",
            description="This is an art gallery. Most of the paintings have been stolen by vandals with exceptional taste. The vandals left through the north, south, east, or west exit.",
            flags=0,
            exits={
                Direction.NORTH: "studio",
                Direction.SOUTH: "east_of_chasm",
                Direction.EAST: "studio",
                Direction.WEST: "east_of_chasm"
            }
        )
        
        self.rooms["studio"] = Room(
            id="studio",
            name="Studio",
            description="This appears to have been an artist's studio. The walls and floors are splattered with paints of 69 different colors. Strangely enough, nothing of value is hanging here. At the north and northwest of the room are small doors.",
            flags=0,
            exits={
                Direction.SOUTH: "gallery",
                Direction.NORTH: "gallery",
                Direction.UP: "kitchen"  # Through chimney
            }
        )
        
        # Temple Area
        self.rooms["engravings_cave"] = Room(
            id="engravings_cave",
            name="Engravings Cave",
            description="You have entered a low cave with passages leading northwest and east. There are old engravings on the walls here.",
            flags=0,
            exits={
                Direction.NW: "round_room",
                Direction.EAST: "dome_room"
            }
        )
        
        self.rooms["dome_room"] = Room(
            id="dome_room",
            name="Dome Room",
            description="You are at the periphery of a large dome, which forms the ceiling of another room below. Protecting you from a precipitous drop is a wooden railing which circles the dome.",
            flags=0,
            exits={
                Direction.WEST: "engravings_cave",
                Direction.DOWN: "torch_room"  # Via rope
            }
        )
        
        self.rooms["torch_room"] = Room(
            id="torch_room",
            name="Torch Room",
            description="This is a large room with a prominent doorway leading to a down staircase. Above you is a large dome. Up around the edge of the dome (20 feet up) is a wooden railing. In the center of the room sits a white marble pedestal.",
            flags=0,
            exits={
                Direction.SOUTH: "temple",
                Direction.DOWN: "north_temple",
                Direction.UP: "dome_room"  # Via rope
            }
        )
        
        self.rooms["temple"] = Room(
            id="temple",
            name="Temple",
            description="This is the north end of a large temple. On the east wall is an ancient inscription, probably a prayer in a long-forgotten language. Below the prayer is a staircase leading down. The west wall is solid granite. The exit to the north end of the temple is through huge marble pillars.",
            flags=0,
            exits={
                Direction.NORTH: "torch_room",
                Direction.EAST: "egyptian_room",
                Direction.DOWN: "egyptian_room",
                Direction.SOUTH: "altar"
            }
        )
        
        self.rooms["altar"] = Room(
            id="altar",
            name="Altar",
            description="This is the south end of a large temple. In front of you is what appears to be an altar. In one corner is a small hole in the floor which leads into darkness. You probably could not get back up it.",
            flags=0,
            exits={
                Direction.NORTH: "temple",
                Direction.DOWN: "cave_1"  # One way
            }
        )
        
        self.rooms["egyptian_room"] = Room(
            id="egyptian_room",
            name="Egyptian Room",
            description="This is a room which looks like an Egyptian tomb. There is an ascending staircase to the west.",
            flags=0,
            exits={
                Direction.WEST: "temple",
                Direction.UP: "temple"
            }
        )
        
        self.rooms["north_temple"] = Room(
            id="north_temple",
            name="North Temple",
            description="This is a room of large proportions filled with religious objects, paintings, and a digital clock which has stopped. There is a door to the west and a staircase leading up.",
            flags=0,
            exits={
                Direction.UP: "torch_room",
                Direction.WEST: "entrance_to_hades",
                Direction.SOUTH: "south_temple"
            }
        )
        
        self.rooms["south_temple"] = Room(
            id="south_temple",
            name="South Temple",
            description="This is the south end of a large temple. There is a door to the west, and a staircase leading up. The door is barred from the other side.",
            flags=0,
            exits={
                Direction.NORTH: "north_temple",
                Direction.UP: "treasure_room",
                Direction.WEST: "south_temple"  # Barred
            }
        )
        
        # Land of the Dead
        self.rooms["entrance_to_hades"] = Room(
            id="entrance_to_hades",
            name="Entrance to Hades",
            description="You are outside a large gate, on which is inscribed:\n\n\"Abandon every hope, all ye who enter here!\"\n\nThe gate is open; through it you can see a desolation, with a pile of mangled bodies in one corner. Thousands of voices, lamenting some hideous fate, can be heard. The way through the gate is barred by evil spirits, who jeer at your attempts to pass.",
            flags=0,
            exits={
                Direction.NORTH: "cave_1",
                Direction.UP: "cave_2",
                Direction.SOUTH: "land_of_the_dead",  # Blocked by spirits unless exorcised
                Direction.EAST: "north_temple"
            }
        )
        
        self.rooms["land_of_the_dead"] = Room(
            id="land_of_the_dead",
            name="Land of the Living Dead",
            description="You have entered the Land of the Living Dead. Thousands of lost souls can be heard weeping and moaning. In the corner are stacked the remains of dozens of previous adventurers less fortunate than yourself. A passage exits to the north.",
            flags=0,
            exits={
                Direction.NORTH: "entrance_to_hades"
            }
        )
        
    def _init_objects(self):
        """Initialize all objects"""
        
        # Basic Items
        self.objects["mailbox"] = GameObject(
            id="mailbox",
            name="mailbox",
            description="small mailbox",
            examine_text="It's a small mailbox.",
            flags=ObjectFlag.CONTAINER.value | ObjectFlag.CLOSED.value,
            location="west_of_house"
        )
        
        self.objects["leaflet"] = GameObject(
            id="leaflet", 
            name="leaflet",
            description="leaflet",
            examine_text="\"WELCOME TO ZORK!\n\nZORK is a game of adventure, danger, and low cunning. In it you will explore some of the most amazing territory ever seen by mortals. No computer should be without one!\"",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="mailbox",
            size=1
        )
        
        self.objects["mat"] = GameObject(
            id="mat",
            name="mat", 
            description="welcome mat",
            examine_text="Welcome to Zork!",
            initial_text="A rubber mat saying 'Welcome to Zork!' lies by the door.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="west_of_house",
            size=2
        )
        
        # Light Sources
        self.objects["lamp"] = GameObject(
            id="lamp",
            name="lamp",
            description="brass lantern",
            examine_text="It is a shiny brass lamp. It is not currently lit.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TURNNABLE.value,
            location="living_room",
            size=3
        )
        
        self.objects["torch"] = GameObject(
            id="torch",
            name="torch",
            description="ivory torch",
            examine_text="The torch is ivory-colored, inlaid with gold.",
            initial_text="Sitting on the pedestal is a flaming torch, made of ivory.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.LIGHT.value | ObjectFlag.TURNEDON.value | ObjectFlag.FLAMMABLE.value | ObjectFlag.TREASURE.value,
            location="torch_room",
            size=2,
            value=14
        )
        
        self.objects["candles"] = GameObject(
            id="candles",
            name="candles",
            description="pair of candles",
            examine_text="The candles are not lit.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.FLAMMABLE.value,
            location="altar",
            size=2
        )
        
        self.objects["matchbook"] = GameObject(
            id="matchbook",
            name="matchbook",
            description="matchbook",
            examine_text="The matchbook is from the Borphee Grill. You have 5 matches.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="dam_lobby",
            size=1
        )
        
        # Weapons
        self.objects["sword"] = GameObject(
            id="sword",
            name="sword",
            description="elvish sword",
            examine_text="It's an elvish sword of great antiquity. It glows with a faint blue glow.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="living_room",
            size=3
        )
        
        self.objects["knife"] = GameObject(
            id="knife",
            name="knife",
            description="nasty knife",
            examine_text="It's a nasty-looking knife.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="attic",
            size=1
        )
        
        self.objects["axe"] = GameObject(
            id="axe",
            name="axe",
            description="bloody axe",
            examine_text="It's a bloody axe.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location=None,  # Troll has it initially
            size=3
        )
        
        self.objects["stiletto"] = GameObject(
            id="stiletto",
            name="stiletto",
            description="stiletto",
            examine_text="It's a vicious stiletto.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location=None,  # Thief has it
            size=1
        )
        
        self.objects["rusty_knife"] = GameObject(
            id="rusty_knife",
            name="knife",
            description="rusty knife",
            examine_text="It's a rusty knife.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="maze_4",
            size=1
        )
        
        # Tools
        self.objects["rope"] = GameObject(
            id="rope",
            name="rope",
            description="rope",
            examine_text="It's a sturdy hemp rope.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="attic",
            size=2
        )
        
        self.objects["shovel"] = GameObject(
            id="shovel",
            name="shovel",
            description="shovel",
            examine_text="It's a sturdy shovel.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="white_cliffs_beach_south",
            size=3
        )
        
        self.objects["screwdriver"] = GameObject(
            id="screwdriver",
            name="screwdriver",
            description="screwdriver",
            examine_text="It's a flathead screwdriver.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="maintenance_room",
            size=1
        )
        
        self.objects["wrench"] = GameObject(
            id="wrench",
            name="wrench",
            description="wrench",
            examine_text="It's a large adjustable wrench.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="maintenance_room",
            size=2
        )
        
        self.objects["pump"] = GameObject(
            id="pump",
            name="pump",
            description="hand-held air pump",
            examine_text="It's a hand-held air pump for inflating things.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="gas_room",
            size=2
        )
        
        # Containers
        self.objects["bottle"] = GameObject(
            id="bottle",
            name="bottle",
            description="glass bottle",
            examine_text="The glass bottle contains:\n  A quantity of water",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.TRANSPARENT.value,
            location="kitchen",
            size=2
        )
        
        self.objects["water"] = GameObject(
            id="water",
            name="water",
            description="quantity of water",
            flags=ObjectFlag.DRINKABLE.value,
            location="bottle",
            size=1
        )
        
        self.objects["sack"] = GameObject(
            id="sack",
            name="sack",
            description="brown sack",
            examine_text="The brown sack contains:\n  A lunch\n  A clove of garlic",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.OPEN.value,
            location="kitchen",
            size=2,
            capacity=9
        )
        
        self.objects["lunch"] = GameObject(
            id="lunch",
            name="lunch",
            description="lunch",
            examine_text="It looks like a tasty lunch.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.EDIBLE.value,
            location="sack",
            size=2
        )
        
        self.objects["garlic"] = GameObject(
            id="garlic",
            name="garlic",
            description="clove of garlic",
            examine_text="It's a clove of garlic. It smells terribly.",
            flags=ObjectFlag.TAKEABLE.value,
            location="sack",
            size=1
        )
        
        self.objects["bag"] = GameObject(
            id="bag",
            name="bag",
            description="leather bag of coins",
            examine_text="The leather bag is filled with gold coins.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.OPEN.value | ObjectFlag.TREASURE.value,
            location="maze_5",
            size=3,
            value=10
        )
        
        self.objects["basket"] = GameObject(
            id="basket",
            name="basket",
            description="wicker basket",
            examine_text="It's a wicker basket.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.OPEN.value,
            location="shaft_room",
            size=3,
            capacity=5
        )
        
        # Special Objects
        self.objects["case"] = GameObject(
            id="case",
            name="case",
            description="trophy case",
            examine_text="The trophy case is empty.",
            flags=ObjectFlag.CONTAINER.value | ObjectFlag.OPEN.value | ObjectFlag.TRANSPARENT.value | ObjectFlag.SACRED.value,
            location="living_room",
            capacity=30
        )
        
        self.objects["rug"] = GameObject(
            id="rug",
            name="rug",
            description="large oriental rug",
            examine_text="The rug is extremely heavy and cannot be carried.",
            initial_text="A large oriental rug covers the floor.",
            flags=ObjectFlag.VISIBLE.value,
            location="living_room"
        )
        
        self.objects["trap_door"] = GameObject(
            id="trap_door",
            name="door",
            description="trap door",
            examine_text="The trap door is closed.",
            flags=ObjectFlag.DOOR.value | ObjectFlag.CLOSED.value,
            location=None  # Hidden until rug moved
        )
        
        self.objects["window"] = GameObject(
            id="window",
            name="window",
            description="small window",
            examine_text="The window is slightly ajar, but not enough to allow entry.",
            flags=ObjectFlag.VISIBLE.value,
            location="behind_house"
        )
        
        self.objects["chimney"] = GameObject(
            id="chimney",
            name="chimney",
            description="chimney",
            examine_text="The chimney leads down.",
            flags=ObjectFlag.VISIBLE.value,
            location="kitchen"
        )
        
        self.objects["leaves"] = GameObject(
            id="leaves",
            name="leaves",
            description="pile of leaves",
            examine_text="The leaves are turning brown, indicating autumn.",
            flags=ObjectFlag.VISIBLE.value,
            location="clearing"
        )
        
        self.objects["grating"] = GameObject(
            id="grating",
            name="grating",
            description="grating",
            examine_text="The grating is locked.",
            flags=ObjectFlag.DOOR.value | ObjectFlag.LOCKED.value | ObjectFlag.CLOSED.value,
            location=None  # Hidden initially
        )
        
        self.objects["skeleton_key"] = GameObject(
            id="skeleton_key",
            name="key",
            description="skeleton key",
            examine_text="It's a skeleton key.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="maze_4",
            size=1
        )
        
        self.objects["skeleton"] = GameObject(
            id="skeleton",
            name="skeleton",
            description="skeleton",
            examine_text="A skeleton is lying in the corner.",
            flags=ObjectFlag.VISIBLE.value,
            location="maze_4"
        )
        
        self.objects["useless_lantern"] = GameObject(
            id="useless_lantern",
            name="lantern",
            description="broken brass lantern",
            examine_text="It's a broken brass lantern. It won't light.",
            flags=ObjectFlag.TAKEABLE.value,
            location="maze_4",
            size=3
        )
        
        self.objects["chain"] = GameObject(
            id="chain",
            name="chain",
            description="heavy chain",
            examine_text="It's a heavy iron chain.",
            flags=ObjectFlag.VISIBLE.value,
            location="shaft_room"
        )
        
        self.objects["timber"] = GameObject(
            id="timber",
            name="timber",
            description="broken timber",
            examine_text="It's a broken piece of timber.",
            flags=ObjectFlag.TAKEABLE.value,
            location="timber_room",
            size=3
        )
        
        self.objects["pile_of_coal"] = GameObject(
            id="pile_of_coal",
            name="coal",
            description="small pile of coal",
            examine_text="It's a small pile of coal.",
            flags=ObjectFlag.TAKEABLE.value,
            location="dead_end_coal_mine",
            size=2
        )
        
        self.objects["machine"] = GameObject(
            id="machine",
            name="machine",
            description="machine",
            examine_text="It's a complex machine with a large lid and a small switch.",
            flags=ObjectFlag.VISIBLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.CLOSED.value,
            location="machine_room",
            capacity=5
        )
        
        self.objects["switch"] = GameObject(
            id="switch",
            name="switch",
            description="switch",
            examine_text="It's a small switch labelled \"START\".",
            flags=ObjectFlag.VISIBLE.value,
            location="machine_room"
        )
        
        # Dam Controls
        self.objects["control_panel"] = GameObject(
            id="control_panel",
            name="panel",
            description="control panel",
            examine_text="The panel has a large green button marked \"Open Sluice Gate\" and a large red button marked \"Close Sluice Gate\".",
            flags=ObjectFlag.VISIBLE.value,
            location="dam"
        )
        
        self.objects["green_button"] = GameObject(
            id="green_button",
            name="button",
            description="green button",
            examine_text="It's a large green button marked \"Open Sluice Gate\".",
            flags=ObjectFlag.VISIBLE.value,
            location="dam"
        )
        
        self.objects["red_button"] = GameObject(
            id="red_button",
            name="button",
            description="red button",
            examine_text="It's a large red button marked \"Close Sluice Gate\".",
            flags=ObjectFlag.VISIBLE.value,
            location="dam"
        )
        
        self.objects["guidebook"] = GameObject(
            id="guidebook",
            name="guidebook",
            description="tour guidebook",
            examine_text="\"Flood Control Dam #3 was constructed in 783 GUE with a grant of 37 million zorkmids from Lord Dimwit Flathead the Excessive...\"",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="dam_lobby",
            size=1
        )
        
        # Temple Objects
        self.objects["bell"] = GameObject(
            id="bell",
            name="bell",
            description="brass bell",
            examine_text="It's a small brass bell.",
            flags=ObjectFlag.TAKEABLE.value,
            location="temple",
            size=2
        )
        
        self.objects["book"] = GameObject(
            id="book",
            name="book",
            description="black book",
            examine_text="The book is written in an ancient language. Some of the text is readable:\n\n\"...seek ye the Black Crystal of Night which was lost in the Land of the Living Dead...\"",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value | ObjectFlag.SACRED.value,
            location="altar",
            size=2
        )
        
        self.objects["prayer"] = GameObject(
            id="prayer",
            name="prayer",
            description="ancient prayer",
            examine_text="The prayer is inscribed in an ancient script. It appears to be a powerful exorcism ritual.",
            flags=ObjectFlag.READABLE.value,
            location="temple"
        )
        
        # Mirror Objects
        self.objects["mirror_south"] = GameObject(
            id="mirror_south",
            name="mirror",
            description="mirror",
            examine_text="You see yourself in the mirror.",
            flags=ObjectFlag.VISIBLE.value,
            location="mirror_room_south"
        )
        
        self.objects["mirror_north"] = GameObject(
            id="mirror_north",
            name="mirror",
            description="mirror",
            examine_text="You see yourself in the mirror.",
            flags=ObjectFlag.VISIBLE.value,
            location="mirror_room_north"
        )
        
        # Treasures
        self.objects["jeweled_egg"] = GameObject(
            id="jeweled_egg",
            name="egg",
            description="jewel-encrusted egg",
            examine_text="The egg is covered with fine gold inlay and ornamented in lapis lazuli and mother-of-pearl. Unlike most eggs, this one is hinged and closed with a delicate looking clasp. The egg appears extremely fragile.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.CLOSED.value | ObjectFlag.TREASURE.value,
            location="up_tree",
            size=2,
            value=5
        )
        
        self.objects["golden_canary"] = GameObject(
            id="golden_canary",
            name="canary",
            description="golden clockwork canary",
            examine_text="The golden clockwork canary is a tiny mechanical bird made of gold. It appears to have a winding key.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="jeweled_egg",
            size=1,
            value=6
        )
        
        self.objects["painting"] = GameObject(
            id="painting",
            name="painting",
            description="painting",
            examine_text="The painting is of unparalleled beauty. It depicts a gentleman on horseback.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value | ObjectFlag.FLAMMABLE.value,
            location="gallery",
            size=4,
            value=4
        )
        
        self.objects["sceptre"] = GameObject(
            id="sceptre",
            name="sceptre",
            description="sceptre",
            examine_text="The sceptre is ornamented with colored enamel and jewels.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location=None,  # In coffin
            size=2,
            value=4
        )
        
        self.objects["coffin"] = GameObject(
            id="coffin",
            name="coffin",
            description="gold coffin",
            examine_text="The gold coffin is closed.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.CONTAINER.value | ObjectFlag.CLOSED.value | ObjectFlag.SACRED.value | ObjectFlag.TREASURE.value,
            location="egyptian_room",
            size=6,
            value=10
        )
        
        self.objects["trunk"] = GameObject(
            id="trunk",
            name="trunk",
            description="trunk of jewels",
            examine_text="The trunk is filled with jewels of every type, size, and color.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location=None,  # Appears when reservoir drained
            size=5,
            value=14
        )
        
        self.objects["crystal_trident"] = GameObject(
            id="crystal_trident",
            name="trident",
            description="crystal trident",
            examine_text="The trident is made of pure crystal and gleams with an inner light.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="atlantis_room",
            size=3,
            value=4
        )
        
        self.objects["jade_figurine"] = GameObject(
            id="jade_figurine",
            name="figurine",
            description="jade figurine",
            examine_text="The figurine is of a small green elephant. It is exquisitely crafted.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="bat_room",
            size=1,
            value=5
        )
        
        self.objects["sapphire_bracelet"] = GameObject(
            id="sapphire_bracelet",
            name="bracelet",
            description="sapphire bracelet",
            examine_text="The bracelet is made of hundreds of tiny sapphires.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="gas_room",
            size=1,
            value=5
        )
        
        self.objects["chalice"] = GameObject(
            id="chalice",
            name="chalice",
            description="silver chalice",
            examine_text="The silver chalice is intricately engraved.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="treasure_room",
            size=2,
            value=10
        )
        
        self.objects["pot_of_gold"] = GameObject(
            id="pot_of_gold",
            name="gold",
            description="pot of gold",
            examine_text="The pot is filled with gold pieces. It must be worth a fortune!",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="end_of_rainbow",
            size=4,
            value=10
        )
        
        self.objects["platinum_bar"] = GameObject(
            id="platinum_bar",
            name="bar",
            description="platinum bar",
            examine_text="The platinum bar is extremely heavy.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="loud_room",
            size=5,
            value=10
        )
        
        self.objects["crystal_skull"] = GameObject(
            id="crystal_skull",
            name="skull",
            description="crystal skull",
            examine_text="The crystal skull grins at you menacingly. Its eyes seem to follow your movements.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="land_of_the_dead",
            size=2,
            value=10
        )
        
        self.objects["jeweled_scarab"] = GameObject(
            id="jeweled_scarab",
            name="scarab",
            description="beautiful jeweled scarab",
            examine_text="The scarab is covered with precious jewels.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location=None,  # Found by digging
            size=1,
            value=5
        )
        
        self.objects["large_emerald"] = GameObject(
            id="large_emerald",
            name="emerald",
            description="large emerald",
            examine_text="The emerald is exceptionally large and perfectly cut.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location="white_cliffs_beach_south",
            size=1,
            value=5
        )
        
        self.objects["diamond"] = GameObject(
            id="diamond",
            name="diamond",
            description="huge diamond",
            examine_text="The diamond is enormous! It catches the light beautifully.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
            location=None,  # Created by machine from coal
            size=1,
            value=10
        )
        
        # Put sceptre in coffin
        self.objects["sceptre"].location = "coffin"
        
    def _init_actors(self):
        """Initialize NPCs"""
        
        self.actors["troll"] = Actor(
            id="troll",
            name="troll",
            description="A nasty-looking troll, brandishing a bloody axe, blocks all passages out of the room.",
            location="troll_room",
            health=100,
            hostile=True,
            messages={
                "first_encounter": "A nasty-looking troll, brandishing a bloody axe, blocks all passages out of the room.",
                "fight": "The troll swings his axe at you!",
                "death": "The troll collapses to the floor, dead.",
                "payment": "The troll, satisfied with his payment, retreats to the north.",
                "axe_thrown": "The troll, disarmed, cowers in terror, pleading for his life."
            }
        )
        
        self.actors["thief"] = Actor(
            id="thief",
            name="thief",
            description="A seedy-looking individual with a large bag just wandered through the room.",
            location=None,  # Appears randomly
            health=100,
            hostile=False,
            messages={
                "first_encounter": "Someone carrying a large bag is casually leaning against one of the walls here.",
                "fight": "The thief nimbly avoids your attack.",
                "steal": "The thief skillfully relieves you of",
                "death": "The thief drops his bag and falls to the floor, dead.",
                "stiletto": "The thief stabs you with his stiletto!",
                "engrossed": "The thief is engrossed in his booty and doesn't notice you."
            }
        )
        
        self.actors["cyclops"] = Actor(
            id="cyclops",
            name="cyclops",
            description="A cyclops, who looks prepared to eat horses (much less mere adventurers), blocks the staircase.",
            location="cyclops_room",
            health=200,
            hostile=True,
            messages={
                "first_encounter": "A cyclops, who looks prepared to eat horses (much less mere adventurers), blocks the staircase.",
                "fight": "The cyclops swings his massive fist at you!",
                "hungry": "The cyclops is hungry and blocking the staircase.",
                "flees": "The cyclops, hearing the name of his master, flees the room by knocking down the wall on the east of the room!",
                "odysseus": "\"Do you think I'm as stupid as my father was?\" he says, and hits you with a crushing blow."
            }
        )
        
        self.actors["spirits"] = Actor(
            id="spirits",
            name="spirits",
            description="Evil spirits guard the entrance to Hades.",
            location="entrance_to_hades",
            health=999,  # Can't be killed
            hostile=False,
            messages={
                "block": "Some invisible force prevents you from passing through the gate.",
                "ceremony": "The spirits, sensing the power of the ceremony, flee in terror!",
                "exorcise": "The bell, book, and candles perform an exorcism, banishing the evil spirits!"
            }
        )
        
        self.actors["bat"] = Actor(
            id="bat",
            name="bat",
            description="A large vampire bat is hanging from the ceiling.",
            location="bat_room",
            health=10,
            hostile=False,
            messages={
                "first_encounter": "In the corner of the room on the ceiling is a large vampire bat who is obviously deranged and holding his nose.",
                "garlic": "The bat, upon seeing the garlic, squeaks in terror and flies away!",
                "flies": "The bat flies around the room."
            }
        )
        
    def start(self):
        """Start the game"""
        self._show_intro()
        
        # Get player name
        name = input("What is your name, adventurer? ").strip()
        if name:
            self.player_name = name
            print(f"\nWelcome, {self.player_name}!")
        else:
            print(f"\nWelcome, Adventurer!")
        
        print()
        self._look()
        
        # Give troll his axe
        self.objects["axe"].location = "troll"
        
        # Main game loop
        while not self.game_over:
            try:
                # Check for random events
                self._check_random_events()
                
                # Get input
                user_input = input("> ").strip().lower()
                
                if not user_input:
                    continue
                    
                # Parse and execute command
                command = self._parse_command(user_input)
                self._execute_command(command)
                
                # Increment moves
                self.moves += 1
                
                # Update lamp life
                if self.lamp_on:
                    self.lamp_life -= 1
                    if self.lamp_life == 30:
                        print("Your lamp is getting dim.")
                    elif self.lamp_life == 0:
                        print("Your lamp has run out of power.")
                        self.lamp_on = False
                        self.objects["lamp"].set_flag(ObjectFlag.LIGHT, False)
                        self.objects["lamp"].set_flag(ObjectFlag.TURNEDON, False)
                        self._check_light()
                
            except KeyboardInterrupt:
                print("\nUse QUIT to exit.")
            except EOFError:
                self.game_over = True
                
    def _show_intro(self):
        """Show game intro"""
        print("ZORK I: The Great Underground Empire")
        print("Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.")
        print("ZORK is a registered trademark of Infocom, Inc.")
        print("Revision 88 / Serial number 840726")
        print()
        
    def _parse_command(self, user_input: str) -> ParsedCommand:
        """Parse user input into a command"""
        command = ParsedCommand(raw_input=user_input)
        words = user_input.split()
        
        if not words:
            return command
            
        # Check for direction shortcuts
        direction_map = {
            "n": Direction.NORTH, "north": Direction.NORTH,
            "s": Direction.SOUTH, "south": Direction.SOUTH,
            "e": Direction.EAST, "east": Direction.EAST,
            "w": Direction.WEST, "west": Direction.WEST,
            "ne": Direction.NE, "northeast": Direction.NE,
            "nw": Direction.NW, "northwest": Direction.NW,
            "se": Direction.SE, "southeast": Direction.SE,
            "sw": Direction.SW, "southwest": Direction.SW,
            "u": Direction.UP, "up": Direction.UP,
            "d": Direction.DOWN, "down": Direction.DOWN,
            "in": Direction.IN, "enter": Direction.IN,
            "out": Direction.OUT, "exit": Direction.OUT
        }
        
        if words[0] in direction_map:
            command.direction = direction_map[words[0]]
            return command
            
        # Parse verbs
        verb_map = {
            "take": VerbType.TAKE, "get": VerbType.TAKE, "pick": VerbType.TAKE,
            "drop": VerbType.DROP, "throw": VerbType.DROP, "put": VerbType.DROP,
            "open": VerbType.OPEN,
            "close": VerbType.CLOSE, "shut": VerbType.CLOSE,
            "examine": VerbType.EXAMINE, "x": VerbType.EXAMINE, "look": VerbType.EXAMINE,
            "l": VerbType.LOOK,
            "inventory": VerbType.INVENTORY, "i": VerbType.INVENTORY,
            "quit": VerbType.QUIT, "q": VerbType.QUIT,
            "save": VerbType.SAVE,
            "restore": VerbType.RESTORE, "load": VerbType.RESTORE,
            "restart": VerbType.RESTART,
            "score": VerbType.SCORE,
            "version": VerbType.VERSION,
            "verbose": VerbType.VERBOSE,
            "brief": VerbType.BRIEF,
            "wait": VerbType.WAIT, "z": VerbType.WAIT,
            "turn": VerbType.TURN,
            "light": VerbType.TURN_ON,
            "extinguish": VerbType.TURN_OFF,
            "move": VerbType.MOVE, "push": VerbType.PUSH,
            "read": VerbType.READ,
            "attack": VerbType.ATTACK, "kill": VerbType.KILL, "fight": VerbType.ATTACK,
            "eat": VerbType.EAT,
            "drink": VerbType.DRINK,
            "break": VerbType.BREAK, "smash": VerbType.BREAK,
            "diagnose": VerbType.DIAGNOSE,
            "give": VerbType.GIVE,
            "unlock": VerbType.UNLOCK,
            "lock": VerbType.LOCK,
            "tie": VerbType.TIE,
            "untie": VerbType.UNTIE,
            "burn": VerbType.BURN, "light": VerbType.BURN,
            "extinguish": VerbType.EXTINGUISH,
            "ring": VerbType.RING,
            "wind": VerbType.WIND,
            "dig": VerbType.DIG,
            "fill": VerbType.FILL,
            "pour": VerbType.POUR,
            "pray": VerbType.PRAY,
            "wave": VerbType.WAVE,
            "raise": VerbType.RAISE,
            "lower": VerbType.LOWER,
            "climb": VerbType.CLIMB,
            "jump": VerbType.JUMP
        }
        
        verb_word = words[0]
        if verb_word in verb_map:
            command.verb = verb_map[verb_word]
            
            # Parse objects if present
            if len(words) > 1:
                # Handle multi-word commands
                remaining = " ".join(words[1:])
                
                # Special case for "look at X"
                if command.verb == VerbType.EXAMINE and remaining.startswith("at "):
                    remaining = remaining[3:]
                    
                # Special case for "turn on/off"
                if command.verb == VerbType.TURN:
                    if remaining.startswith("on "):
                        command.verb = VerbType.TURN_ON
                        remaining = remaining[3:]
                    elif remaining.startswith("off "):
                        command.verb = VerbType.TURN_OFF
                        remaining = remaining[4:]
                        
                # Special case for "pick up"
                if command.verb == VerbType.TAKE and remaining.startswith("up "):
                    remaining = remaining[3:]
                    
                # Find direct object
                command.direct_object = self._find_object(remaining)
                
        return command
        
    def _find_object(self, name: str) -> Optional[str]:
        """Find an object by name"""
        # Also check actors
        for actor_id, actor in self.actors.items():
            if actor.location == self.current_room and actor_id == name:
                return actor_id
                
        # Check for exact matches first
        for obj_id, obj in self.objects.items():
            if obj.name == name and self._is_visible(obj_id):
                return obj_id
                
        # Check for partial matches
        for obj_id, obj in self.objects.items():
            if name in obj.name and self._is_visible(obj_id):
                return obj_id
                
        # Check for description matches
        for obj_id, obj in self.objects.items():
            if name in obj.description and self._is_visible(obj_id):
                return obj_id
                
        return None
        
    def _is_visible(self, obj_id: str) -> bool:
        """Check if object is visible to player"""
        obj = self.objects.get(obj_id)
        if not obj:
            return False
            
        # In inventory
        if obj_id in self.player_inventory:
            return True
            
        # In current room
        if obj.location == self.current_room:
            return True
            
        # In open container in room or inventory
        if obj.location:
            container = self.objects.get(obj.location)
            if container and container.has_flag(ObjectFlag.CONTAINER):
                if (container.has_flag(ObjectFlag.OPEN) or 
                    container.has_flag(ObjectFlag.TRANSPARENT)):
                    if container.location == self.current_room or container.id in self.player_inventory:
                        return True
                        
        return False
        
    def _execute_command(self, command: ParsedCommand):
        """Execute a parsed command"""
        # Handle movement
        if command.direction:
            self._go(command.direction)
            return
            
        # Handle verbs
        if not command.verb:
            print("I don't understand that.")
            return
            
        # Dispatch to appropriate handler
        handlers = {
            VerbType.LOOK: self._look,
            VerbType.EXAMINE: self._examine,
            VerbType.TAKE: self._take,
            VerbType.DROP: self._drop,
            VerbType.INVENTORY: self._inventory,
            VerbType.OPEN: self._open,
            VerbType.CLOSE: self._close,
            VerbType.READ: self._read,
            VerbType.TURN_ON: self._turn_on,
            VerbType.TURN_OFF: self._turn_off,
            VerbType.MOVE: self._move,
            VerbType.PUSH: self._push,
            VerbType.ATTACK: self._attack,
            VerbType.EAT: self._eat,
            VerbType.DRINK: self._drink,
            VerbType.QUIT: self._quit,
            VerbType.SAVE: self._save,
            VerbType.RESTORE: self._restore,
            VerbType.RESTART: self._restart,
            VerbType.SCORE: self._score,
            VerbType.VERSION: self._version,
            VerbType.VERBOSE: self._verbose,
            VerbType.BRIEF: self._brief,
            VerbType.WAIT: self._wait,
            VerbType.DIAGNOSE: self._diagnose,
            VerbType.GIVE: self._give,
            VerbType.UNLOCK: self._unlock,
            VerbType.LOCK: self._lock,
            VerbType.TIE: self._tie,
            VerbType.UNTIE: self._untie,
            VerbType.BURN: self._burn,
            VerbType.EXTINGUISH: self._extinguish,
            VerbType.RING: self._ring,
            VerbType.WIND: self._wind,
            VerbType.DIG: self._dig,
            VerbType.FILL: self._fill,
            VerbType.POUR: self._pour,
            VerbType.PRAY: self._pray,
            VerbType.WAVE: self._wave,
            VerbType.RAISE: self._raise,
            VerbType.LOWER: self._lower,
            VerbType.CLIMB: self._climb,
            VerbType.JUMP: self._jump,
            VerbType.BREAK: self._break
        }
        
        handler = handlers.get(command.verb)
        if handler:
            handler(command)
        else:
            print("I don't know how to do that.")
            
    def _go(self, direction: Direction):
        """Move in a direction"""
        room = self.rooms[self.current_room]
        
        # Special cases
        
        # Trap door
        if self.current_room == "living_room" and direction == Direction.DOWN:
            if "trap_door" in [obj.id for obj in self.objects.values() if obj.location == "living_room"]:
                trap_door = self.objects["trap_door"]
                if trap_door.has_flag(ObjectFlag.OPEN):
                    self.current_room = "cellar"
                    self._check_light()
                    self._look()
                else:
                    print("The trap door is closed.")
            else:
                print("You can't go that way.")
            return
            
        # Grating
        if self.current_room == "grating_room" and direction == Direction.UP:
            if self.grating_unlocked:
                self.current_room = "clearing"
                self._look()
            else:
                print("The grating is locked.")
            return
            
        # Window
        if self.current_room == "behind_house" and direction in [Direction.WEST, Direction.IN]:
            if self.objects["window"].has_flag(ObjectFlag.OPEN):
                self.current_room = "kitchen"
                self._look()
            else:
                print("The window is closed.")
            return
            
        # Strange Passage
        if self.current_room == "living_room" and direction == Direction.WEST:
            if not self.cyclops_fled:
                print("The door is nailed shut.")
            else:
                self.current_room = "strange_passage"
                self._look()
            return
            
        # Cyclops blocks stairs
        if self.current_room == "cyclops_room" and direction == Direction.UP:
            cyclops = self.actors["cyclops"]
            if cyclops.location == "cyclops_room" and cyclops.active:
                print("The cyclops blocks the staircase.")
                return
                
        # Troll blocks passages
        if self.current_room == "troll_room":
            troll = self.actors["troll"]
            if troll.location == "troll_room" and troll.active and not self.troll_payment:
                print("The troll blocks your way!")
                return
                
        # Spirits block entrance to Hades
        if self.current_room == "entrance_to_hades" and direction == Direction.SOUTH:
            if not self.spirits_released:
                print(self.actors["spirits"].messages["block"])
                return
                
        # Dam/Reservoir navigation
        if self.current_room == "reservoir":
            if not self.dam_open:
                print("You can't swim in the deep water.")
                return
                
        # Rainbow
        if self.current_room == "end_of_rainbow" and direction == Direction.EAST:
            if not self.rainbow_solid:
                print("Can you walk on water vapor?")
                return
                
        # Slide is one-way
        if self.current_room == "slide_room" and direction == Direction.DOWN:
            print("Wheeeee!")
            self.current_room = "cellar"
            self._look()
            return
            
        # Normal movement
        if direction in room.exits:
            new_room = room.exits[direction]
            if new_room == self.current_room:  # Can't go that way
                print("You can't go that way.")
            else:
                self.current_room = new_room
                self._check_light()
                self._look()
        else:
            print("You can't go that way.")
            
    def _look(self, command: Optional[ParsedCommand] = None):
        """Look around or at something"""
        if command and command.direct_object:
            self._examine(command)
            return
            
        room = self.rooms[self.current_room]
        
        # Check if can see
        if not self._can_see():
            return
            
        # Room name
        if room.id in self.visited_rooms and not self.verbose:
            print(room.name)
        else:
            print(room.name)
            print(room.description)
            
        self.visited_rooms.add(room.id)
        
        # Special room descriptions
        if self.current_room == "loud_room":
            print(f"The sound level is: {self.loud_room_level}")
            
        # Check for actors
        for actor_id, actor in self.actors.items():
            if actor.location == self.current_room and actor.active:
                print(actor.messages.get("first_encounter", actor.description))
                
        # List visible objects
        room_objects = []
        for obj_id, obj in self.objects.items():
            if obj.location == self.current_room:
                # Special handling
                if obj_id == "trap_door":
                    if obj.has_flag(ObjectFlag.OPEN):
                        print("There is an open trap door here.")
                    else:
                        print("There is a closed trap door here.")
                elif obj_id == "grating" and self.objects["leaves"].location != "clearing":
                    continue  # Don't show grating until leaves moved
                elif obj.initial_text and room.id not in self.visited_rooms:
                    print(obj.initial_text)
                else:
                    room_objects.append(obj)
                    
        # List containers' contents
        for obj_id, obj in self.objects.items():
            if obj.location == self.current_room and obj.has_flag(ObjectFlag.CONTAINER):
                if obj.has_flag(ObjectFlag.OPEN) or obj.has_flag(ObjectFlag.TRANSPARENT):
                    contents = [o for o in self.objects.values() if o.location == obj_id]
                    if contents:
                        if obj.has_flag(ObjectFlag.TRANSPARENT):
                            print(f"The {obj.name} contains:")
                        else:
                            print(f"The {obj.name} is open. It contains:")
                        for item in contents:
                            print(f"  A {item.description}")
                            
        # List other objects
        if room_objects:
            for obj in room_objects:
                if obj.id not in ["case", "rug", "window", "control_panel", "prayer", "mirror_south", "mirror_north", "chimney", "chain", "switch", "green_button", "red_button"]:
                    print(f"There is a {obj.description} here.")
                    
    def _examine(self, command: ParsedCommand):
        """Examine an object"""
        if not command.direct_object:
            print("What do you want to examine?")
            return
            
        # Check if it's an actor
        if command.direct_object in self.actors:
            actor = self.actors[command.direct_object]
            if actor.location == self.current_room:
                print(actor.description)
            else:
                print("You don't see that here.")
            return
            
        obj = self.objects[command.direct_object]
        print(obj.examine_text)
        
        # Show contents if container
        if obj.has_flag(ObjectFlag.CONTAINER):
            if obj.has_flag(ObjectFlag.OPEN) or obj.has_flag(ObjectFlag.TRANSPARENT):
                contents = [o for o in self.objects.values() if o.location == obj.id]
                if contents:
                    print(f"The {obj.name} contains:")
                    for item in contents:
                        print(f"  A {item.description}")
                elif obj.has_flag(ObjectFlag.OPEN):
                    print(f"The {obj.name} is empty.")
                    
    def _take(self, command: ParsedCommand):
        """Take an object"""
        if not command.direct_object:
            print("What do you want to take?")
            return
            
        # Can't take actors
        if command.direct_object in self.actors:
            print("The " + command.direct_object + " is too heavy.")
            return
            
        obj_id = command.direct_object
        obj = self.objects[obj_id]
        
        # Check if takeable
        if not obj.has_flag(ObjectFlag.TAKEABLE):
            print("You can't take that.")
            return
            
        # Check if already carried
        if obj_id in self.player_inventory:
            print("You already have that.")
            return
            
        # Check if in a container
        if obj.location in self.objects:
            container = self.objects[obj.location]
            if container.has_flag(ObjectFlag.CONTAINER):
                if not (container.has_flag(ObjectFlag.OPEN) or container.has_flag(ObjectFlag.TRANSPARENT)):
                    print(f"You can't see any {obj.name} here.")
                    return
                    
        # Check inventory limit
        if len(self.player_inventory) >= 7:
            print("Your load is too heavy.")
            return
            
        # Take it
        self.player_inventory.append(obj_id)
        obj.location = "player"
        print("Taken.")
        
        # Special cases
        if obj.has_flag(ObjectFlag.TREASURE):
            self.score += obj.value
            
    def _drop(self, command: ParsedCommand):
        """Drop an object"""
        if not command.direct_object:
            print("What do you want to drop?")
            return
            
        obj_id = command.direct_object
        
        if obj_id not in self.player_inventory:
            print("You don't have that.")
            return
            
        # Drop it
        self.player_inventory.remove(obj_id)
        obj = self.objects[obj_id]
        obj.location = self.current_room
        print("Dropped.")
        
        # Check if dropped in trophy case
        if self.current_room == "living_room":
            case = self.objects["case"]
            if case.has_flag(ObjectFlag.OPEN) and obj.has_flag(ObjectFlag.TREASURE):
                obj.location = "case"
                self.treasures_deposited += 1
                print(f"The {obj.name} is now in the trophy case.")
                self.score += obj.value
                
    def _inventory(self, command: ParsedCommand):
        """Show inventory"""
        if not self.player_inventory:
            print("You are empty-handed.")
        else:
            print("You are carrying:")
            for obj_id in self.player_inventory:
                obj = self.objects[obj_id]
                print(f"  A {obj.description}")
                if obj.has_flag(ObjectFlag.TURNEDON):
                    print("    (providing light)")
                    
    def _open(self, command: ParsedCommand):
        """Open something"""
        if not command.direct_object:
            print("What do you want to open?")
            return
            
        obj_id = command.direct_object
        obj = self.objects[obj_id]
        
        # Special case for window
        if obj_id == "window":
            print("With great effort, you open the window far enough to allow entry.")
            obj.set_flag(ObjectFlag.OPEN, True)
            self.rooms["behind_house"].exits[Direction.WEST] = "kitchen"
            self.rooms["behind_house"].exits[Direction.IN] = "kitchen"
            return
            
        # Special case for egg
        if obj_id == "jeweled_egg":
            if obj.has_flag(ObjectFlag.OPEN):
                print("It's already open.")
            else:
                print("You have neither the tools nor the expertise.")
            return
            
        # Check if openable
        if not (obj.has_flag(ObjectFlag.CONTAINER) or obj.has_flag(ObjectFlag.DOOR)):
            print("You can't open that.")
            return
            
        # Check if already open
        if obj.has_flag(ObjectFlag.OPEN):
            print("It's already open.")
            return
            
        # Check if locked
        if obj.has_flag(ObjectFlag.LOCKED):
            print("It's locked.")
            return
            
        # Open it
        obj.set_flag(ObjectFlag.OPEN, True)
        obj.set_flag(ObjectFlag.CLOSED, False)
        print("Opened.")
        
        # Show contents
        if obj.has_flag(ObjectFlag.CONTAINER):
            contents = [o for o in self.objects.values() if o.location == obj_id]
            if contents:
                print(f"Opening the {obj.name} reveals:")
                for item in contents:
                    print(f"  A {item.description}")
                    
        # Special case for coffin
        if obj_id == "coffin":
            self.coffin_open = True
            
        # Special case for machine
        if obj_id == "machine":
            if self.objects["pile_of_coal"].location == "machine":
                print("The machine comes to life and creates a beautiful diamond!")
                self.objects["diamond"].location = "machine"
                del self.objects["pile_of_coal"]
                
    def _close(self, command: ParsedCommand):
        """Close something"""
        if not command.direct_object:
            print("What do you want to close?")
            return
            
        obj_id = command.direct_object
        obj = self.objects[obj_id]
        
        # Check if closeable
        if not (obj.has_flag(ObjectFlag.CONTAINER) or obj.has_flag(ObjectFlag.DOOR)):
            print("You can't close that.")
            return
            
        # Check if already closed
        if obj.has_flag(ObjectFlag.CLOSED):
            print("It's already closed.")
            return
            
        # Close it
        obj.set_flag(ObjectFlag.OPEN, False)
        obj.set_flag(ObjectFlag.CLOSED, True)
        print("Closed.")
        
    def _read(self, command: ParsedCommand):
        """Read something"""
        if not command.direct_object:
            print("What do you want to read?")
            return
            
        obj = self.objects[command.direct_object]
        
        if not obj.has_flag(ObjectFlag.READABLE):
            print("There's nothing to read.")
            return
            
        print(obj.examine_text)
        
        # Special case for black book
        if command.direct_object == "book":
            self.book_read = True
            
        # Special case for prayer
        if command.direct_object == "prayer":
            print("The prayer mentions the following words: \"bell\", \"book\", and \"candles\".")
            
    def _turn_on(self, command: ParsedCommand):
        """Turn on something"""
        if not command.direct_object:
            print("What do you want to turn on?")
            return
            
        obj_id = command.direct_object
        obj = self.objects[obj_id]
        
        if not obj.has_flag(ObjectFlag.TURNNABLE):
            print("You can't turn that on.")
            return
            
        if obj_id == "lamp":
            if self.lamp_on:
                print("It's already on.")
            else:
                if self.lamp_life > 0:
                    self.lamp_on = True
                    obj.set_flag(ObjectFlag.TURNEDON, True)
                    obj.set_flag(ObjectFlag.LIGHT, True)
                    obj.examine_text = "It is a shiny brass lamp. It is lit."
                    print("The lamp is now on.")
                    if not self.rooms[self.current_room].has_flag(RoomFlag.LIT):
                        self._look()
                else:
                    print("The lamp has run out of power.")
                    
    def _turn_off(self, command: ParsedCommand):
        """Turn off something"""
        if not command.direct_object:
            print("What do you want to turn off?")
            return
            
        obj_id = command.direct_object
        obj = self.objects[obj_id]
        
        if not obj.has_flag(ObjectFlag.TURNNABLE):
            print("You can't turn that off.")
            return
            
        if obj_id == "lamp":
            if not self.lamp_on:
                print("It's already off.")
            else:
                self.lamp_on = False
                obj.set_flag(ObjectFlag.TURNEDON, False)
                obj.set_flag(ObjectFlag.LIGHT, False)
                obj.examine_text = "It is a shiny brass lamp. It is not currently lit."
                print("The lamp is now off.")
                self._check_light()
                
    def _move(self, command: ParsedCommand):
        """Move/push an object"""
        if not command.direct_object:
            print("What do you want to move?")
            return
            
        obj_id = command.direct_object
        
        if obj_id == "rug":
            if self.objects["trap_door"].location is None:
                print("With a great effort, the rug is moved to one side of the room, revealing the dusty cover of a closed trap door.")
                self.objects["trap_door"].location = "living_room"
            else:
                print("Having moved the rug previously, you find it impossible to move it again.")
        elif obj_id == "leaves":
            if self.objects["grating"].location is None:
                print("In disturbing the pile of leaves, a grating is revealed.")
                self.objects["grating"].location = "clearing"
                self.rooms["clearing"].exits[Direction.DOWN] = "grating_room"
            else:
                print("You've already done that.")
        else:
            print("You can't move that.")
            
    def _push(self, command: ParsedCommand):
        """Push something"""
        if not command.direct_object:
            print("What do you want to push?")
            return
            
        obj_id = command.direct_object
        
        # Push button
        if obj_id in ["green_button", "red_button", "button"] and self.current_room == "dam":
            if obj_id == "green_button" or (obj_id == "button" and not self.dam_open):
                if not self.dam_open:
                    print("The sluice gates open and water pours through the dam.")
                    self.dam_open = True
                    self._drain_reservoir()
                else:
                    print("The gates are already open.")
            elif obj_id == "red_button" or (obj_id == "button" and self.dam_open):
                if self.dam_open:
                    print("The sluice gates close and water starts to accumulate.")
                    self.dam_open = False
                    self._fill_reservoir()
                else:
                    print("The gates are already closed.")
        else:
            self._move(command)
            
    def _drain_reservoir(self):
        """Drain the reservoir"""
        # Change room descriptions
        self.rooms["reservoir"].description = "You are in a long room, once a large reservoir. There is a north-south path across the room."
        self.rooms["reservoir"].flags &= ~RoomFlag.ONWATER.value
        self.rooms["reservoir"].exits[Direction.NORTH] = "reservoir_north"
        self.rooms["reservoir"].exits[Direction.SOUTH] = "reservoir_south"
        
        self.rooms["reservoir_south"].description = "You are in a long room on the south shore of a dried-up reservoir."
        self.rooms["reservoir_north"].description = "You are in a large cavernous room, north of a dried-up reservoir."
        
        # Reveal trunk
        if self.objects["trunk"].location is None:
            self.objects["trunk"].location = "reservoir_north"
            
        # Update loud room
        self.loud_room_level = 8
        
    def _fill_reservoir(self):
        """Fill the reservoir"""
        # Change room descriptions back
        self.rooms["reservoir"].description = "You are on the lake. Beaches can be seen north and south. Upstream a small stream enters the lake through a narrow cleft in the rocks. The dam can be seen downstream."
        self.rooms["reservoir"].flags |= RoomFlag.ONWATER.value
        
        self.rooms["reservoir_south"].description = "You are in a long room on the south shore of a large lake, far too deep and wide for crossing."
        self.rooms["reservoir_north"].description = "You are in a large cavernous room, north of a large lake."
        
        # Update loud room
        self.loud_room_level = 4
        
    def _attack(self, command: ParsedCommand):
        """Attack something"""
        if not command.direct_object:
            print("What do you want to attack?")
            return
            
        target = command.direct_object
        
        # Check if attacking an actor
        if target in self.actors:
            actor = self.actors[target]
            if actor.location != self.current_room:
                print("You don't see that here.")
                return
                
            if target == "troll":
                if "sword" in self.player_inventory:
                    print("The troll takes a vicious swipe at you with his axe, but you deftly dodge.")
                    print("You charge the troll, who attempts to dodge, but is unsuccessful.")
                    print(actor.messages["death"])
                    actor.active = False
                    actor.location = None
                    if self.objects["axe"].location == "troll":
                        self.objects["axe"].location = "troll_room"
                else:
                    print("Trying to attack the troll with your bare hands is suicidal.")
                    self._death("The troll hits you with a crushing blow.")
                    
            elif target == "thief":
                print("The thief is a formidable opponent. He dodges your attack.")
                if random.randint(1, 3) == 1:
                    print(actor.messages["stiletto"])
                    self._death("The thief stabs you with his stiletto.")
                    
            elif target == "cyclops":
                print("The cyclops laughs at your puny attack!")
                print("The cyclops hits you with a crushing blow.")
                self._death("The cyclops has knocked you senseless.")
                
            elif target == "spirits":
                print("How can you attack spirits?")
                
            elif target == "bat":
                print("The bat flies away from your attack.")
                actor.location = None
                
        else:
            print("I don't know what you're trying to attack.")
            
    def _eat(self, command: ParsedCommand):
        """Eat something"""
        if not command.direct_object:
            print("What do you want to eat?")
            return
            
        obj = self.objects[command.direct_object]
        
        if not obj.has_flag(ObjectFlag.EDIBLE):
            print(f"I don't think the {obj.name} would agree with you.")
            return
            
        if command.direct_object not in self.player_inventory:
            print("You don't have that.")
            return
            
        print("Thank you very much. It really hit the spot.")
        self.player_inventory.remove(command.direct_object)
        del self.objects[command.direct_object]
        
    def _drink(self, command: ParsedCommand):
        """Drink something"""
        if not command.direct_object:
            print("What do you want to drink?")
            return
            
        obj = self.objects[command.direct_object]
        
        if not obj.has_flag(ObjectFlag.DRINKABLE):
            print("You can't drink that!")
            return
            
        print("Thank you very much. I was very thirsty.")
        if command.direct_object == "water":
            self.objects["bottle"].examine_text = "The glass bottle is empty."
            del self.objects["water"]
            
    def _give(self, command: ParsedCommand):
        """Give something to someone"""
        if not command.direct_object:
            print("What do you want to give?")
            return
            
        # Simple implementation - check for troll
        if self.current_room == "troll_room" and self.actors["troll"].active:
            if command.direct_object in self.player_inventory:
                obj = self.objects[command.direct_object]
                if obj.has_flag(ObjectFlag.TREASURE):
                    print("The troll catches your treasure and scurries away out of sight.")
                    self.player_inventory.remove(command.direct_object)
                    del self.objects[command.direct_object]
                    self.actors["troll"].active = False
                    self.actors["troll"].location = None
                    self.troll_payment = True
                else:
                    print("The troll is not interested in your offering.")
            else:
                print("You don't have that.")
        else:
            print("There's no one here to give it to.")
            
    def _unlock(self, command: ParsedCommand):
        """Unlock something"""
        if not command.direct_object:
            print("What do you want to unlock?")
            return
            
        obj_id = command.direct_object
        
        if obj_id == "grating" and self.objects["grating"].location is not None:
            if "skeleton_key" in self.player_inventory:
                print("The grating is unlocked.")
                self.grating_unlocked = True
                self.objects["grating"].set_flag(ObjectFlag.LOCKED, False)
                self.rooms["grating_room"].exits[Direction.UP] = "clearing"
            else:
                print("You don't have the right key.")
        else:
            print("You can't unlock that.")
            
    def _lock(self, command: ParsedCommand):
        """Lock something"""
        if not command.direct_object:
            print("What do you want to lock?")
            return
            
        print("You can't lock that.")
        
    def _tie(self, command: ParsedCommand):
        """Tie rope to something"""
        if not command.direct_object:
            print("What do you want to tie?")
            return
            
        if command.direct_object == "rope" and "rope" in self.player_inventory:
            if self.current_room == "dome_room":
                print("The rope is tied to the wooden railing.")
                self.objects["rope"].location = "dome_room"
                self.player_inventory.remove("rope")
                self.rooms["dome_room"].exits[Direction.DOWN] = "torch_room"
            elif self.current_room == "shaft_room":
                print("The rope is tied to the iron framework.")
                self.objects["rope"].location = "shaft_room"
                self.player_inventory.remove("rope")
                self.rooms["shaft_room"].exits[Direction.DOWN] = "drafty_room"
            else:
                print("You can't tie the rope to anything here.")
        else:
            print("You can't tie that.")
            
    def _untie(self, command: ParsedCommand):
        """Untie rope"""
        if not command.direct_object:
            print("What do you want to untie?")
            return
            
        if command.direct_object == "rope":
            if self.objects["rope"].location in ["dome_room", "shaft_room"]:
                print("The rope is untied.")
                self.player_inventory.append("rope")
                self.objects["rope"].location = "player"
                if self.current_room == "dome_room":
                    del self.rooms["dome_room"].exits[Direction.DOWN]
                elif self.current_room == "shaft_room":
                    del self.rooms["shaft_room"].exits[Direction.DOWN]
            else:
                print("The rope is not tied to anything.")
        else:
            print("You can't untie that.")
            
    def _burn(self, command: ParsedCommand):
        """Burn something"""
        if not command.direct_object:
            print("What do you want to burn?")
            return
            
        obj = self.objects[command.direct_object]
        
        if obj.has_flag(ObjectFlag.FLAMMABLE):
            # Check for flame source
            has_flame = False
            if self.objects["torch"].location == "player" and self.objects["torch"].has_flag(ObjectFlag.TURNEDON):
                has_flame = True
            elif self.objects["candles"].location == "player" and self.candles_lit:
                has_flame = True
            elif "matchbook" in self.player_inventory:
                has_flame = True
                
            if has_flame:
                if command.direct_object == "candles":
                    print("The candles are lit.")
                    self.candles_lit = True
                    obj.set_flag(ObjectFlag.LIGHT, True)
                    obj.set_flag(ObjectFlag.TURNEDON, True)
                else:
                    print(f"The {obj.name} burns to ashes.")
                    if command.direct_object in self.player_inventory:
                        self.player_inventory.remove(command.direct_object)
                    del self.objects[command.direct_object]
            else:
                print("You have no flame source.")
        else:
            print("You can't burn that.")
            
    def _extinguish(self, command: ParsedCommand):
        """Extinguish something"""
        if not command.direct_object:
            print("What do you want to extinguish?")
            return
            
        if command.direct_object == "candles" and self.candles_lit:
            print("The candles are extinguished.")
            self.candles_lit = False
            self.objects["candles"].set_flag(ObjectFlag.LIGHT, False)
            self.objects["candles"].set_flag(ObjectFlag.TURNEDON, False)
        elif command.direct_object == "torch":
            print("You can't extinguish that.")
        else:
            self._turn_off(command)
            
    def _ring(self, command: ParsedCommand):
        """Ring the bell"""
        if not command.direct_object:
            print("What do you want to ring?")
            return
            
        if command.direct_object == "bell" and command.direct_object in self.player_inventory:
            print("Ding, dong.")
            self.bell_rung = True
            self._check_exorcism()
        else:
            print("You can't ring that.")
            
    def _check_exorcism(self):
        """Check if exorcism conditions are met"""
        if (self.current_room == "entrance_to_hades" and 
            self.bell_rung and self.book_read and self.candles_lit):
            print("\nSuddenly, the bell, book, and candles begin to glow!")
            print(self.actors["spirits"].messages["exorcise"])
            self.spirits_released = True
            self.actors["spirits"].active = False
            self.actors["spirits"].location = None
            self.rooms["entrance_to_hades"].exits[Direction.SOUTH] = "land_of_the_dead"
            
    def _wind(self, command: ParsedCommand):
        """Wind something"""
        if not command.direct_object:
            print("What do you want to wind?")
            return
            
        if command.direct_object == "canary" and "golden_canary" in self.player_inventory:
            print("The canary chirps, slightly off-key, an aria from a forgotten opera. From out of the greenery flies a lovely songbird. It perches on a limb just over your head and opens its beak to sing. As it does so a beautiful brass bauble drops from its mouth, bounces off the top of your head, and lands glimmering in the grass. As the canary winds down, the songbird flies away.")
            self.objects["bauble"] = GameObject(
                id="bauble",
                name="bauble",
                description="beautiful brass bauble",
                examine_text="It's a beautiful brass bauble.",
                flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TREASURE.value,
                location=self.current_room,
                size=1,
                value=1
            )
        else:
            print("You can't wind that.")
            
    def _dig(self, command: ParsedCommand):
        """Dig with shovel"""
        if "shovel" not in self.player_inventory:
            print("You don't have anything to dig with.")
            return
            
        if self.current_room == "white_cliffs_beach_south":
            if self.objects["jeweled_scarab"].location is None:
                print("You dig in the sand and uncover a beautiful scarab!")
                self.objects["jeweled_scarab"].location = "white_cliffs_beach_south"
            else:
                print("You find nothing else.")
        else:
            print("The ground is too hard to dig here.")
            
    def _fill(self, command: ParsedCommand):
        """Fill something"""
        if not command.direct_object:
            print("What do you want to fill?")
            return
            
        if command.direct_object == "bottle" and command.direct_object in self.player_inventory:
            if self.current_room in ["stream", "reservoir"] or self.rooms[self.current_room].has_flag(RoomFlag.ONWATER):
                if "water" not in [obj.id for obj in self.objects.values() if obj.location == "bottle"]:
                    print("The bottle is now full of water.")
                    self.objects["water"] = GameObject(
                        id="water",
                        name="water",
                        description="quantity of water",
                        flags=ObjectFlag.DRINKABLE.value,
                        location="bottle",
                        size=1
                    )
                    self.objects["bottle"].examine_text = "The glass bottle contains:\n  A quantity of water"
                else:
                    print("The bottle is already full.")
            else:
                print("There's no water here.")
        else:
            print("You can't fill that.")
            
    def _pour(self, command: ParsedCommand):
        """Pour water"""
        if not command.direct_object:
            print("What do you want to pour?")
            return
            
        if command.direct_object == "water":
            if "water" in [obj.id for obj in self.objects.values() if obj.location == "bottle" and "bottle" in self.player_inventory]:
                print("The water splashes on the ground and evaporates.")
                del self.objects["water"]
                self.objects["bottle"].examine_text = "The glass bottle is empty."
            else:
                print("You don't have any water.")
        else:
            print("You can't pour that.")
            
    def _pray(self, command: ParsedCommand):
        """Pray at altar"""
        if self.current_room == "altar":
            print("The ground shakes and a passage opens beneath you!")
            self.rooms["altar"].exits[Direction.DOWN] = "cave_1"
        else:
            print("Nothing happens.")
            
    def _wave(self, command: ParsedCommand):
        """Wave something"""
        if not command.direct_object:
            print("What do you want to wave?")
            return
            
        obj_id = command.direct_object
        
        if obj_id == "sceptre" and obj_id in self.player_inventory:
            if self.current_room == "end_of_rainbow" or self.current_room == "aragain_falls":
                if not self.rainbow_solid:
                    print("Suddenly, the rainbow appears to become solid and you can walk on it!")
                    self.rainbow_solid = True
                    self.rooms["end_of_rainbow"].exits[Direction.EAST] = "on_the_rainbow"
                    self.rooms["on_the_rainbow"].exits[Direction.WEST] = "end_of_rainbow"
                    self.rooms["on_the_rainbow"].exits[Direction.EAST] = "aragain_falls"
                    self.rooms["aragain_falls"].exits[Direction.WEST] = "on_the_rainbow"
                else:
                    print("The rainbow seems to waver and become less solid.")
                    self.rainbow_solid = False
                    del self.rooms["end_of_rainbow"].exits[Direction.EAST]
                    del self.rooms["aragain_falls"].exits[Direction.WEST]
            else:
                print("A dazzling display of color briefly emanates from the sceptre.")
        else:
            print(f"You wave the {self.objects[obj_id].name}.")
            
    def _raise(self, command: ParsedCommand):
        """Raise something"""
        if not command.direct_object:
            print("What do you want to raise?")
            return
            
        print("You can't raise that.")
        
    def _lower(self, command: ParsedCommand):
        """Lower something"""
        if not command.direct_object:
            print("What do you want to lower?")
            return
            
        if command.direct_object == "basket" and self.current_room == "shaft_room":
            if "basket" in self.player_inventory:
                print("The basket is lowered on the chain.")
                self.objects["basket"].location = "drafty_room"
                self.player_inventory.remove("basket")
            else:
                print("You're not carrying the basket.")
        else:
            print("You can't lower that.")
            
    def _climb(self, command: ParsedCommand):
        """Climb something"""
        if self.current_room == "dome_room" and self.objects["rope"].location == "dome_room":
            print("You climb down the rope.")
            self.current_room = "torch_room"
            self._look()
        elif Direction.UP in self.rooms[self.current_room].exits:
            self._go(Direction.UP)
        elif Direction.DOWN in self.rooms[self.current_room].exits:
            self._go(Direction.DOWN)
        else:
            print("There's nothing to climb here.")
            
    def _jump(self, command: ParsedCommand):
        """Jump"""
        if self.current_room == "aragain_falls":
            print("You jump off the falls...")
            self._death("You didn't make it.")
        else:
            print("Wheee!")
            
    def _break(self, command: ParsedCommand):
        """Break something"""
        if not command.direct_object:
            print("What do you want to break?")
            return
            
        obj_id = command.direct_object
        
        if obj_id == "mirror_south" or obj_id == "mirror_north":
            if not self.mirror_broken:
                print("You have broken the mirror. The looking glass is now gone.")
                self.mirror_broken = True
                # Connect the two mirror rooms
                self.rooms["mirror_room_south"].exits[Direction.NORTH] = "mirror_room_north"
                self.rooms["mirror_room_north"].exits[Direction.SOUTH] = "mirror_room_south"
                del self.objects["mirror_south"]
                del self.objects["mirror_north"]
            else:
                print("The mirror is already broken.")
        elif obj_id == "jeweled_egg":
            print("The egg is now open, but the clumsiness of your attempt has seriously compromised its esthetic appeal.")
            self.objects["jeweled_egg"].set_flag(ObjectFlag.OPEN, True)
            self.objects["jeweled_egg"].value = 2  # Reduced value
        else:
            print("You can't break that.")
            
    def _quit(self, command: ParsedCommand):
        """Quit the game"""
        response = input("Are you sure you want to quit? ").lower()
        if response.startswith('y'):
            self._show_final_score()
            self.game_over = True
            
    def _save(self, command: ParsedCommand):
        """Save the game"""
        filename = input("Save filename: ")
        try:
            save_data = {
                'player_name': self.player_name,
                'current_room': self.current_room,
                'inventory': self.player_inventory,
                'score': self.score,
                'moves': self.moves,
                'deaths': self.deaths,
                'visited_rooms': list(self.visited_rooms),
                'lamp_on': self.lamp_on,
                'lamp_life': self.lamp_life,
                'grating_unlocked': self.grating_unlocked,
                'trap_door_open': self.trap_door_open,
                'rainbow_solid': self.rainbow_solid,
                'dam_open': self.dam_open,
                'loud_room_level': self.loud_room_level,
                'coffin_open': self.coffin_open,
                'bell_rung': self.bell_rung,
                'candles_lit': self.candles_lit,
                'book_read': self.book_read,
                'spirits_released': self.spirits_released,
                'cyclops_fled': self.cyclops_fled,
                'mirror_broken': self.mirror_broken,
                'troll_payment': self.troll_payment,
                'thief_here': self.thief_here,
                'treasures_deposited': self.treasures_deposited,
                'objects': {},
                'actors': {}
            }
            
            # Save object states
            for obj_id, obj in self.objects.items():
                save_data['objects'][obj_id] = {
                    'location': obj.location,
                    'flags': obj.flags,
                    'value': obj.value
                }
                
            # Save actor states
            for actor_id, actor in self.actors.items():
                save_data['actors'][actor_id] = {
                    'location': actor.location,
                    'health': actor.health,
                    'active': actor.active
                }
                
            with open(filename, 'w') as f:
                json.dump(save_data, f)
            print("Game saved.")
        except Exception as e:
            print(f"Save failed: {e}")
            
    def _restore(self, command: ParsedCommand):
        """Restore a saved game"""
        filename = input("Restore filename: ")
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
                
            self.player_name = save_data.get('player_name', 'Adventurer')
            self.current_room = save_data['current_room']
            self.player_inventory = save_data['inventory']
            self.score = save_data['score']
            self.moves = save_data['moves']
            self.deaths = save_data.get('deaths', 0)
            self.visited_rooms = set(save_data['visited_rooms'])
            self.lamp_on = save_data['lamp_on']
            self.lamp_life = save_data.get('lamp_life', 330)
            self.grating_unlocked = save_data.get('grating_unlocked', False)
            self.trap_door_open = save_data.get('trap_door_open', False)
            self.rainbow_solid = save_data.get('rainbow_solid', False)
            self.dam_open = save_data.get('dam_open', False)
            self.loud_room_level = save_data.get('loud_room_level', 4)
            self.coffin_open = save_data.get('coffin_open', False)
            self.bell_rung = save_data.get('bell_rung', False)
            self.candles_lit = save_data.get('candles_lit', False)
            self.book_read = save_data.get('book_read', False)
            self.spirits_released = save_data.get('spirits_released', False)
            self.cyclops_fled = save_data.get('cyclops_fled', False)
            self.mirror_broken = save_data.get('mirror_broken', False)
            self.troll_payment = save_data.get('troll_payment', False)
            self.thief_here = save_data.get('thief_here', False)
            self.treasures_deposited = save_data.get('treasures_deposited', 0)
            
            # Restore object states
            for obj_id, obj_data in save_data['objects'].items():
                if obj_id in self.objects:
                    self.objects[obj_id].location = obj_data['location']
                    self.objects[obj_id].flags = obj_data['flags']
                    self.objects[obj_id].value = obj_data.get('value', self.objects[obj_id].value)
                    
            # Restore actor states
            for actor_id, actor_data in save_data.get('actors', {}).items():
                if actor_id in self.actors:
                    self.actors[actor_id].location = actor_data['location']
                    self.actors[actor_id].health = actor_data['health']
                    self.actors[actor_id].active = actor_data['active']
                    
            print("Game restored.")
            self._look()
        except FileNotFoundError:
            print("Restore failed. File not found.")
        except Exception as e:
            print(f"Restore failed: {e}")
            
    def _restart(self, command: ParsedCommand):
        """Restart the game"""
        response = input("Are you sure you want to restart? ").lower()
        if response.startswith('y'):
            saved_name = self.player_name
            self.__init__()
            self.player_name = saved_name
            print()
            self._look()
            
    def _score(self, command: ParsedCommand):
        """Show score"""
        max_score = 350
        print(f"Your score is {self.score} (total of {max_score} points), in {self.moves} moves.")
        print(f"This gives you the rank of {self._get_rank()}.")
        
    def _get_rank(self):
        """Get player rank based on score"""
        if self.score >= 350:
            return "Master Adventurer"
        elif self.score >= 330:
            return "Wizard"
        elif self.score >= 300:
            return "Master"
        elif self.score >= 200:
            return "Adventurer"
        elif self.score >= 100:
            return "Junior Adventurer"
        elif self.score >= 50:
            return "Novice Adventurer"
        elif self.score >= 25:
            return "Amateur Adventurer"
        else:
            return "Beginner"
            
    def _show_final_score(self):
        """Show final score and rank"""
        print()
        print(f"In {self.moves} moves, you have scored {self.score} points (total of 350 points).")
        print(f"This gives you the rank of {self._get_rank()}.")
        if self.deaths > 0:
            print(f"You died {self.deaths} times.")
            
    def _version(self, command: ParsedCommand):
        """Show version"""
        print("ZORK I: The Great Underground Empire")
        print("Infocom interactive fiction - a fantasy story")
        print("Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.")
        print("ZORK is a registered trademark of Infocom, Inc.")
        print("Revision 88 / Serial number 840726")
        print(f"Python implementation by haxorthematrix in 2025")
        
    def _verbose(self, command: ParsedCommand):
        """Set verbose mode"""
        self.verbose = True
        print("Maximum verbosity.")
        
    def _brief(self, command: ParsedCommand):
        """Set brief mode"""
        self.verbose = False
        print("Brief descriptions.")
        
    def _wait(self, command: ParsedCommand):
        """Wait a turn"""
        print("Time passes...")
        
    def _diagnose(self, command: ParsedCommand):
        """Show health status"""
        if self.deaths == 0:
            print("You are in perfect health.")
        else:
            print(f"You have died {self.deaths} times. You are in decent health.")
            
    def _check_light(self):
        """Check if player can see in current room"""
        room = self.rooms[self.current_room]
        
        # Room is naturally lit
        if room.has_flag(RoomFlag.LIT):
            return
            
        # Check for light source
        if not self._can_see():
            print("It is pitch black. You are likely to be eaten by a grue.")
            if random.randint(1, 4) == 1:  # 25% chance
                print("\nOh, no! You have walked into the slavering fangs of a lurking grue!")
                self._death("You have died.")
                
    def _can_see(self):
        """Check if player can see"""
        room = self.rooms[self.current_room]
        
        if room.has_flag(RoomFlag.LIT):
            return True
            
        # Check for light sources
        for obj_id in self.player_inventory:
            obj = self.objects[obj_id]
            if obj.has_flag(ObjectFlag.LIGHT) and obj.has_flag(ObjectFlag.TURNEDON):
                return True
                
        for obj_id, obj in self.objects.items():
            if obj.location == self.current_room:
                if obj.has_flag(ObjectFlag.LIGHT) and obj.has_flag(ObjectFlag.TURNEDON):
                    return True
                    
        return False
        
    def _death(self, message):
        """Handle player death"""
        print(message)
        self.deaths += 1
        print(f"\n    ****  You have died  ****\n")
        
        # Drop everything
        for obj_id in self.player_inventory.copy():
            self.objects[obj_id].location = self.current_room
            self.player_inventory.remove(obj_id)
            
        # Restore player
        self.current_room = "west_of_house"
        print("As you take your last breath, you feel yourself being pulled from your body.")
        print("You float upward, watching your corpse below. Suddenly, you find yourself...")
        print()
        self._look()
        
    def _check_random_events(self):
        """Check for random events"""
        # Thief appears randomly
        if (not self.thief_here and 
            not self.rooms[self.current_room].has_flag(RoomFlag.LIT) and
            not self.rooms[self.current_room].has_flag(RoomFlag.NOPIRATE) and
            random.randint(1, 100) <= 5):
            
            self.thief_here = True
            self.actors["thief"].location = self.current_room
            print("\nSomeone carrying a large bag just wandered through the room.")
            
            # Thief might steal
            if random.randint(1, 100) <= 20:
                treasures = [obj_id for obj_id in self.player_inventory 
                           if self.objects[obj_id].has_flag(ObjectFlag.TREASURE)]
                if treasures:
                    stolen = random.choice(treasures)
                    self.player_inventory.remove(stolen)
                    print(f"The thief deftly relieves you of the {self.objects[stolen].name}.")
                    
        # Thief leaves
        elif self.thief_here and random.randint(1, 100) <= 30:
            self.thief_here = False
            self.actors["thief"].location = None
            print("\nThe thief vanishes into the gloom.")
            
        # Bat
        if self.current_room == "bat_room" and self.actors["bat"].active:
            if "garlic" in self.player_inventory:
                print("\n" + self.actors["bat"].messages["garlic"])
                self.actors["bat"].active = False
                self.actors["bat"].location = None
                
        # Cyclops
        if self.current_room == "cyclops_room" and self.actors["cyclops"].active:
            # Check if player says "Odysseus" or "Ulysses"
            pass  # Would need to implement in command parser


# Main entry point
if __name__ == "__main__":
    game = ZorkGame()
    game.start()#!/usr/bin/env python3
"""
Zork (Dungeon) - Python Implementation - Expanded Version
Based on the C version translated from FORTRAN by way of f2c
Original game by Tim Anderson, Marc Blank, Bruce Daniels, and Dave Lebling
Python conversion maintains the structure and functionality of the C version
This expanded version includes more rooms, treasures, NPCs, and puzzles from the original
"""

import sys
import os
import pickle
import json
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Union
import random
import textwrap

# Constants and Enumerations
class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NE = "northeast"
    NW = "northwest"
    SE = "southeast"
    SW = "southwest"
    UP = "up"
    DOWN = "down"
    IN = "in"
    OUT = "out"
    LAND = "land"

class VerbType(Enum):
    TAKE = auto()
    DROP = auto()
    OPEN = auto()
    CLOSE = auto()
    LIGHT = auto()
    EXTINGUISH = auto()
    MOVE = auto()
    ATTACK = auto()
    EXAMINE = auto()
    READ = auto()
    THROW = auto()
    PUT = auto()
    TURN = auto()
    JUMP = auto()
    INVENTORY = auto()
    QUIT = auto()
    SAVE = auto()
    RESTORE = auto()
    RESTART = auto()
    VERBOSE = auto()
    BRIEF = auto()
    SCORE = auto()
    VERSION = auto()
    LOOK = auto()
    WAIT = auto()
    AGAIN = auto()
    ENTER = auto()
    EXIT = auto()
    CLIMB = auto()
    GIVE = auto()
    DRINK = auto()
    EAT = auto()
    BREAK = auto()
    KILL = auto()
    WAVE = auto()
    RAISE = auto()
    LOWER = auto()
    TURN_ON = auto()
    TURN_OFF = auto()
    DIAGNOSE = auto()
    UNLOCK = auto()
    LOCK = auto()
    TIE = auto()
    UNTIE = auto()
    BURN = auto()
    EXTINGUISH = auto()
    RING = auto()
    WIND = auto()
    DIG = auto()
    FILL = auto()
    POUR = auto()
    PRAY = auto()
    PUSH = auto()
    
# Object flags
class ObjectFlag(Enum):
    VISIBLE = 0x0001
    TAKEABLE = 0x0002
    CONTAINER = 0x0008
    OPEN = 0x0010
    CLOSED = 0x0020
    LOCKED = 0x0040
    LIGHT = 0x0080
    READABLE = 0x0100
    DOOR = 0x0200
    TRANSPARENT = 0x0400
    WEAPON = 0x0800
    TURNNABLE = 0x1000
    TURNEDON = 0x2000
    EDIBLE = 0x4000
    DRINKABLE = 0x8000
    TREASURE = 0x10000
    VEHICLE = 0x20000
    SACRED = 0x40000
    TOOL = 0x80000
    FLAMMABLE = 0x100000
    
# Room flags
class RoomFlag(Enum):
    LIT = 0x0001
    DEATH = 0x0002
    SACRED = 0x0008
    NOPIRATE = 0x0010
    ONWATER = 0x0020
    
@dataclass
class GameObject:
    """Represents an object in the game"""
    id: str
    name: str
    description: str = ""
    examine_text: str = ""
    initial_text: str = ""
    flags: int = 0
    location: Optional[str] = None
    capacity: int = 0
    size: int = 0
    value: int = 0
    
    def has_flag(self, flag: ObjectFlag) -> bool:
        return bool(self.flags & flag.value)
    
    def set_flag(self, flag: ObjectFlag, value: bool = True):
        if value:
            self.flags |= flag.value
        else:
            self.flags &= ~flag.value
            
@dataclass
class Room:
    """Represents a room/location in the game"""
    id: str
    name: str
    description: str = ""
    flags: int = 0
    exits: Dict[Direction, str] = field(default_factory=dict)
    
    def has_flag(self, flag: RoomFlag) -> bool:
        return bool(self.flags & flag.value)
    
    def set_flag(self, flag: RoomFlag, value: bool = True):
        if value:
            self.flags |= flag.value
        else:
            self.flags &= ~flag.value

@dataclass
class Actor:
    """Represents an NPC in the game"""
    id: str
    name: str
    description: str
    location: Optional[str]
    health: int = 100
    hostile: bool = False
    active: bool = True
    messages: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class ParsedCommand:
    """Result of parsing user input"""
    verb: Optional[VerbType] = None
    direct_object: Optional[str] = None
    indirect_object: Optional[str] = None
    direction: Optional[Direction] = None
    raw_input: str = ""

class ZorkGame:
    """Main game class"""
    
    def __init__(self):
        # Player name
        self.player_name: str = "Adventurer"
        
        # Game state
        self.rooms: Dict[str, Room] = {}
        self.objects: Dict[str, GameObject] = {}
        self.actors: Dict[str, Actor] = {}
        self.current_room: str = "west_of_house"
        self.player_inventory: List[str] = []
        self.score: int = 0
        self.moves: int = 0
        self.verbose: bool = True
        self.game_over: bool = False
        self.visited_rooms: Set[str] = set()
        self.deaths: int = 0
        
        # Special flags
        self.lamp_on: bool = False
        self.lamp_life: int = 330  # Lamp has limited life
        self.grating_unlocked: bool = False
        self.trap_door_open: bool = False
        self.rainbow_solid: bool = False
        self.dam_open: bool = False
        self.loud_room_level: int = 4  # Water level
        self.coffin_open: bool = False
        self.bell_rung: bool = False
        self.candles_lit: bool = False
        self.book_read: bool = False
        self.spirits_released: bool = False
        self.cyclops_fled: bool = False
        self.mirror_broken: bool = False
        self.troll_payment: bool = False
        self.thief_here: bool = False
        self.treasures_deposited: int = 0
        
        # Initialize game world
        self._init_rooms()
        self._init_objects()
        self._init_actors()
        
    def _init_rooms(self):
        """Initialize all rooms"""
        
        # Above Ground Areas
        self.rooms["west_of_house"] = Room(
            id="west_of_house",
            name="West of House",
            description="You are standing in an open field west of a white house, with a boarded front door.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "north_of_house",
                Direction.SOUTH: "south_of_house",
                Direction.WEST: "forest_1",
                Direction.EAST: "west_of_house"  # Can't enter house this way
            }
        )
        
        self.rooms["north_of_house"] = Room(
            id="north_of_house",
            name="North of House",
            description="You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "west_of_house",
                Direction.EAST: "behind_house",
                Direction.NORTH: "forest_path"
            }
        )
        
        self.rooms["behind_house"] = Room(
            id="behind_house",
            name="Behind House",
            description="You are behind the white house. A path leads into the forest to the east. In one corner of the house there is a small window which is slightly ajar.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "north_of_house",
                Direction.SOUTH: "south_of_house",
                Direction.EAST: "clearing",
                Direction.WEST: "kitchen",
                Direction.IN: "kitchen"
            }
        )
        
        self.rooms["south_of_house"] = Room(
            id="south_of_house",
            name="South of House", 
            description="You are facing the south side of a white house. There is no door here, and all the windows are boarded.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "west_of_house",
                Direction.EAST: "behind_house",
                Direction.SOUTH: "forest_1"
            }
        )
        
        # Inside House
        self.rooms["kitchen"] = Room(
            id="kitchen",
            name="Kitchen",
            description="You are in the kitchen of the white house. A table seems to have been used recently for the preparation of food. A passage leads to the west and a dark staircase can be seen leading upward. A dark chimney leads down and to the east is a small window which is open.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.EAST: "behind_house",
                Direction.WEST: "living_room",
                Direction.UP: "attic",
                Direction.DOWN: "studio",
                Direction.OUT: "behind_house"
            }
        )
        
        self.rooms["living_room"] = Room(
            id="living_room",
            name="Living Room", 
            description="You are in the living room. There is a doorway to the east, a wooden door with strange gothic lettering to the west, which appears to be nailed shut, a trophy case, and a large oriental rug in the center of the room.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.EAST: "kitchen",
                Direction.WEST: "strange_passage"  # Through the door - initially blocked
            }
        )
        
        self.rooms["attic"] = Room(
            id="attic",
            name="Attic",
            description="This is the attic. The only exit is a stairway leading down.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.DOWN: "kitchen"
            }
        )
        
        # Forest
        self.rooms["forest_1"] = Room(
            id="forest_1",
            name="Forest",
            description="This is a forest, with trees in all directions. To the east, there appears to be sunlight.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "clearing",
                Direction.EAST: "forest_path",
                Direction.SOUTH: "forest_3",
                Direction.WEST: "forest_1",
                Direction.UP: "up_tree"
            }
        )
        
        self.rooms["forest_path"] = Room(
            id="forest_path",
            name="Forest Path",
            description="This is a path winding through a dimly lit forest. The path heads north-south here. One particularly large tree with some low branches stands at the edge of the path.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "north_of_house",
                Direction.NORTH: "clearing",
                Direction.UP: "up_tree"
            }
        )
        
        self.rooms["up_tree"] = Room(
            id="up_tree",
            name="Up a Tree",
            description="You are about 10 feet above the ground nestled among some large branches. The nearest branch above you is above your reach.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.DOWN: "forest_path"
            }
        )
        
        self.rooms["forest_2"] = Room(
            id="forest_2",
            name="Forest", 
            description="This is a dimly lit forest, with large trees all around.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "clearing",
                Direction.NORTH: "clearing",
                Direction.EAST: "canyon_view",
                Direction.WEST: "forest_3"
            }
        )
        
        self.rooms["forest_3"] = Room(
            id="forest_3",
            name="Forest",
            description="This is a dimly lit forest, with large trees all around.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.NORTH: "south_of_house",
                Direction.WEST: "forest_1",
                Direction.EAST: "forest_2",
                Direction.SOUTH: "forest_3"
            }
        )
        
        self.rooms["clearing"] = Room(
            id="clearing",
            name="Clearing",
            description="You are in a clearing, with a forest surrounding you on all sides. A path leads south.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.SOUTH: "forest_path",
                Direction.NORTH: "forest_2",
                Direction.EAST: "canyon_view",
                Direction.WEST: "behind_house",
                Direction.DOWN: "grating_room"  # Through grating when open
            }
        )
        
        # Canyon Area
        self.rooms["canyon_view"] = Room(
            id="canyon_view",
            name="Canyon View",
            description="You are at the top of the Great Canyon on its west side. From here there is a marvelous view of the canyon and parts of the Frigid River upstream. Across the canyon, the walls of the White Cliffs join the mighty ramparts of the Flathead Mountains to the east. Following the Canyon upstream to the north, Aragain Falls may be seen, complete with rainbow. The mighty Frigid River flows out from a great dark cavern. To the west and south can be seen an immense forest, stretching for miles around. A path leads northwest. It is possible to climb down into the canyon from here.",
            flags=RoomFlag.LIT.value | RoomFlag.NOPIRATE.value,
            exits={
                Direction.WEST: "forest_2",
                Direction.DOWN: "rocky_ledge",
                Direction.NW: "clearing"
            }
        )
        
        self.rooms["rocky_ledge"] = Room(
            id="rocky_ledge",
            name="Rocky Ledge",
            description="You are on a ledge about halfway up the wall of the river canyon. You can see from here that the main flow from Aragain Falls twists along a passage which it is impossible for you to enter. Below you is the canyon bottom. Above you is more cliff, which appears unclimbable.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.UP: "canyon_view",
                Direction.DOWN: "canyon_bottom"
            }
        )
        
        self.rooms["canyon_bottom"] = Room(
            id="canyon_bottom",
            name="Canyon Bottom",
            description="You are beneath the walls of the river canyon which may be climbable here. The lesser part of the runoff of Aragain Falls flows by below. To the north is a narrow path.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.UP: "rocky_ledge",
                Direction.NORTH: "end_of_rainbow"
            }
        )
        
        self.rooms["end_of_rainbow"] = Room(
            id="end_of_rainbow",
            name="End of Rainbow",
            description="You are on a small, rocky beach on the continuation of the Frigid River past the Falls. The beach is narrow due to the presence of the White Cliffs. The river canyon opens here and sunlight shines in from above. A rainbow crosses over the falls to the east and a narrow path continues to the southwest.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.SW: "canyon_bottom",
                Direction.EAST: "on_the_rainbow"  # Only when rainbow solid
            }
        )
        
        self.rooms["on_the_rainbow"] = Room(
            id="on_the_rainbow",
            name="On the Rainbow",
            description="You are on top of a rainbow (I bet you never thought you would walk on a rainbow), with a magnificent view of the Falls. The rainbow travels east-west here.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.WEST: "end_of_rainbow",
                Direction.EAST: "aragain_falls"
            }
        )
        
        self.rooms["aragain_falls"] = Room(
            id="aragain_falls",
            name="Aragain Falls",
            description="You are at the top of Aragain Falls, an enormous waterfall with a drop of about 150 feet. The only safe way down is on the west side of the falls.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.WEST: "on_the_rainbow",
                Direction.UP: "on_the_rainbow",
                Direction.DOWN: "end_of_rainbow"
            }
        )
        
        # Underground - Main Areas
        self.rooms["cellar"] = Room(
            id="cellar",
            name="Cellar",
            description="You are in a dark and damp cellar with a narrow passageway leading north, and a crawlway to the south. On the west is the bottom of a steep metal ramp which is unclimbable.",
            flags=0,
            exits={
                Direction.NORTH: "troll_room",
                Direction.SOUTH: "east_of_chasm",
                Direction.WEST: "slide_room",  # One way from slide
                Direction.UP: "living_room"  # Only if trap door open
            }
        )
        
        self.rooms["troll_room"] = Room(
            id="troll_room",
            name="The Troll Room", 
            description="This is a small room with passages to the east and south and a forbidding hole leading west. Bloodstains and deep scratches (perhaps made by an axe) mar the walls.",
            flags=0,
            exits={
                Direction.SOUTH: "cellar",
                Direction.EAST: "east_west_passage",
                Direction.WEST: "maze_1"
            }
        )
        
        self.rooms["east_west_passage"] = Room(
            id="east_west_passage",
            name="East-West Passage",
            description="This is a narrow east-west passageway. There is a narrow stairway leading down at the north end of the room.",
            flags=0,
            exits={
                Direction.EAST: "round_room",
                Direction.WEST: "troll_room",
                Direction.NORTH: "chasm",
                Direction.DOWN: "chasm"
            }
        )
        
        self.rooms["round_room"] = Room(
            id="round_room",
            name="Round Room",
            description="This is a circular stone room with passages in all directions. Several of them have unfortunately been blocked by cave-ins.",
            flags=0,
            exits={
                Direction.WEST: "east_west_passage",
                Direction.NORTH: "north_south_passage",
                Direction.SOUTH: "narrow_passage",
                Direction.EAST: "loud_room",
                Direction.SE: "engravings_cave"
            }
        )
        
        self.rooms["narrow_passage"] = Room(
            id="narrow_passage",
            name="Narrow Passage",
            description="This is a long and narrow corridor where a long north-south passageway briefly narrows even further.",
            flags=0,
            exits={
                Direction.NORTH: "round_room",
                Direction.SOUTH: "mirror_room_south"
            }
        )
        
        self.rooms["mirror_room_south"] = Room(
            id="mirror_room_south",
            name="Mirror Room",
            description="You are in a large square room with tall ceilings. On the south wall is an enormous mirror which fills the entire wall. There are exits on the other three sides of the room.",
            flags=0,
            exits={
                Direction.NORTH: "narrow_passage",
                Direction.WEST: "winding_passage",
                Direction.EAST: "cave_2"
            }
        )
        
        self.rooms["cave_2"] = Room(
            id="cave_2",
            name="Cave",
            description="This is a tiny cave with entrances west and north, and a staircase leading down.",
            flags=0,
            exits={
                Direction.WEST: "mirror_room_south",
                Direction.NORTH: "mirror_room_north",
                Direction.DOWN: "entrance_to_hades"
            }
        )
        
        self.rooms["winding_passage"] = Room(
            id="winding_passage",
            name="Winding Passage",
            description="This is a winding passage. It seems that there are only exits on the east and north.",
            flags=0,
            exits={
                Direction.NORTH: "mirror_room_north",
                Direction.EAST: "mirror_room_south"
            }
        )
        
        self.rooms["mirror_room_north"] = Room(
            id="mirror_room_north",
            name="Mirror Room",
            description="You are in a large square room with tall ceilings. On the south wall is an enormous mirror which fills the entire wall. There are exits on the other three sides of the room.",
            flags=0,
            exits={
                Direction.SOUTH: "winding_passage",
                Direction.WEST: "cold_passage",
                Direction.EAST: "cave_1"
            }
        )
        
        self.rooms["cold_passage"] = Room(
            id="cold_passage",
            name="Cold Passage",
            description="This is a cold and damp corridor where a long east-west passageway turns into a southward path.",
            flags=0,
            exits={
                Direction.EAST: "mirror_room_north",
                Direction.SOUTH: "slide_room"
            }
        )
        
        self.rooms["slide_room"] = Room(
            id="slide_room",
            name="Slide Room",
            description="This is a small chamber, which appears to have been part of a coal mine. On the south wall of the chamber the letters \"Granite Wall\" are etched in the rock. To the east is a long passage, and there is a steep metal slide twisting downward. To the north is a small opening.",
            flags=0,
            exits={
                Direction.NORTH: "cold_passage",
                Direction.EAST: "mine_entrance",
                Direction.DOWN: "cellar"  # One way slide
            }
        )
        
        self.rooms["mine_entrance"] = Room(
            id="mine_entrance",
            name="Mine Entrance",
            description="You are standing at the entrance of what might have been a coal mine. The shaft enters the west wall, and there is another exit on the south end of the room.",
            flags=0,
            exits={
                Direction.WEST: "slide_room",
                Direction.SOUTH: "squeaky_room"
            }
        )
        
        self.rooms["squeaky_room"] = Room(
            id="squeaky_room",
            name="Squeaky Room",
            description="You are in a small room. Strange squeaky sounds may be heard coming from the darkness at the east end of the room.",
            flags=0,
            exits={
                Direction.NORTH: "mine_entrance",
                Direction.EAST: "bat_room"
            }
        )
        
        self.rooms["bat_room"] = Room(
            id="bat_room",
            name="Bat Room",
            description="You are in a small room which has doors only to the east and west.",
            flags=0,
            exits={
                Direction.WEST: "squeaky_room",
                Direction.EAST: "shaft_room"
            }
        )
        
        self.rooms["shaft_room"] = Room(
            id="shaft_room",
            name="Shaft Room",
            description="This is a large room, in the middle of which is a small shaft descending through the floor into darkness below. To the west and the north are exits from this room. Constructed over the top of the shaft is a metal framework to which a heavy iron chain is attached.",
            flags=0,
            exits={
                Direction.WEST: "bat_room",
                Direction.NORTH: "smelly_room",
                Direction.DOWN: "drafty_room"  # Via rope or chain
            }
        )
        
        self.rooms["smelly_room"] = Room(
            id="smelly_room",
            name="Smelly Room",
            description="This is a small nondescript room. However, from the direction of a small descending staircase a foul odor can be detected. To the south is a narrow tunnel.",
            flags=0,
            exits={
                Direction.SOUTH: "shaft_room",
                Direction.DOWN: "gas_room"
            }
        )
        
        self.rooms["gas_room"] = Room(
            id="gas_room",
            name="Gas Room",
            description="This is a small room which smells strongly of coal gas. There is a short climb up some stairs and a narrow tunnel leading east.",
            flags=0,
            exits={
                Direction.UP: "smelly_room",
                Direction.EAST: "coal_mine_1"
            }
        )
        
        self.rooms["coal_mine_1"] = Room(
            id="coal_mine_1",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.WEST: "gas_room",
                Direction.NORTH: "coal_mine_2",
                Direction.EAST: "coal_mine_3",
                Direction.SW: "timber_room"
            }
        )
        
        self.rooms["coal_mine_2"] = Room(
            id="coal_mine_2",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_1",
                Direction.NORTH: "coal_mine_4",
                Direction.SE: "coal_mine_3"
            }
        )
        
        self.rooms["coal_mine_3"] = Room(
            id="coal_mine_3",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.WEST: "coal_mine_1",
                Direction.EAST: "coal_mine_4",
                Direction.SOUTH: "ladder_top",
                Direction.NW: "coal_mine_2"
            }
        )
        
        self.rooms["coal_mine_4"] = Room(
            id="coal_mine_4",
            name="Coal Mine",
            description="This is a non-descript part of a coal mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_2",
                Direction.WEST: "coal_mine_3",
                Direction.NORTH: "dead_end_coal_mine"
            }
        )
        
        self.rooms["dead_end_coal_mine"] = Room(
            id="dead_end_coal_mine",
            name="Dead End",
            description="You have come to a dead end in the mine.",
            flags=0,
            exits={
                Direction.SOUTH: "coal_mine_4"
            }
        )
        
        self.rooms["ladder_top"] = Room(
            id="ladder_top",
            name="Ladder Top",
            description="This is a very small room. In the corner is a rickety wooden ladder, leading downward. It might be safe to descend. There is also a staircase leading upward.",
            flags=0,
            exits={
                Direction.NORTH: "coal_mine_3",
                Direction.DOWN: "ladder_bottom",
                Direction.UP: "coal_mine_3"
            }
        )
        
        self.rooms["ladder_bottom"] = Room(
            id="ladder_bottom",
            name="Ladder Bottom",
            description="This is a rather wide room. On one side is the bottom of a narrow wooden ladder. To the west and the south are passages leaving the room.",
            flags=0,
            exits={
                Direction.UP: "ladder_top",
                Direction.WEST: "timber_room",
                Direction.SOUTH: "dead_end_mine"
            }
        )
        
        self.rooms["dead_end_mine"] = Room(
            id="dead_end_mine",
            name="Dead End",
            description="You have come to a dead end in the mine.",
            flags=0,
            exits={
                Direction.NORTH: "ladder_bottom"
            }
        )
        
        self.rooms["timber_room"] = Room(
            id="timber_room",
            name="Timber Room",
            description="This is a long and narrow passage, which is cluttered with broken timbers. A wide passage comes from the east and turns at the west end of the room into a very narrow passageway. From the west comes a strong draft.",
            flags=0,
            exits={
                Direction.EAST: "ladder_bottom",
                Direction.WEST: "drafty_room",
                Direction.SOUTH: "coal_mine_1"
            }
        )
        
        self.rooms["drafty_room"] = Room(
            id="drafty_room",
            name="Drafty Room",
            description="This is a small drafty room in which is the bottom of a long shaft. To the south is a passageway and to the east a very narrow passage. In the shaft can be seen a heavy iron chain.",
            flags=0,
            exits={
                Direction.EAST: "timber_room",
                Direction.SOUTH: "machine_room",
                Direction.UP: "shaft_room"
            }
        )
        
        self.rooms["machine_room"] = Room(
            id="machine_room",
            name="Machine Room",
            description="This is a large, cold room whose sole exit is to the north. In one corner there is a machine which is reminiscent of a clothes dryer. On its face is a switch which is labelled \"START\". The switch does not appear to be manipulatable by any human hand (unless the fingers are about 1/16 by 1/4 inch). On the front of the machine is a large lid, which is closed.",
            flags=0,
            exits={
                Direction.NORTH: "drafty_room"
            }
        )
        
        # Cave Area
        self.rooms["cave_1"] = Room(
            id="cave_1",
            name="Cave",
            description="This is a tiny cave with entrances west and north, and a dark, forbidding staircase leading down.",
            flags=0,
            exits={
                Direction.WEST: "mirror_room_north",
                Direction.NORTH: "twisting_passage",
                Direction.DOWN: "entrance_to_hades"
            }
        )
        
        self.rooms["twisting_passage"] = Room(
            id="twisting_passage",
            name="Twisting Passage",
            description="This is a winding passage. It seems that there are only exits on the east and north.",
            flags=0,
            exits={
                Direction.NORTH: "mirror_room_north",
                Direction.SOUTH: "cave_1"
            }
        )
        
        # Temple Area
        self.rooms["north_south_passage"] = Room(
            id="north_south_passage",
            name="North-South Passage",
            description="This is a high north-south passage, which forks to the northeast.",
            flags=0,
            exits={
                Direction.NORTH: "chasm",
                Direction.NE: "deep_canyon",
                Direction.SOUTH: "round_room"
            }
        )
        
        self.rooms["chasm"] = Room(
            id="chasm",
            name="Chasm",
            description="A chasm runs southwest to northeast and the path follows it. You are on the south side of the chasm, where a crack opens into a passage.",
            flags=0,
            exits={
                Direction.NE: "reservoir_south",
                Direction.SW: "east_west_passage",
                Direction.SOUTH: "north_south_passage",
                Direction.DOWN: "north_south_passage"
            }
        )
        
        self.rooms["deep_canyon"] = Room(
            id="deep_canyon",
            name="Deep Canyon",
            description="You are on the south edge of a deep canyon. Passages lead off to the east, northwest and southwest. A stairway leads down. You can hear the sound of flowing water from below.",
            flags=0,
            exits={
                Direction.SW: "north_south_passage",
                Direction.EAST: "dam",
                Direction.NW: "reservoir_south",
                Direction.DOWN: "loud_room"
            }
        )
        
        self.rooms["loud_room"] = Room(
            id="loud_room",
            name="Loud Room",
            description="This is a large room with a ceiling which cannot be detected from the ground. There is a narrow passage from east to west and a stone stairway leading upward. The room is deafeningly loud with an undetermined rushing sound. The sound seems to reverberate from all of the walls, making it difficult to determine its origin (although it is louder towards the west).",
            flags=0,
            exits={
                Direction.WEST: "round_room",
                Direction.UP: "deep_canyon",
                Direction.EAST: "damp_cave"
            }
        )
        
        self.rooms["damp_cave"] = Room(
            id="damp_cave",
            name="Damp Cave",
            description="This cave has exits to the west and east, and narrows to a crack toward the south. The earth is particularly damp here.",
            flags=0,
            exits={
                Direction.WEST: "loud_room",
                Direction.EAST: "white_cliffs_beach_north"
            }
        )
        
        self.rooms["white_cliffs_beach_north"] = Room(
            id="white_cliffs_beach_north",
            name="White Cliffs Beach",
            description="You are on a narrow strip of beach which runs along the base of the White Cliffs. There is a narrow path heading south along the Cliffs and a tight passage leading west into the cliffs themselves.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.WEST: "damp_cave",
                Direction.SOUTH: "white_cliffs_beach_south"
            }
        )
        
        self.rooms["white_cliffs_beach_south"] = Room(
            id="white_cliffs_beach_south",
            name="White Cliffs Beach",
            description="You are on a rocky, narrow strip of beach beside the Cliffs. A narrow path leads north along the shore.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.NORTH: "white_cliffs_beach_north"
            }
        )
        
        # Dam Area
        self.rooms["dam"] = Room(
            id="dam",
            name="Dam",
            description="You are standing on the top of the Flood Control Dam #3, which was built in 783 GUE to harness the mighty Frigid River. The dam controls a sluice gate by which water is passed downstream. The sluice gate can be controlled by a panel of buttons on the dam. A ladder leads down to the base of the dam.",
            flags=RoomFlag.LIT.value,
            exits={
                Direction.WEST: "deep_canyon",
                Direction.NORTH: "dam_lobby",
                Direction.EAST: "dam_base",
                Direction.DOWN: "dam_base"
            }
        )
        
        self.rooms["dam_lobby"] = Room(
            id="dam_lobby",
            name="Dam Lobby",
            description="This room appears to have been the waiting room for groups touring the dam. There are open doorways here to the north and east marked \"Private\", though the doors are open, and an exit to the south.",
            flags=0,
            exits={
                Direction.SOUTH: "dam",
                Direction.NORTH: "maintenance_room",
                Direction.EAST: "maintenance_room"
            }
        )
        
        self.rooms["maintenance_room"] = Room(
            id="maintenance_room",
            name="Maintenance Room",
            description="This is what appears to have been the maintenance room for Flood Control Dam #3. Apparently, it has been many years since its last use. Most of the equipment here is in a state of disrepair. The only exit is to the south.",
            flags=0,
            exits={
                Direction.SOUTH: "dam_lobby"
            }
        )
        
        self.rooms["dam_base"] = Room(
            id="dam_base",
            name="Dam Base",
            description="You are at the base of Flood Control Dam #3, which looms above you and to the north. The River Frigid is flowing by here. Along the river are the White Cliffs which seem to form giant walls stretching from north to south along the shores of the river as it winds its way downstream.",
            flags=RoomFlag.LIT.value | RoomFlag.ONWATER.value,
            exits={
                Direction.NORTH: "dam",
                Direction.UP: "dam"
            }
        )
        
        # Reservoir Area
        self.rooms["reservoir_south"] = Room(
            id="reservoir_south",
            name="Reservoir South",
            description="You are in a long room on the south shore of a large lake, far too deep and wide for crossing. There is a path along the stream to the east or west, a steep pathway climbing southwest along the edge of a chasm, and a path leading into a canyon to the southeast.",
            flags=0,
            exits={
                Direction.SE: "deep_canyon",
                Direction.SW: "chasm",
                Direction.WEST: "stream_view",
                Direction.EAST: "dam",
                Direction.NORTH: "reservoir"  # When drained can walk across
            }
        )
        
        self.rooms["reservoir"] = Room(
            id="reservoir",
            name="Reservoir",
            description="You are on the lake. Beaches can be seen north and south. Upstream a small stream enters the lake through a narrow cleft in the rocks. The dam can be seen downstream.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.SOUTH: "reservoir_south",
                Direction.NORTH: "reservoir_north"
            }
        )
        
        self.rooms["reservoir_north"] = Room(
            id="reservoir_north",
            name="Reservoir North",
            description="You are in a large cavernous room, north of a large lake. There is a slimy stairway leaving the room to the north.",
            flags=0,
            exits={
                Direction.SOUTH: "reservoir",
                Direction.NORTH: "atlantis_room"
            }
        )
        
        self.rooms["stream_view"] = Room(
            id="stream_view",
            name="Stream View",
            description="You are standing on a path beside a gently flowing stream. The path follows the stream, which flows from west to east.",
            flags=0,
            exits={
                Direction.EAST: "reservoir_south",
                Direction.WEST: "stream"
            }
        )
        
        self.rooms["stream"] = Room(
            id="stream",
            name="Stream",
            description="You are on the gently flowing stream. The upstream route is too narrow to navigate, and the downstream route is blocked by a dam.",
            flags=RoomFlag.ONWATER.value,
            exits={
                Direction.EAST: "reservoir",
                Direction.WEST: "sluice_gate"  # Only when dam open
            }
        )
        
        # Atlantis
        self.rooms["atlantis_room"] = Room(
            id="atlantis_room",
            name="Atlantis Room",
            description="This is an ancient room, long buried beneath the earth. The room is bare, but the walls are covered with decorations of great archaeological value. An exit lies to the south, and a staircase leads up.",
            flags=0,
            exits={
                Direction.SOUTH: "reservoir_north",
                Direction.UP: "cave_2"
            }
        )
        
        # Maze
        self.rooms["maze_1"] = Room(
            id="maze_1",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "troll_room",
                Direction.NORTH: "maze_1",
                Direction.SOUTH: "maze_2",
                Direction.EAST: "maze_4"
            }
        )
        
        self.rooms["maze_2"] = Room(
            id="maze_2",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.SOUTH: "maze_1",
                Direction.NORTH: "maze_4",
                Direction.EAST: "maze_3"
            }
        )
        
        self.rooms["maze_3"] = Room(
            id="maze_3",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_2",
                Direction.NORTH: "maze_4",
                Direction.UP: "maze_5"
            }
        )
        
        self.rooms["maze_4"] = Room(
            id="maze_4",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike. A skeleton, probably the remains of a luckless adventurer, lies here.",
            flags=0,
            exits={
                Direction.WEST: "maze_1",
                Direction.NORTH: "maze_2",
                Direction.SOUTH: "maze_3"
            }
        )
        
        self.rooms["maze_5"] = Room(
            id="maze_5",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.EAST: "dead_end_1",
                Direction.NORTH: "maze_6",
                Direction.DOWN: "maze_3"
            }
        )
        
        self.rooms["maze_6"] = Room(
            id="maze_6",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_7",
                Direction.EAST: "maze_7",
                Direction.WEST: "maze_7",
                Direction.UP: "maze_9"
            }
        )
        
        self.rooms["maze_7"] = Room(
            id="maze_7",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.UP: "maze_14",
                Direction.WEST: "maze_6",
                Direction.NE: "dead_end_1",
                Direction.EAST: "maze_8",
                Direction.SOUTH: "maze_15"
            }
        )
        
        self.rooms["maze_8"] = Room(
            id="maze_8",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.NE: "maze_7",
                Direction.WEST: "maze_8",
                Direction.SE: "dead_end_2"
            }
        )
        
        self.rooms["maze_9"] = Room(
            id="maze_9",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_6",
                Direction.SOUTH: "maze_10",
                Direction.EAST: "maze_12",
                Direction.WEST: "maze_13",
                Direction.NORTH: "maze_11"
            }
        )
        
        self.rooms["maze_10"] = Room(
            id="maze_10",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.EAST: "maze_9",
                Direction.WEST: "maze_13",
                Direction.UP: "maze_5"
            }
        )
        
        self.rooms["maze_11"] = Room(
            id="maze_11",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_12",
                Direction.SW: "grating_room",
                Direction.EAST: "maze_13",
                Direction.WEST: "maze_11",
                Direction.UP: "maze_9"
            }
        )
        
        self.rooms["maze_12"] = Room(
            id="maze_12",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.UP: "maze_11",
                Direction.SW: "maze_5",
                Direction.EAST: "maze_9",
                Direction.DOWN: "dead_end_1",
                Direction.NORTH: "maze_13"
            }
        )
        
        self.rooms["maze_13"] = Room(
            id="maze_13",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.DOWN: "maze_12",
                Direction.WEST: "maze_11",
                Direction.NE: "grating_room",
                Direction.SOUTH: "maze_10",
                Direction.EAST: "maze_9"
            }
        )
        
        self.rooms["maze_14"] = Room(
            id="maze_14",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_15",
                Direction.NE: "maze_7",
                Direction.NW: "maze_15"
            }
        )
        
        self.rooms["maze_15"] = Room(
            id="maze_15",
            name="Maze",
            description="This is part of a maze of twisty little passages, all alike.",
            flags=0,
            exits={
                Direction.WEST: "maze_14",
                Direction.SOUTH: "cyclops_room",
                Direction.NE: "maze_7"
            }
        )
        
        self.rooms["dead_end_1"] = Room(
            id="dead_end_1",
            name="Dead End",
            description="You have come to a dead end in the maze.",
            flags=0,
            exits={
                Direction.SOUTH: "maze_11"
            }
        )
        
        self.rooms["dead_end_2"] = Room(
            id="dead_end_2",
            name="Dead End",
            description="You have come to a dead end in the maze.",
            flags=0,
            exits={
                Direction.NW: "maze_8"
            }
        )
        
        self.rooms["grating_room"] = Room(
            id="grating_room",
            name="Grating Room",
            description="You are in a small room near the maze. There are twisty passages in the immediate vicinity. Above you is a grating locked with a skull-and-crossbones lock.",
            flags=0,
            exits={
                Direction.SW: "maze_11",
                Direction.NE: "maze_13",
                Direction.UP: "clearing"  # Only if grating unlocked
            }
        )
        
        # Cyclops and Treasure Room
        self.rooms["cyclops_room"] = Room(
            id="cyclops_room",
            name="Cyclops Room",
            description="This room has an exit on the west side, and a staircase leading up. A cyclops, who looks prepared to eat horses (much less mere adventurers), blocks the staircase. From his state of health, and the bloodstains on the walls, you gather that he is not very friendly, though he likes people.",
            flags=0,
            exits={
                Direction.WEST: "maze_15",
                Direction.UP: "treasure_room"  # Only if cyclops gone
            }
        )
        
        self.rooms["treasure_room"] = Room(
            id="treasure_room",
            name="Treasure Room",
            description="This is a large room, whose north wall is solid granite. A number of discarded bags, which crumble at your touch, are scattered about on the floor. There is an exit down and what appears to be a chimney in the east corner of the room.",
            flags=0,
            exits={
                Direction.DOWN: "cyclops_room",
                Direction.EAST: "strange_passage"
            }
        )
        
        self.rooms["strange_passage"] = Room(
            id="strange_passage",
            name="Strange Passage",
            description="This is a long passage. To the west is one entrance. On the east there is an old wooden door, with a large opening in it (about cyclops sized).",
            flags=0,
            exits={
                Direction.WEST: "treasure_room",
                Direction.EAST: "living_room"  # Through door
            }
        )
        
        # Gallery and Studio
        self.rooms["east_of_chasm"] = Room(
            id="east_of_chasm",
            name="East of Chasm",
            description="You are on the east edge of a chasm, the bottom of which cannot be seen. A narrow passage goes north, and the path you are on continues to the east.",
            flags=0,
            exits={
                Direction.NORTH: "cellar",
                Direction.EAST: "gallery"
            }
        )
        
        self.rooms["gallery"] = Room(
            id="gallery",
            name="Gallery",
            description="This is an art gallery. Most of the paintings have been stolen by vandals with exceptional taste. The vandals left through the north, south, east, or west exit.",
            flags=0,
            exits={
                Direction.NORTH: "studio",
                Direction.SOUTH: "east_of_chasm",
                Direction.EAST: "studio",
                Direction.WEST: "east_of_chasm"
            }
        )
        
        self.rooms["studio"] = Room(
            id="studio",
            name="Studio",
            description="This appears to have been an artist's studio. The walls and floors are splattered with paints of 69 different colors. Strangely enough, nothing of value is hanging here. At the north and northwest of the room are small doors.",
            flags=0,
            exits={
                Direction.SOUTH: "gallery",
                Direction.NORTH: "gallery",
                Direction.UP: "kitchen"  # Through chimney
            }
        )
        
        # Temple Area
        self.rooms["engravings_cave"] = Room(
            id="engravings_cave",
            name="Engravings Cave",
            description="You have entered a low cave with passages leading northwest and east. There are old engravings on the walls here.",
            flags=0,
            exits={
                Direction.NW: "round_room",
                Direction.EAST: "dome_room"
            }
        )
        
        self.rooms["dome_room"] = Room(
            id="dome_room",
            name="Dome Room",
            description="You are at the periphery of a large dome, which forms the ceiling of another room below. Protecting you from a precipitous drop is a wooden railing which circles the dome.",
            flags=0,
            exits={
                Direction.WEST: "engravings_cave",
                Direction.DOWN: "torch_room"  # Via rope
            }
        )
        
        self.rooms["torch_room"] = Room(
            id="torch_room",
            name="Torch Room",
            description="This is a large room with a prominent doorway leading to a down staircase. Above you is a large dome. Up around the edge of the dome (20 feet up) is a wooden railing. In the center of the room sits a white marble pedestal.",
            flags=0,
            exits={
                Direction.SOUTH: "temple",
                Direction.DOWN: "north_temple",
                Direction.UP: "dome_room"  # Via rope
            }
        )
        
        self.rooms["temple"] = Room(
            id="temple",
            name="Temple",
            description="This is the north end of a large temple. On the east wall is an ancient inscription, probably a prayer in a long-forgotten language. Below the prayer is a staircase leading down. The west wall is solid granite. The exit to the north end of the temple is through huge marble pillars.",
            flags=0,
            exits={
                Direction.NORTH: "torch_room",
                Direction.EAST: "egyptian_room",
                Direction.DOWN: "egyptian_room",
                Direction.SOUTH: "altar"
            }
        )
        
        self.rooms["altar"] = Room(
            id="altar",
            name="Altar",
            description="This is the south end of a large temple. In front of you is what appears to be an altar. In one corner is a small hole in the floor which leads into darkness. You probably could not get back up it.",
            flags=0,
            exits={
                Direction.NORTH: "temple",
                Direction.DOWN: "cave_1"  # One way
            }
        )
        
        self.rooms["egyptian_room"] = Room(
            id="egyptian_room",
            name="Egyptian Room",
            description="This is a room which looks like an Egyptian tomb. There is an ascending staircase to the west.",
            flags=0,
            exits={
                Direction.WEST: "temple",
                Direction.UP: "temple"
            }
        )
        
        self.rooms["north_temple"] = Room(
            id="north_temple",
            name="North Temple",
            description="This is a room of large proportions filled with religious objects, paintings, and a digital clock which has stopped. There is a door to the west and a staircase leading up.",
            flags=0,
            exits={
                Direction.UP: "torch_room",
                Direction.WEST: "entrance_to_hades",
                Direction.SOUTH: "south_temple"
            }
        )
        
        self.rooms["south_temple"] = Room(
            id="south_temple",
            name="South Temple",
            description="This is the south end of a large temple. There is a door to the west, and a staircase leading up. The door is barred from the other side.",
            flags=0,
            exits={
                Direction.NORTH: "north_temple",
                Direction.UP: "treasure_room",
                Direction.WEST: "south_temple"  # Barred
            }
        )
        
        # Land of the Dead
        self.rooms["entrance_to_hades"] = Room(
            id="entrance_to_hades",
            name="Entrance to Hades",
            description="You are outside a large gate, on which is inscribed:\n\n\"Abandon every hope, all ye who enter here!\"\n\nThe gate is open; through it you can see a desolation, with a pile of mangled bodies in one corner. Thousands of voices, lamenting some hideous fate, can be heard. The way through the gate is barred by evil spirits, who jeer at your attempts to pass.",
            flags=0,
            exits={
                Direction.NORTH: "cave_1",
                Direction.UP: "cave_2",
                Direction.SOUTH: "land_of_the_dead",  # Blocked by spirits unless exorcised
                Direction.EAST: "north_temple"
            }
        )
        
        self.rooms["land_of_the_dead"] = Room(
            id="land_of_the_dead",
            name="Land of the Living Dead",
            description="You have entered the Land of the Living Dead. Thousands of lost souls can be heard weeping and moaning. In the corner are stacked the remains of dozens of previous adventurers less fortunate than yourself. A passage exits to the north.",
            flags=0,
            exits={
                Direction.NORTH: "entrance_to_hades"
            }
        )
        
    def _init_objects(self):
        """Initialize all objects"""
        
        # Basic Items
        self.objects["mailbox"] = GameObject(
            id="mailbox",
            name="mailbox",
            description="small mailbox",
            examine_text="It's a small mailbox.",
            flags=ObjectFlag.CONTAINER.value | ObjectFlag.CLOSED.value,
            location="west_of_house"
        )
        
        self.objects["leaflet"] = GameObject(
            id="leaflet", 
            name="leaflet",
            description="leaflet",
            examine_text="\"WELCOME TO ZORK!\n\nZORK is a game of adventure, danger, and low cunning. In it you will explore some of the most amazing territory ever seen by mortals. No computer should be without one!\"",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="mailbox",
            size=1
        )
        
        self.objects["mat"] = GameObject(
            id="mat",
            name="mat", 
            description="welcome mat",
            examine_text="Welcome to Zork!",
            initial_text="A rubber mat saying 'Welcome to Zork!' lies by the door.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="west_of_house",
            size=2
        )
        
        # Light Sources
        self.objects["lamp"] = GameObject(
            id="lamp",
            name="lamp",
            description="brass lantern",
            examine_text="It is a shiny brass lamp. It is not currently lit.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TURNNABLE.value,
            location="living_room",
            size=3
        )
        
        self.objects["torch"] = GameObject(
            id="torch",
            name="torch",
            description="ivory torch",
            examine_text="The torch is ivory-colored, inlaid with gold.",
            initial_text="Sitting on the pedestal is a flaming torch, made of ivory.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.LIGHT.value | ObjectFlag.TURNEDON.value | ObjectFlag.FLAMMABLE.value | ObjectFlag.TREASURE.value,
            location="torch_room",
            size=2,
            value=14
        )
        
        self.objects["candles"] = GameObject(
            id="candles",
            name="candles",
            description="pair of candles",
            examine_text="The candles are not lit.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.FLAMMABLE.value,
            location="altar",
            size=2
        )
        
        self.objects["matchbook"] = GameObject(
            id="matchbook",
            name="matchbook",
            description="matchbook",
            examine_text="The matchbook is from the Borphee Grill. You have 5 matches.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.READABLE.value,
            location="dam_lobby",
            size=1
        )
        
        # Weapons
        self.objects["sword"] = GameObject(
            id="sword",
            name="sword",
            description="elvish sword",
            examine_text="It's an elvish sword of great antiquity. It glows with a faint blue glow.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="living_room",
            size=3
        )
        
        self.objects["knife"] = GameObject(
            id="knife",
            name="knife",
            description="nasty knife",
            examine_text="It's a nasty-looking knife.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="attic",
            size=1
        )
        
        self.objects["axe"] = GameObject(
            id="axe",
            name="axe",
            description="bloody axe",
            examine_text="It's a bloody axe.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location=None,  # Troll has it initially
            size=3
        )
        
        self.objects["stiletto"] = GameObject(
            id="stiletto",
            name="stiletto",
            description="stiletto",
            examine_text="It's a vicious stiletto.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location=None,  # Thief has it
            size=1
        )
        
        self.objects["rusty_knife"] = GameObject(
            id="rusty_knife",
            name="knife",
            description="rusty knife",
            examine_text="It's a rusty knife.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.WEAPON.value,
            location="maze_4",
            size=1
        )
        
        # Tools
        self.objects["rope"] = GameObject(
            id="rope",
            name="rope",
            description="rope",
            examine_text="It's a sturdy hemp rope.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="attic",
            size=2
        )
        
        self.objects["shovel"] = GameObject(
            id="shovel",
            name="shovel",
            description="shovel",
            examine_text="It's a sturdy shovel.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="white_cliffs_beach_south",
            size=3
        )
        
        self.objects["screwdriver"] = GameObject(
            id="screwdriver",
            name="screwdriver",
            description="screwdriver",
            examine_text="It's a flathead screwdriver.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="maintenance_room",
            size=1
        )
        
        self.objects["wrench"] = GameObject(
            id="wrench",
            name="wrench",
            description="wrench",
            examine_text="It's a large adjustable wrench.",
            flags=ObjectFlag.TAKEABLE.value | ObjectFlag.TOOL.value,
            location="maintenance_room",
            size=2
        )