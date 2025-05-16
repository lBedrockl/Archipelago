from typing import cast, ClassVar, Optional, Dict, List, Set
from dataclasses import dataclass

from BaseClasses import ItemClassification, Location, Region
from .items import ERItemCategory, item_table

# Regions in approximate order of progression
#MARK: Location Order
region_order = [
    "Chapel of Anticipation",

    # Limgrave
    "Stranded Graveyard",
    "Fringefolk Hero's Grave",
    "Limgrave",
    "Church of Elleh",
    "Coastal Cave",
    "Church of Dragon Communion",
    "Groveside Cave",
    "Stormfoot Catacombs",
    "Gatefront Ruins",
    "Limgrave Tunnels",
    "Stormgate",
    "Stormhill Shack",
    "Waypoint Ruins",
    "Dragon-Burnt Ruins",
    "Murkwater Cave",
    "Mistwood Ruins",
    "Fort Haight",
    "Third Church of Marika",
    "LG Artist's Shack",
    "Summonwater Village",
    "Murkwater Catacombs",
    "Highroad Cave",
    "Deathtouched Catacombs",
    "Warmaster's Shack",

    # The hold
    "Roundtable Hold",

    # Weeping
    "Bridge of Sacrifice",
    "Weeping Peninsula",
    "Impaler's Catacombs",
    "Church of Pilgrimage",
    "Tombsward Catacombs",
    "Tombsward Cave",
    "Isolated Merchant's Shack",
    "Morne Tunnel",
    "Earthbore Cave",
    
    "Castle Morne",

    # Liurnia
    "Liurnia of The Lakes",
    "Chapel of Anticipation [Return]",

    # Caelid
    "Caelid",
    "Smoldering Church",
    "Bestial Sanctum",
    "Dragonbarrow Cave",
    "Fort Faroth",
    "Sellia Hideaway",
    "Cathedral of Dragon Communion",
    "Caelid Catacombs",
    "Caelid Waypoint Ruins",
    "Gaol Cave",
    "Fort Gael",
    "Street of Sages Ruins",
    
    "Redmane Castle",
    
    # Altus
    "Altus Plateau",

    # Leyndell
    "Leyndell, Royal Capital",
    "Divine Bridge",
    
    "Leyndell, Ashen Capital",

    # Haligtree
    "Miquella's Haligtree",
    "Elphael, Brace of the Haligtree",
]

#MARK: DLC Location Order
region_order_dlc = [
    #DLC
    "Gravesite Plain",
]

@dataclass
class ERLocationData:
    __location_id: ClassVar[int] = 7000000
    """The next location ID to use when creating location data."""

    name: str
    """The name of this location according to Archipelago.

    This needs to be unique within this world."""

    default_item_name: Optional[str]
    """The name of the item that appears by default in this location.

    If this is None, that indicates that this location is an "event" that's
    automatically considered accessed as soon as it's available. Events are used
    to indicate major game transitions that aren't otherwise gated by items so
    that progression balancing and item smoothing is more accurate for ER.
    """

    ap_code: Optional[int] = None
    """Archipelago's internal ID for this location (also known as its "address")."""

    region_value: int = 0
    """The relative value of items in this location's region.

    This is used to sort locations when placing items like the base game.
    """

    static: Optional[str] = None
    """The key in the static randomizer's Slots table that corresponds to this location.

    By default, the static randomizer chooses its location based on the region and the item name.
    If the item name is unique across the whole game, it can also look it up based on that alone. If
    there are multiple instances of the same item type in the same region, it will assume its order
    (in annotations.txt) matches Archipelago's order.

    In cases where this heuristic doesn't work, such as when Archipelago's region categorization or
    item name disagrees with the static randomizer's, this field is used to provide an explicit
    association instead.
    """

    missable: bool = False
    """Whether this item is possible to permanently lose access to.

    This is also used for items that are *technically* possible to get at any time, but are
    prohibitively difficult without blocking off other checks (items dropped by NPCs on death
    generally fall into this category).

    Missable locations are always marked as excluded, so they will never contain
    progression or useful items.
    """

    dlc: bool = False
    """Whether this location is only accessible if the DLC is enabled."""

    npc: bool = False
    """Whether this item is contingent on killing an NPC or following their quest."""

    prominent: bool = False
    """Whether this is one of few particularly prominent places for items to appear.

    This is a small number of locations (boss drops and progression locations)
    intended to be set as priority locations for players who don't want a lot of
    mandatory checks.

    For bosses with multiple drops, only one should be marked prominent.
    """

    progression: bool = False
    """Whether this location normally contains an item that blocks forward progress."""

    mainboss: bool = False
    """Whether this location is a reward for defeating a main boss."""

    boss: bool = False
    """Whether this location is a reward for defeating a boss."""

    drop: bool = False
    """Whether this is an item dropped by a (non-boss) enemy.

    This is automatically set to True if scarab, is True.
    """

    hostile_npc: bool = False
    """Whether this location is dropped by a hostile NPC."""

    shop: bool = False
    """Whether this location can appear in an NPC's shop."""

    conditional: bool = False
    """Whether this location is conditional on a progression item.

    This is used to track locations that won't become available until an unknown amount of time into
    the run, and as such shouldn't have "similar to the base game" items placed in them.
    """

    hidden: bool = False
    """Whether this location is particularly tricky to find.

    This is for players without an encyclopedic knowledge of ER who don't want to get stuck looking
    for an illusory wall or one random mob with a guaranteed drop.
    """

    scarab: bool = False
    """Whether this location is dropped by a scarab."""
    
    rise_puzzle: bool = False
    """Whether this location is a rise puzzle."""



    @property
    def is_event(self) -> bool:
        """Whether this location represents an event rather than a specific item pickup."""
        return self.default_item_name is None

    def __post_init__(self):
        if not self.is_event:
            self.ap_code = self.ap_code or ERLocationData.__location_id
            ERLocationData.__location_id += 1
        if self.scarab or self.hostile_npc: self.drop = True

    def location_groups(self) -> List[str]:
        """The names of location groups this location should appear in.

        This is computed from the properties assigned to this location."""
        names = []
        if self.mainboss: # any boss should be a prominent place
            names.append("Main Boss Rewards")
            self.prominent=True
        if self.boss: 
            names.append("Boss Rewards")
            self.prominent=True
        
        if self.prominent: names.append("Prominent")
        if self.progression: names.append("Progression")
        if self.hostile_npc: names.append("Hostile NPC Rewards")
        if self.npc: names.append("Friendly NPC Rewards")

        default_item = item_table[cast(str, self.default_item_name)]
        names.append({
                         ERItemCategory.GOODS: "Goods",
                         ERItemCategory.WEAPON: "Weapons",
                         ERItemCategory.ARMOR: "Armor",
                         ERItemCategory.ACCESSORY: "Accessory",
                         ERItemCategory.ASHOFWAR: "Ash of war",
                         ERItemCategory.CUSTOMWEAPON: "Upgraded Weapons",
                     }[default_item.category])
        if default_item.classification == ItemClassification.progression:
            names.append("Progression")

        return names


class ERLocation(Location):
    game: str = "EldenRing"
    data: ERLocationData

    def __init__(
            self,
            player: int,
            data: ERLocationData,
            parent: Optional[Region] = None,
            event: bool = False):
        super().__init__(player, data.name, None if event else data.ap_code, parent)
        self.data = data

# from ds3 locations.py

# * Avoid using vanilla enemy placements as landmarks, because these are
#   randomized by the enemizer by default. Instead, use generic terms like
#   "enemy", "boss", and "npc".

# * Location descriptions don't need to direct the player to the precise spot.
#   You can assume the player is broadly familiar with Eldenring or willing
#   to look at a vanilla guide. Just give a general area to look in or an idea
#   of what quest a check is connected to. Terseness is valuable: try to keep
#   each location description short enough that the whole line doesn't exceed
#   100 characters.

# * Use "[name] drop" for items that require killing an NPC who becomes hostile
#   as part of their normal quest, "kill [name]" for items that require killing
#   them even when they aren't hostile, and just "[name]" for items that are
#   naturally available as part of their quest.

# items that are always prominent, unless the check is missable or a boss drop
# golden seed, sacred tear and memory stone if not in a rise

# for descriptions 
# [area acronym]/[grace or location acronym]: [original item] - [what gives item, if it does] [direction from grace] or [very brief description]

# CD/AFCHN: Lifesteal Fist - scarab to NW         # grace
# LG/WR: Golden Rune [1] - graveyard S of WR      # location
# LG/(CE): Smithing Stone [1] - on anvil          # within location

# for shops with inf of an item, leave to be nothing

# Catacomb = CC, Cave = CV, Coast = CO

# Tombsward Ruins, Tower of Return = TwR, ToR

# ERLocationData(":  - ", ""),
#MARK: Locations
location_tables: Dict[str, List[ERLocationData]] = {
    "Chapel of Anticipation":[
        ERLocationData("CA: Ornamental Straight Sword - boss drop", "Ornamental Straight Sword", missable=True, boss=True),
        ERLocationData("CA: Golden Beast Crest Shield - boss drop", "Golden Beast Crest Shield", missable=True, boss=True),
    ],
    # MARK: Limgrave
    "Stranded Graveyard":[
        ERLocationData("LG/SG: Strength! - after cave of knowledge boss", "Strength!"),
        ERLocationData("LG/SG: Tarnished's Furled Finger - beside grace", "Tarnished's Furled Finger"),
        ERLocationData("LG/SG: Finger Severer - beside grace", "Finger Severer"),
    ],
    "Fringefolk Hero's Grave":[ # 2
        ERLocationData("LG/FHG: Poisonbone Dart x5 - top of first ramp", "Poisonbone Dart x5"),
        ERLocationData("LG/FHG: Golden Rune [5] - middle of second ramp pit", "Golden Rune [5]"),
        ERLocationData("LG/FHG: Lightning Grease x2 - drop into second ramp pit, left of fire spitter", "Lightning Grease x2"),
        ERLocationData("LG/FHG: Erdtree's Favor - altar by miniboss duo", "Erdtree's Favor"),
        ERLocationData("LG/FHG: Stonesword Key - drop into second ramp pit, past fire spitter, drop to bottom of big room", "Stonesword Key"),
        ERLocationData("LG/FHG: Erdtree Greatbow - kill chariot", "Erdtree Greatbow", drop=True, missable=True), #requires shackle or bow
        ERLocationData("LG/FHG: Great Arrow x10 - kill chariot", "Great Arrow x10", drop=True, missable=True), #requires shackle or bow
        ERLocationData("LG/FHG: Dragonwound Grease - top of third ramp", "Dragonwound Grease"),
        ERLocationData("LG/FHG: Dragon Communion Seal - enemy drop top of third ramp", "Dragon Communion Seal", drop=True),
        ERLocationData("LG/FHG: Grave Glovewort [1] - middle of lower third ramp", "Grave Glovewort [1]"),
        ERLocationData("LG/FHG: Golden Seed - boss drop", "Golden Seed", boss=True),
        ERLocationData("LG/FHG: Banished Knight Oleg - boss drop", "Banished Knight Oleg", boss=True),
    ],
    "Limgrave":[ # World locations
        # misc stuff
        ERLocationData("LG/SG: Silver-Pickled Fowl Foot x2 - hidden drop down behind SG entrance", "Silver-Pickled Fowl Foot x2", hidden=True),
        ERLocationData("LG/TFS: Golden Halberd - first field boss", "Golden Halberd", boss=True),
        ERLocationData("LG/CE: Golden Rune [1] - E of CE", "Golden Rune [1]"),
        ERLocationData("LG/GC: Kukri x4 - E of GC", "Kukri x4"),
        ERLocationData("LG/SC: Crossed Legs - on ruin above SC", "Crossed Legs"),
        ERLocationData("LG/SC: Starlight Shards - cliff above W of SC", "Starlight Shards"),
        ERLocationData("LG/SS: Golden Seed - golden tree SE of SS", "Golden Seed", prominent=True),
        ERLocationData("LG/SS: Smithing Stone [1] x3 - SE of SS", "Smithing Stone [1] x3"),
        ERLocationData("LG/SS: Ash of War: Wild Strikes - scarab NW of SS", "Ash of War: Wild Strikes", scarab=True),
        ERLocationData("LG/SS: Lump of Flesh - under bridge NW of SS", "Lump of Flesh"),
        ERLocationData("LG/MCV: Reduvia - npc invader E of MCV", "Reduvia", hostile_npc=True),
        ERLocationData("LG/MR: Sacrificial Twig - W of MR", "Sacrificial Twig"),
        ERLocationData("LG/MR: Golden Rune [1] - N of MR", "Golden Rune [1]"),
        ERLocationData("LG/TCM: Ash of War: Sacred Blade - scarab N of TCM", "Ash of War: Sacred Blade", scarab=True),
        ERLocationData("LG/TCM: Neutralizing Boluses - NE of TCM", "Neutralizing Boluses"),
        ERLocationData("LG/AS: Somber Smithing Stone [1] - scarab W of AS", "Somber Smithing Stone [1]", scarab=True),
        ERLocationData("LG/MCO: Golden Rune [2] - W of MCO", "Golden Rune [2]"),
        ERLocationData("LG/MCO: Armorer's Cookbook [1] - SW of MCO", "Armorer's Cookbook [1]"),
        ERLocationData("LG/MCO: Poisonbloom x2 - NE of MCO", "Poisonbloom x2"),
        ERLocationData("LG/HC: Turtle Neck Meat - N above HC", "Turtle Neck Meat"),
        ERLocationData("LG/DC: Golden Rune [3] - E of DC", "Golden Rune [3]"),
        ERLocationData("LG/DC: Lance Talisman - NE of DC", "Lance Talisman"),
        ERLocationData("LG/DC: Soporific Grease x3 - above on the pillar of divine bridge N of DC", "Soporific Grease x3", hidden=True),

        # Near CC
        ERLocationData("LG/CC: Gold-Pickled Fowl Foot - SE of CC along beach", "Gold-Pickled Fowl Foot"),
        ERLocationData("LG/CC: Land Octopus Ovary - NW of CC along beach", "Land Octopus Ovary"),
        ERLocationData("LG/CC: Strip of White Flesh - NW of CC along beach", "Strip of White Flesh"),
        ERLocationData("LG/CC: Ash of War: Stamp (Sweep) - scarab NW of CC along beach", "Ash of War: Stamp (Sweep)"),
        # shop
        ERLocationData("LG/CC: Neutralizing Boluses x5 - Nomadic Merchant SE of CC", "Neutralizing Boluses x5", shop=True),
        ERLocationData("LG/CC: Stanching Boluses x3 - Nomadic Merchant SE of CC", "Stanching Boluses x3", shop=True),
        ERLocationData("LG/CC: Stimulating Boluses x2 - Nomadic Merchant SE of CC", "Stimulating Boluses x2", shop=True),
        ERLocationData("LG/CC: Smithing Stone [1] x3 - Nomadic Merchant SE of CC", "Smithing Stone [1] x3", shop=True),
        ERLocationData("LG/CC: Armorer's Cookbook [2] - Nomadic Merchant SE of CC", "Armorer's Cookbook [2]", shop=True),
        ERLocationData("LG/CC: Broadsword - Nomadic Merchant SE of CC", "Broadsword", shop=True),
        ERLocationData("LG/CC: Club - Nomadic Merchant SE of CC", "Club", shop=True),
        ERLocationData("LG/CC: Shortbow - Nomadic Merchant SE of CC", "Shortbow", shop=True),
        ERLocationData("LG/CC: Iron Roundshield - Nomadic Merchant SE of CC", "Iron Roundshield", shop=True),
        ERLocationData("LG/CC: Note: Land Squirts - Nomadic Merchant SE of CC", "Note: Land Squirts", shop=True),
        ERLocationData("LG/CC: Note: Stonedigger Trolls - Nomadic Merchant SE of CC", "Note: Stonedigger Trolls", shop=True),
        # Near WR
        ERLocationData("LG/WR: Greataxe - carriage W of WR", "Greataxe"),
        ERLocationData("LG/WR: Gold-Pickled Fowl Foot - NW of WR", "Gold-Pickled Fowl Foot"),
        ERLocationData("LG/WR: Smoldering Butterfly x4 - SW of WR", "Smoldering Butterfly x4"),
        ERLocationData("LG/WR: Glintstone Staff - enemy drop S of WR under ruin", "Glintstone Staff", drop=True),
        ERLocationData("LG/WR: Golden Rune [1] 1 - graveyard S of WR", "Golden Rune [1]"),
        ERLocationData("LG/WR: Golden Rune [1] 2 - graveyard S of WR", "Golden Rune [1]"),
        ERLocationData("LG/WR: Golden Rune [1] 3 - graveyard S of WR", "Golden Rune [1]"),
        ERLocationData("LG/WR: Golden Rune [2] - graveyard S of WR", "Golden Rune [2]"),
        ERLocationData("LG/WR: Golden Rune [3] - graveyard S of WR", "Golden Rune [3]"),
        # Near ALN grace
        ERLocationData("LG/ALN: Mushroom x10 - Boc to SE", "Mushroom x10", missable=True),
        ERLocationData("LG/ALN: Arteria Leaf - to SE", "Arteria Leaf"),
        ERLocationData("LG/ALN: Ash of War: Determination - scarab to SE", "Ash of War: Determination", scarab=True),
        ERLocationData("LG/ALN: Smithing Stone [1] - bridge to SE", "Smithing Stone [1]"),
        ERLocationData("LG/ALN: Fire Grease - under bridge to SE", "Fire Grease"),
        ERLocationData("LG/ALN: Ash of War: Repeating Thrust - night boss drop to SE", "Ash of War: Repeating Thrust", boss=True),
        ERLocationData("LG/ALN: Somber Smithing Stone [1] - after bridge to SE", "Somber Smithing Stone [1]"),
        # Near ALS grace
        ERLocationData("LG/ALS: Ash of War: Unsheathe - scarab to NW", "Ash of War: Unsheathe", scarab=True),
        ERLocationData("LG/ALS: Crab Eggs - to NW", "Crab Eggs"),
        ERLocationData("LG/ALS: Sliver of Meat - to W", "Sliver of Meat"),
        ERLocationData("LG/ALS: Golden Rune [2] - to S", "Golden Rune [2]"),
        ERLocationData("LG/ALS: Larval Tear - transforming enemy to E", "Larval Tear"),
        ERLocationData("LG/ALS: Golden Rune [1] - to SE high on cliff", "Golden Rune [1]"),
        ERLocationData("LG/ALS: Starlight Shards - to SE high on cliff", "Starlight Shards"),
        ERLocationData("LG/ALS: Royal House Scroll - to E on ruin", "Royal House Scroll"),
        ERLocationData("LG/ALS: Golden Rune [1] - to E", "Golden Rune [1]"),
        ERLocationData("LG/ALS: Great Épée - to E in chest", "Great Épée"),
        # Near Forlorn Hound Evergaol
        ERLocationData("LG/FHE: Large Club - S of Evergaol", "Large Club"),
        ERLocationData("LG/FHE: Ruin Fragment x3 - SW of Evergaol", "Ruin Fragment x3"),
        # Near SR grace
        ERLocationData("LG/SR: Crab Eggs - to S", "Crab Eggs"),
        ERLocationData("LG/SR: Slumbering Egg - to E on ruin", "Slumbering Egg"),
        ERLocationData("LG/SR: Golden Rune [1] - to N", "Golden Rune [1]"),
        ERLocationData("LG/SR: Lump of Flesh x3 - lower beach to W", "Lump of Flesh x3"),
        ERLocationData("LG/SR: Ash of War: Gravitas - enemy drop lower beach to NW", "Ash of War: Gravitas", drop=True),
        ERLocationData("LG/SR: Haligdrake Talisman - cave entrance lower beach to NW", "Haligdrake Talisman"),
        ERLocationData("LG/SR: Incantation Scarab - \"Homing Instinct\" Painting reward to NW", "Incantation Scarab"),
        # Near DBR
        ERLocationData("LG/DBR: Smithing Stone [1] - W of DBR", "Smithing Stone [1]"),
        ERLocationData("LG/DBR: Arteria Leaf - NE of DBR", "Arteria Leaf"),
        ERLocationData("LG/DBR: Dragon Heart - boss drop N of DBR", "Dragon Heart", boss=True),
        # Near MO grace
        ERLocationData("LG/MO: Magic Grease - to NE", "Magic Grease"),
        ERLocationData("LG/MO: Golden Rune [1] - on ruin to SW", "Golden Rune [1]"),
        ERLocationData("LG/MO: Golden Rune [5] - to SE", "Golden Rune [5]"),
        ERLocationData("LG/MO: Throwing Dagger x5 - to SE", "Throwing Dagger x5"),
        ERLocationData("LG/MO: Gold-Tinged Excrement x5 - to SE", "Gold-Tinged Excrement x5"),

        # Kenneth Haight
        ERLocationData("LG/MO: Erdsteel Dagger - kill FH enemy Kenneth Haight to NE", "Erdsteel Dagger",npc=True ,missable=True),
        ERLocationData("LG/MO: Golden Seed - kill Kenneth Haight to NE", "Golden Seed", npc=True, missable=True),

        # Near SRW
        ERLocationData("LG/SRW: Map: Limgrave, East - map pillar W of SRW", "Map: Limgrave, East", prominent=True),
        ERLocationData("LG/SRW: Nomadic Warrior's Cookbook [4] - W of SRW", "Nomadic Warrior's Cookbook [4]"),
        ERLocationData("LG/SRW: Strip of White Flesh x3 - of SRW", "Strip of White Flesh x3"),
        # Near ME Minor Erdtree
        ERLocationData("LG/ME: Ash of War: Ground Slam - W of ME", "Ash of War: Ground Slam", scarab=True),
        ERLocationData("LG/ME: Thin Beast Bones x3 - W of ME", "Thin Beast Bones x3"),
        # shop
        ERLocationData("LG/ME: Festering Bloody Finger x5 - Nomadic Merchant S of ME", "Festering Bloody Finger x5", shop=True),
        ERLocationData("LG/ME: Sliver of Meat x5 - Nomadic Merchant S of ME", "Sliver of Meat x5", shop=True),
        ERLocationData("LG/ME: Beast Liver x5 - Nomadic Merchant S of ME", "Beast Liver x5", shop=True),
        ERLocationData("LG/ME: Lump of Flesh x3 - Nomadic Merchant S of ME", "Lump of Flesh x3", shop=True),
        ERLocationData("LG/ME: Trina's Lily x3 - Nomadic Merchant S of ME", "Trina's Lily x3", shop=True),
        ERLocationData("LG/ME: Smithing Stone [1] x3 - Nomadic Merchant S of ME", "Smithing Stone [1] x3", shop=True),
        ERLocationData("LG/ME: Nomadic Warrior's Cookbook [5] - Nomadic Merchant S of ME", "Nomadic Warrior's Cookbook [5]", shop=True),
        ERLocationData("LG/ME: Armorer's Cookbook [3] - Nomadic Merchant S of ME", "Armorer's Cookbook [3]", shop=True),
        ERLocationData("LG/ME: Hand Axe - Nomadic Merchant S of ME", "Hand Axe", shop=True),
        ERLocationData("LG/ME: St. Trina's Arrow x10 - Nomadic Merchant S of ME", "St. Trina's Arrow x10", shop=True),
        ERLocationData("LG/ME: Riveted Wooden Shield - Nomadic Merchant S of ME", "Riveted Wooden Shield", shop=True),
        ERLocationData("LG/ME: Blue-Gold Kite Shield - Nomadic Merchant S of ME", "Blue-Gold Kite Shield", shop=True),

        # Near FHW
        ERLocationData("LG/FHW: Golden Seed - golden tree to E", "Golden Seed", prominent=True),
        ERLocationData("LG/FHW: Golden Rune [1] - beach to SW", "Golden Rune [1]"),
        ERLocationData("LG/FHW: Golden Rune [1] 1 - graveyard to SW", "Golden Rune [1]"),
        ERLocationData("LG/FHW: Golden Rune [1] 2 - graveyard to SW", "Golden Rune [1]"),
        ERLocationData("LG/FHW: Golden Rune [1] 3 - graveyard to SW", "Golden Rune [1]"),
        ERLocationData("LG/FHW: Golden Rune [1] 4 - graveyard to SW", "Golden Rune [1]"),
        ERLocationData("LG/FHW: Golden Rune [2] 1 - graveyard to SW", "Golden Rune [2]"),
        ERLocationData("LG/FHW: Golden Rune [2] 2 - graveyard to SW", "Golden Rune [2]"),
        ERLocationData("LG/FHW: Golden Rune [3] - graveyard to SW", "Golden Rune [3]"),
        ERLocationData("LG/FHW: Golden Rune [4] - graveyard to SW", "Golden Rune [4]"),
        # Near SB grace
        ERLocationData("LG/SB: Smithing Stone [1] x2 - on bridge to E", "Smithing Stone [1] x2"),
        ERLocationData("LG/SB: Golden Rune [1] - past bridge to SE", "Golden Rune [1]"),
        ERLocationData("LG/SB: Smithing Stone [1] - to S", "Smithing Stone [1]"),
        # shop
        ERLocationData("LG/SB: Pickled Turtle Neck x3 - Nomadic Merchant to E", "Pickled Turtle Neck x3", shop=True),
        ERLocationData("LG/SB: Smithing Stone [1] x3 - Nomadic Merchant to E", "Smithing Stone [1] x3", shop=True),
        ERLocationData("LG/SB: Cracked Pot - Nomadic Merchant to E", "Cracked Pot", shop=True),
        ERLocationData("LG/SB: Nomadic Warrior's Cookbook [3] - Nomadic Merchant to E", "Nomadic Warrior's Cookbook [3]", shop=True),
        ERLocationData("LG/SB: Short Sword - Nomadic Merchant to E", "Short Sword", shop=True),
        ERLocationData("LG/SB: Halberd - Nomadic Merchant to E", "Halberd", shop=True),
        ERLocationData("LG/SB: Bandit Mask - Nomadic Merchant to E", "Bandit Mask", shop=True),
        ERLocationData("LG/SB: Note: Flame Chariots - Nomadic Merchant to E", "Note: Flame Chariots", shop=True),
        # Near SWVO  summonwater village outskirts
        ERLocationData("LG/SWVO: Fevor's Cookbook [1] - graveyard to S", "Fevor's Cookbook [1]"),
        ERLocationData("LG/SWVO: Golden Rune [1] 1 - graveyard to S", "Golden Rune [1]"),
        ERLocationData("LG/SWVO: Golden Rune [1] 2 - graveyard to S", "Golden Rune [1]"),
        ERLocationData("LG/SWVO: Golden Rune [1] 3 - graveyard to S", "Golden Rune [1]"),
        ERLocationData("LG/SWVO: Golden Rune [2] - graveyard to S", "Golden Rune [2]"),
        ERLocationData("LG/SWVO: Golden Rune [4] 1 - graveyard to S", "Golden Rune [4]"),
        ERLocationData("LG/SWVO: Golden Rune [4] 2 - graveyard to S", "Golden Rune [4]"),
        ERLocationData("LG/SWVO: Golden Rune [6] - graveyard to S", "Golden Rune [6]"),
        # Near SWV
        ERLocationData("LG/SWV: Smithing Stone [2] - down S of SMV", "Smithing Stone [2]"),
        ERLocationData("LG/SWV: Golden Rune [1] 1 - graveyard SE of SMV", "Golden Rune [1]"),
        ERLocationData("LG/SWV: Golden Rune [1] 2 - graveyard SE of SMV", "Golden Rune [1]"),
        ERLocationData("LG/SWV: Golden Rune [1] 3 - graveyard SE of SMV", "Golden Rune [1]"),
        ERLocationData("LG/SWV: Golden Rune [1] 4 - graveyard SE of SMV", "Golden Rune [1]"),
        ERLocationData("LG/SWV: Golden Rune [1] 5 - graveyard SE of SMV", "Golden Rune [1]"),
        ERLocationData("LG/SWV: Golden Rune [2] - graveyard SE of SMV", "Golden Rune [2]"),
        ERLocationData("LG/SWV: Golden Rune [5] - graveyard SE of SMV", "Golden Rune [5]"),
        ERLocationData("LG/SWV: Golden Rune [4] - ruins NE of SMV", "Golden Rune [4]"),
        
        # Near WS
        ERLocationData("LG/WS: Fire Arrow x5 - W of WS", "Fire Arrow x5"),
        ERLocationData("LG/WS: Golden Rune [1] 1 - graveyard SW of WS", "Golden Rune [1]"),
        ERLocationData("LG/WS: Golden Rune [1] 2 - graveyard SW of WS", "Golden Rune [1]"),
        ERLocationData("LG/WS: Golden Rune [1] 3 - graveyard SW of WS", "Golden Rune [1]"),
        ERLocationData("LG/WS: Golden Rune [1] 4 - graveyard SW of WS", "Golden Rune [1]"),
        ERLocationData("LG/WS: Golden Rune [2] 1 - graveyard SW of WS", "Golden Rune [2]"),
        ERLocationData("LG/WS: Golden Rune [2] 2 - graveyard SW of WS", "Golden Rune [2]"),
        ERLocationData("LG/WS: Golden Rune [3] - graveyard SW of WS", "Golden Rune [3]"),
        ERLocationData("LG/WS: Golden Rune [5] - graveyard SW of WS", "Golden Rune [5]"),
        ERLocationData("LG/WS: Beast Liver - SE of WS", "Beast Liver"),
        ERLocationData("LG/WS: Blue-Feathered Branchsword - night boss drop SE of WS", "Blue-Feathered Branchsword", boss=True),
        ERLocationData("LG/WS: Smithing Stone [1] x5 - breakable statue SE of WS", "Smithing Stone [1] x5"),
        ERLocationData("LG/WS: Smithing Stone [2] - breakable statue SE of WS", "Smithing Stone [2]"),
        ERLocationData("LG/WS: Exalted Flesh - enemy camp NE of WS", "Exalted Flesh"),
        ERLocationData("LG/WS: Beast Crest Heater Shield - chest within enemy camp NE of WS", "Beast Crest Heater Shield"),
        ERLocationData("LG/WS: Lance - on ruin in enemy camp NE of WS", "Lance"),
        ERLocationData("LG/WS: Ash of War: Golden Vow - enemy drop NE of WS", "Ash of War: Golden Vow", drop=True),
        ERLocationData("LG/WS: Somber Smithing Stone [1] - scarab on ruin NE of WS", "Somber Smithing Stone [1]", scarab=True),
        ERLocationData("LG/WS: Strength-knot Crystal Tear - on cliff NW of WS", "Strength-knot Crystal Tear"),
        
        # Near sv first boss arena
        ERLocationData("LG/SV: Smithing Stone [1] - S of first SV boss arena W side", "Smithing Stone [1]"),
        ERLocationData("LG/SV: Magic Grease x3 - S of first SV boss arena E side item 1", "Magic Grease x3"),
        ERLocationData("LG/SV: Godrick Soldier Ashes - S of first SV boss arena E side item 2", "Godrick Soldier Ashes"),
        ERLocationData("LG/SV: Bloodrose x3 - S of first SV boss arena E side item 3", "Bloodrose x3"),
        
        # broken bridge E of sv
        ERLocationData("LG/SV: Nomadic Warrior's Cookbook [7] - E of SV on broken bridge", "Nomadic Warrior's Cookbook [7]"),
        ERLocationData("LG/SV: Ash of War: Storm Wall - scarab E of SV after broken bridge", "Ash of War: Storm Wall", scarab=True),
        
        # Colo
        ERLocationData("LG/LC: Hammer Talisman - invader drop", "Hammer Talisman", hostile_npc=True, missable=True),
        ERLocationData("LG/LC: Small Red Effigy - by door", "Small Red Effigy"),
        ERLocationData("LG/LC: Duelist's Furled Finger - by door", "Duelist's Furled Finger"),
        
        # LG Evergaols
        ERLocationData("LG/SE: Aspects of the Crucible: Tail - Stormhill Evergaol", "Aspects of the Crucible: Tail", boss=True),
        ERLocationData("LG/FHE: Bloodhound's Fang - Forlorn Hound Evergaol", "Bloodhound's Fang", boss=True),
        ERLocationData("LG/FHE: Somber Smithing Stone [1] - Blaidd reward Forlorn Hound Evergaol", "Somber Smithing Stone [1]", npc=True, missable=True),
        

        ERLocationData("LG/ME: Spiked Cracked Tear - Minor Erdtree", "Spiked Cracked Tear"),
        ERLocationData("LG/ME: Greenspill Crystal Tear - Minor Erdtree", "Greenspill Crystal Tear"),
    ],
    "Church of Elleh":[
        ERLocationData("LG/(CE): Smithing Stone [1] - on anvil", "Smithing Stone [1]"),
        ERLocationData("LG/(CE): Golden Rune [2] - out front", "Golden Rune [2]"),
        # Kalé shop
        ERLocationData("LG/(CE): Finger Snap - kill Kalé or Blaidd quest", "Finger Snap", npc=True), #just hear howl, talk to kale get finger, finger at howl, blaidd appear
        #ERLocationData("LG/(CE): Throwing Dagger - Kalé Shop", "Throwing Dagger", shop=True),
        ERLocationData("LG/(CE): Telescope - Kalé Shop", "Telescope", shop=True),
        ERLocationData("LG/(CE): Furlcalling Finger Remedy - Kalé Shop", "Furlcalling Finger Remedy", shop=True),
        ERLocationData("LG/(CE): Cracked Pot x3 - Kalé Shop", "Cracked Pot x3", shop=True),
        ERLocationData("LG/(CE): Crafting Kit - Kalé Shop", "Crafting Kit", shop=True),
        ERLocationData("LG/(CE): Nomadic Warrior's Cookbook [1] - Kalé Shop", "Nomadic Warrior's Cookbook [1]", shop=True),
        ERLocationData("LG/(CE): Nomadic Warrior's Cookbook [2] - Kalé Shop", "Nomadic Warrior's Cookbook [2]", shop=True),
        ERLocationData("LG/(CE): Missionary's Cookbook [1] - Kalé Shop", "Missionary's Cookbook [1]", shop=True),
        #ERLocationData("LG/(CE): Arrow - Kalé Shop", "Arrow", shop=True),
        #ERLocationData("LG/(CE): Bolt - Kalé Shop", "Bolt", shop=True),
        ERLocationData("LG/(CE): Torch - Kalé Shop", "Torch", shop=True),
        ERLocationData("LG/(CE): Large Leather Shield - Kalé Shop", "Large Leather Shield", shop=True),
        ERLocationData("LG/(CE): Chain Coif - Kalé Shop", "Chain Coif", shop=True),
        ERLocationData("LG/(CE): Chain Armor - Kalé Shop", "Chain Armor", shop=True),
        ERLocationData("LG/(CE): Gauntlets - Kalé Shop", "Gauntlets", shop=True),
        ERLocationData("LG/(CE): Chain Leggings - Kalé Shop", "Chain Leggings", shop=True),
        ERLocationData("LG/(CE): Note: Flask of Wondrous Physick - Kalé Shop", "Note: Flask of Wondrous Physick", shop=True),
        ERLocationData("LG/(CE): Note: Waypoint Ruins - Kalé Shop", "Note: Waypoint Ruins", shop=True),
        # Ranni
        ERLocationData("LG/(CE): Spirit Calling Bell - Ranni", "Spirit Calling Bell", prominent=True),
        ERLocationData("LG/(CE): Lone Wolf Ashes - Ranni", "Lone Wolf Ashes"),
    ],
    "Coastal Cave":[
        ERLocationData("LG/(CC): Land Octopus Ovary - before boss", "Land Octopus Ovary"),
        ERLocationData("LG/(CC): Sewing Needle - boss drop", "Sewing Needle", boss=True),
        ERLocationData("LG/(CC): Tailoring Tools - boss drop", "Tailoring Tools", boss=True),
        ERLocationData("LG/(CC): Smoldering Butterfly - after boss", "Smoldering Butterfly"),
    ],
    "Church of Dragon Communion":[
        ERLocationData("LG/(CDC): Great Dragonfly Head x4 - to W", "Great Dragonfly Head x4"),
        ERLocationData("LG/(CDC): Exalted Flesh - to S up high", "Exalted Flesh"),
        ERLocationData("LG/(CDC): Smithing Stone [2] - to S", "Smithing Stone [2]"),
        ERLocationData("LG/(CDC): Somber Smithing Stone [1] - scarab to S", "Somber Smithing Stone [1]", scarab=True),
        ERLocationData("LG/(CDC): Dragonfire - Dragon Communion", "Dragonfire", shop=True),
        ERLocationData("LG/(CDC): Dragonclaw - Dragon Communion", "Dragonclaw", shop=True),
        ERLocationData("LG/(CDC): Dragonmaw - Dragon Communion", "Dragonmaw", shop=True),
    ],
    "Groveside Cave":[
        ERLocationData("LG/(GC): Cracked Pot - first room", "Cracked Pot"),
        ERLocationData("LG/(GC): Glowstone x3 - first room", "Glowstone x3"),
        ERLocationData("LG/(GC): Golden Rune [1] - first room", "Golden Rune [1]"),
        ERLocationData("LG/(GC): Flamedrake Talisman - boss drop", "Flamedrake Talisman", boss=True),
    ],
    "Stormfoot Catacombs":[
        ERLocationData("LG/(SC): Root Resin x2 - first room", "Root Resin x2"),
        ERLocationData("LG/(SC): Prattling Pate \"Hello\" - behind first fire spitter", "Prattling Pate \"Hello\""),
        ERLocationData("LG/(SC): Smoldering Butterfly x3 - behind second fire spitter", "Smoldering Butterfly x3"),
        ERLocationData("LG/(SC): Wandering Noble Ashes - room at end of hall after latter", "Wandering Noble Ashes"),
        ERLocationData("LG/(SC): Noble Sorcerer Ashes - boss drop", "Noble Sorcerer Ashes"),
    ],
    "Gatefront Ruins":[
        ERLocationData("LG/(GR): Lordsworn's Greatsword - NW carriage", "Lordsworn's Greatsword"),
        ERLocationData("LG/(GR): Map: Limgrave, West - map pillar", "Map: Limgrave, West", prominent=True),
        ERLocationData("LG/(GR): Ruin Fragment x3 - S of NW carriage", "Ruin Fragment x3"),
        ERLocationData("LG/(GR): Flail - NE carriage", "Flail"),
        ERLocationData("LG/(GR): Ash of War: Storm Stomp - underground chest", "Ash of War: Storm Stomp"),
        ERLocationData("LG/(GR): Whetstone Knife - underground chest", "Whetstone Knife", prominent=True),
    ],
    "Limgrave Tunnels":[
        ERLocationData("LG/(LT): Golden Rune [4] - off side of entrance elevator", "Golden Rune [4]"),
        ERLocationData("LG/(LT): Smithing Stone [1] - room with rats", "Smithing Stone [1]"),
        ERLocationData("LG/(LT): Glintstone Scrap x3 - off side of second elevator", "Glintstone Scrap x3"),
        ERLocationData("LG/(LT): Large Glintstone Scrap x5 - room after second elevator", "Large Glintstone Scrap x5"),
        ERLocationData("LG/(LT): Golden Rune [1] - off side of third elevator", "Golden Rune [1]"),
        ERLocationData("LG/(LT): Roar Medallion - boss drop", "Roar Medallion", boss=True),
    ],
    "Stormgate":[
        ERLocationData("LG/(SG): Lump of Flesh - lower area", "Lump of Flesh"),
        ERLocationData("LG/(SG): Golden Rune [1] - lower area", "Golden Rune [1]"),
        ERLocationData("LG/(SG): Smoldering Butterfly x5 - on cliff above", "Smoldering Butterfly x5"),
        ERLocationData("LG/(SG): Arrow's Reach Talisman - chest above gate", "Arrow's Reach Talisman"),
        ERLocationData("LG/(SG): Golden Rune [2] - off side of ruin above", "Golden Rune [2]"),
    ],
    "Stormhill Shack":[
        ERLocationData("LG/(SS): Stonesword Key - near grace", "Stonesword Key"),
        ERLocationData("LG/(SS): Sitting Sideways - talk to Roderika", "Sitting Sideways", npc=True),
        ERLocationData("LG/(SS): Spirit Jellyfish Ashes - talk to Roderika 4 times", "Spirit Jellyfish Ashes", npc=True),
    ],
    "Waypoint Ruins":[
        ERLocationData("LG/(WR): Golden Rune [1] - within ruins", "Golden Rune [1]"),
        ERLocationData("LG/(WR): Immunizing Cured Meat - within ruins", "Immunizing Cured Meat"),
        ERLocationData("LG/(WR): Glowstone x2 - within ruins", "Glowstone x2"),
        ERLocationData("LG/(WR): Trina's Lily x4 - on ruin wall", "Trina's Lily x4"),
        # Sellen shop
        ERLocationData("LG/(WR): Nod In Thought - Sellen", "Nod In Thought"),
        ERLocationData("LG/(WR): Glintstone Pebble - Sellen Shop", "Glintstone Pebble", shop=True),
        ERLocationData("LG/(WR): Glintstone Stars - Sellen Shop", "Glintstone Stars", shop=True),
        ERLocationData("LG/(WR): Glintstone Arc - Sellen Shop", "Glintstone Arc", shop=True),
        ERLocationData("LG/(WR): Crystal Barrage - Sellen Shop", "Crystal Barrage", shop=True),
        ERLocationData("LG/(WR): Scholar's Armament - Sellen Shop", "Scholar's Armament", shop=True),
        ERLocationData("LG/(WR): Scholar's Shield - Sellen Shop", "Scholar's Shield", shop=True),

        # Sorcerer Scrolls
        ERLocationData("LG/(WR): Great Glintstone Shard - Academy Scroll", "Great Glintstone Shard", shop=True, conditional=True, missable=True),
        ERLocationData("LG/(WR): Swift Glintstone Shard - Academy Scroll", "Swift Glintstone Shard", shop=True, conditional=True, missable=True),
        ERLocationData("LG/(WR): Glintstone Cometshard - Conspectus Scroll", "Glintstone Cometshard", shop=True, conditional=True, missable=True),
        ERLocationData("LG/(WR): Star Shower - Conspectus Scroll", "Star Shower", shop=True, conditional=True, missable=True),
        ERLocationData("LG/(WR): Glintblade Phalanx - Royal House Scroll", "Glintblade Phalanx", shop=True, conditional=True, missable=True),
        ERLocationData("LG/(WR): Carian Slicer - Royal House Scroll", "Carian Slicer", shop=True, conditional=True, missable=True),
    ],
    "Dragon-Burnt Ruins":[
        ERLocationData("LG/(DBR): Crab Eggs - within ruins", "Crab Eggs"),
        ERLocationData("LG/(DBR): Stonesword Key - within ruined building", "Stonesword Key"),
        ERLocationData("LG/(DBR): Golden Rune [2] - within ruins", "Golden Rune [2]"),
        ERLocationData("LG/(DBR): Twinblade - underground chest hidden within ruin", "Twinblade", hidden=True),
    ],
    "Murkwater Cave":[
        ERLocationData("LG/(MCV): Mushroom x5 - chest at back", "Mushroom x5"),
        ERLocationData("LG/(MCV): Cloth Garb - Patches chest", "Cloth Garb"),
        ERLocationData("LG/(MCV): Cloth Trousers - Patches chest", "Cloth Trousers"),
        # patches
        ERLocationData("LG/(MCV): Golden Rune [1] x2 - spare or kill Patches", "Golden Rune [1] x2"),
        ERLocationData("LG/(MCV): Grovel For Mercy - spare Patches", "Grovel For Mercy", missable=True),

        ERLocationData("LG/(MCV): Spear +7 - kill Patches", "Spear", missable=True, npc=True),
        ERLocationData("LG/(MCV): Leather Armor - kill Patches", "Leather Armor", missable=True, npc=True),
        ERLocationData("LG/(MCV): Leather Gloves - kill Patches", "Leather Gloves", missable=True, npc=True),
        ERLocationData("LG/(MCV): Leather Boots - kill Patches", "Leather Boots", missable=True, npc=True),

        ERLocationData("LG/(MCV): Extreme Repentance - grovel emote Patches", "Extreme Repentance", missable=True),
        ERLocationData("LG/(MCV): Calm Down! - trapped chest", "Calm Down!", missable=True),

        ERLocationData("LG/(MCV): Gold-Pickled Fowl Foot x3 - Patches Shop", "Gold-Pickled Fowl Foot x3"),
        ERLocationData("LG/(MCV): Fan Daggers x20 - Patches Shop", "Fan Daggers x20"),
        ERLocationData("LG/(MCV): Margit's Shackle - Patches Shop", "Margit's Shackle"),
        ERLocationData("LG/(MCV): Grace Mimic x15 - Patches Shop", "Grace Mimic x15"),
        ERLocationData("LG/(MCV): Furlcalling Finger Remedy x3 - Patches Shop", "Furlcalling Finger Remedy x3"),
        ERLocationData("LG/(MCV): Festering Bloody Finger x5 - Patches Shop", "Festering Bloody Finger x5"),
        ERLocationData("LG/(MCV): Stonesword Key - Patches Shop", "Stonesword Key"),
        ERLocationData("LG/(MCV): Missionary's Cookbook [2] - Patches Shop", "Missionary's Cookbook [2]"),
        ERLocationData("LG/(MCV): Parrying Dagger - Patches Shop", "Parrying Dagger"),
        ERLocationData("LG/(MCV): Great Arrow x10 - Patches Shop", "Great Arrow x10"),
        ERLocationData("LG/(MCV): Ballista Bolt x5 - Patches Shop", "Ballista Bolt x5"),
        ERLocationData("LG/(MCV): Horse Crest Wooden Shield - Patches Shop", "Horse Crest Wooden Shield"),
        ERLocationData("LG/(MCV): Sacrificial Twig - Patches Shop", "Sacrificial Twig"),
    ],
    "Mistwood Ruins":[
        ERLocationData("LG/(MR): Smithing Stone [2] - chest in ruins", "Smithing Stone [2]"),
        ERLocationData("LG/(MR): Axe Talisman - chest underground", "Axe Talisman"),
        ERLocationData("LG/(MR): Golden Rune [2] - within ruins", "Golden Rune [2]"),
    ],
    "Fort Haight":[
        ERLocationData("LG/(FH): Bloodrose x3 - near entrance", "Bloodrose x3"),
        ERLocationData("LG/(FH): Nomadic Warrior's Cookbook [6] - ground floor room", "Nomadic Warrior's Cookbook [6]"),
        ERLocationData("LG/(FH): Ash of War: Bloody Slash - enemy drop upper area", "Ash of War: Bloody Slash", drop=True),
        ERLocationData("LG/(FH): Bloodrose x5 - upper area", "Bloodrose x5"),
        ERLocationData("LG/(FH): Smithing Stone [1] - catwalk right of tower", "Smithing Stone [1]"),
        ERLocationData("LG/(FH): Dectus Medallion (Left) - tower chest", "Dectus Medallion (Left)", prominent=True),
    ],
    "Third Church of Marika":[
        ERLocationData("LG/(TCM): Flask of Wondrous Physick - in basin", "Flask of Wondrous Physick", prominent=True),
        ERLocationData("LG/(TCM): Crimson Crystal Tear - in basin", "Crimson Crystal Tear"),
        ERLocationData("LG/(TCM): Sacred Tear - by statue", "Sacred Tear", prominent=True),
    ],
    "LG Artist's Shack":[
        ERLocationData("LG/(AS): \"Homing Instinct\" Painting - painting", "\"Homing Instinct\" Painting"),
        ERLocationData("LG/(AS): Smithing Stone [1] - on corpse", "Smithing Stone [1]"),
    ],
    "Summonwater Village":[
        ERLocationData("LG/(SWV): Mushroom x3 - within ruins", "Mushroom x3"),
        ERLocationData("LG/(SWV): Smithing Stone [1] - N side", "Smithing Stone [1]"),
        ERLocationData("LG/(SWV): Green Turtle Talisman - behind imp statue", "Green Turtle Talisman"), # 1
        ERLocationData("LG/(SWV): Deathroot - boss drop", "Deathroot", boss=True),
        ERLocationData("LG/(SWV): Skeletal Militiaman Ashes - boss drop", "Skeletal Militiaman Ashes", boss=True),
    ],
    "Murkwater Catacombs":[
        ERLocationData("LG/(MCC): Root Resin x5 - by lever", "Root Resin x5"),
        ERLocationData("LG/(MCC): Banished Knight Engvall - boss drop", "Banished Knight Engvall", boss=True),
    ],
    "Highroad Cave":[
        ERLocationData("LG/(HC): Golden Rune [1] - past second hole", "Golden Rune [1]"),
        ERLocationData("LG/(HC): Arteria Leaf x3 - on ledge before water area", "Arteria Leaf x3"),
        ERLocationData("LG/(HC): Fire Grease x2 - below ledge before water area", "Fire Grease x2"),
        ERLocationData("LG/(HC): Smithing Stone [1] x3 - below water entrance ledge", "Smithing Stone [1] x3"),
        ERLocationData("LG/(HC): Smithing Stone [2] - top of small waterfall area", "Smithing Stone [2]"),
        ERLocationData("LG/(HC): Golden Rune [4] - top of small waterfall area", "Golden Rune [4]"),
        ERLocationData("LG/(HC): Shamshir - center of water area", "Shamshir"),
        ERLocationData("LG/(HC): Furlcalling Finger Remedy - past miniboss on ledge", "Furlcalling Finger Remedy"),
        ERLocationData("LG/(HC): Blue Dancer Charm - boss drop", "Blue Dancer Charm", boss=True),
    ],
    "Deathtouched Catacombs":[
        ERLocationData("LG/(DC): Bloodrose x3 - by lever", "Bloodrose x3"),
        ERLocationData("LG/(DC): Uchigatana - down small tunnel on ledge", "Uchigatana"),
        ERLocationData("LG/(DC): Assassin's Crimson Dagger - boss drop", "Assassin's Crimson Dagger", boss=True),
        ERLocationData("LG/(DC): Deathroot - boss chest", "Deathroot", boss=True),
    ],
    "Warmaster's Shack":[
        ERLocationData("LG/(WS): Ash of War: Stamp (Upward Cut) - Bernahl shop", "Ash of War: Stamp (Upward Cut)", shop=True),
        ERLocationData("LG/(WS): Ash of War: Kick - Bernahl shop", "Ash of War: Kick", shop=True),
        ERLocationData("LG/(WS): Ash of War: Endure - Bernahl shop", "Ash of War: Endure", shop=True),
        ERLocationData("LG/(WS): Ash of War: War Cry - Bernahl shop", "Ash of War: War Cry", shop=True),
        ERLocationData("LG/(WS): Ash of War: Spinning Slash - Bernahl shop", "Ash of War: Spinning Slash", shop=True),
        ERLocationData("LG/(WS): Ash of War: Impaling Thrust - Bernahl shop", "Ash of War: Impaling Thrust", shop=True),
        ERLocationData("LG/(WS): Ash of War: Quickstep - Bernahl shop", "Ash of War: Quickstep", shop=True),
        ERLocationData("LG/(WS): Ash of War: Storm Blade - Bernahl shop", "Ash of War: Storm Blade", shop=True),
        ERLocationData("LG/(WS): Ash of War: Parry - Bernahl shop", "Ash of War: Parry", shop=True),
        ERLocationData("LG/(WS): Ash of War: No Skill - Bernahl shop", "Ash of War: No Skill", shop=True),
        # kill bernahl at WS or later in farum as invader
        ERLocationData("LG/(WS): Beast Champion Helm - kill Bernahl", "Beast Champion Helm", npc=True),
        ERLocationData("LG/(WS): Beast Champion Armor (Altered) - kill Bernahl", "Beast Champion Armor (Altered)", npc=True),
        ERLocationData("LG/(WS): Beast Champion Gauntlets - kill Bernahl", "Beast Champion Gauntlets", npc=True),
        ERLocationData("LG/(WS): Beast Champion Greaves - kill Bernahl", "Beast Champion Greaves", npc=True),
        ERLocationData("LG/(WS): Devourer's Scepter - kill Bernahl", "Devourer's Scepter", npc=True),

        ERLocationData("LG/(WS): Bone Peddler's Bell Bearing - night boss drop", "Bone Peddler's Bell Bearing", boss=True),
    ],

    # MARK: Roundtable Hold
    "Roundtable Hold":[
        ERLocationData("RH: Baldachin's Blessing - be held", "Baldachin's Blessing", npc=True),
        ERLocationData("RH: What Do You Want? - talk to Ensha", "What Do You Want?", npc=True, missable=True),
        ERLocationData("RH: Taunter's Tongue - invader drop", "Taunter's Tongue", hostile_npc=True), # idk if missable
        ERLocationData("RH: Cipher Pata - on bed in lower area", "Cipher Pata"),
        # behind ss key
        ERLocationData("RH: Crepus's Black-Key Crossbow - behind imp statue in chest", "Crepus's Black-Key Crossbow"),
        ERLocationData("RH: Black-Key Bolt x20 - behind imp statue in chest", "Black-Key Bolt x20"),
        ERLocationData("RH: Assassin's Prayerbook - behind second imp statue in chest", "Assassin's Prayerbook"), # 2 key chest
        # Corhyn
        ERLocationData("RH: Prayer - talk to Corhyn", "Prayer", npc=True),
        ERLocationData("RH: Urgent Heal - Corhyn shop", "Urgent Heal", shop=True),
        ERLocationData("RH: Heal - Corhyn shop", "Heal", shop=True),
        ERLocationData("RH: Cure Poison - Corhyn shop", "Cure Poison", shop=True),
        ERLocationData("RH: Magic Fortification - Corhyn shop", "Magic Fortification", shop=True),
        ERLocationData("RH: Flame Fortification - Corhyn shop", "Flame Fortification", shop=True),
        ERLocationData("RH: Rejection - Corhyn shop", "Rejection", shop=True),
        ERLocationData("RH: Catch Flame - Corhyn shop", "Catch Flame", shop=True),
        ERLocationData("RH: Flame Sling - Corhyn shop", "Flame Sling", shop=True),

        # Cleric books
        ERLocationData("RH: Lord's Heal - Two Fingers' Prayerbook", "Lord's Heal", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Lord's Aid - Two Fingers' Prayerbook", "Lord's Aid", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Assassin's Approach - Assassin's Prayerbook", "Assassin's Approach", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Darkness - Assassin's Prayerbook", "Darkness", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Radagon's Rings of Light - Golden Order Principia", "Radagon's Rings of Light", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Law of Regression - Golden Order Principia", "Law of Regression", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Lightning Spear - Dragon Cult Prayerbook", "Lightning Spear", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Honed Bolt - Dragon Cult Prayerbook", "Honed Bolt", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Electrify Armament - Dragon Cult Prayerbook", "Electrify Armament", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Ancient Dragons' Lightning Spear - Ancient Dragon Prayerbook", "Ancient Dragons' Lightning Spear", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Ancient Dragons' Lightning Strike - Ancient Dragon Prayerbook", "Ancient Dragons' Lightning Strike", shop=True, conditional=True, missable=True),
        ERLocationData("RH: O, Flame! - Fire Monks' Prayerbook", "O, Flame!", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Surge, O Flame! - Fire Monks' Prayerbook", "Surge, O Flame!", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Giantsflame Take Thee - Giant's Prayerbook", "Giantsflame Take Thee", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Flame, Fall Upon Them - Giant's Prayerbook", "Flame, Fall Upon Them", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Black Flame - Godskin Prayerbook", "Black Flame", shop=True, conditional=True, missable=True),
        ERLocationData("RH: Black Flame Blade - Godskin Prayerbook", "Black Flame Blade", shop=True, conditional=True, missable=True),

        # Twin maiden husks
        ERLocationData("RH: Rune Arc x5 - Twin maiden shop", "Rune Arc x5", shop=True),
        ERLocationData("RH: White Cipher Ring - Twin maiden shop", "White Cipher Ring", shop=True),
        ERLocationData("RH: Blue Cipher Ring - Twin maiden shop", "Blue Cipher Ring", shop=True),
        ERLocationData("RH: Memory Stone - Twin maiden shop", "Memory Stone", shop=True, prominent=True),
        ERLocationData("RH: Stonesword Key x3 - Twin maiden shop", "Stonesword Key x3", shop=True),
        ERLocationData("RH: Dagger - Twin maiden shop", "Dagger", shop=True),
        ERLocationData("RH: Longsword - Twin maiden shop", "Longsword", shop=True),
        ERLocationData("RH: Rapier - Twin maiden shop", "Rapier", shop=True),
        ERLocationData("RH: Scimitar - Twin maiden shop", "Scimitar", shop=True),
        ERLocationData("RH: Battle Axe - Twin maiden shop", "Battle Axe", shop=True),
        ERLocationData("RH: Mace - Twin maiden shop", "Mace", shop=True),
        ERLocationData("RH: Short Spear - Twin maiden shop", "Short Spear", shop=True),
        ERLocationData("RH: Longbow - Twin maiden shop", "Longbow", shop=True),
        ERLocationData("RH: Finger Seal - Twin maiden shop", "Finger Seal", shop=True),
        ERLocationData("RH: Heater Shield - Twin maiden shop", "Heater Shield", shop=True),
        ERLocationData("RH: Knight Helm - Twin maiden shop", "Knight Helm", shop=True),
        ERLocationData("RH: Knight Armor - Twin maiden shop", "Knight Armor", shop=True),
        ERLocationData("RH: Knight Gauntlets - Twin maiden shop", "Knight Gauntlets", shop=True),
        ERLocationData("RH: Knight Greaves - Twin maiden shop", "Knight Greaves", shop=True),
        ERLocationData("RH: Furled Finger's Trick-Mirror - Twin maiden shop", "Furled Finger's Trick-Mirror", shop=True),
        ERLocationData("RH: Host's Trick-Mirror - Twin maiden shop", "Host's Trick-Mirror", shop=True),
        
        # D
        ERLocationData("RH: Litany of Proper Death - D shop", "Litany of Proper Death", shop=True, missable=True), 
        ERLocationData("RH: Order's Blade - D shop", "Order's Blade", shop=True, missable=True), # i think D can me missed
    ],

    "Bridge of Sacrifice":[
        ERLocationData("BS: Smithing Stone [1] x3 - corpse hanging off edge", "Smithing Stone [1] x3"),
        ERLocationData("BS: Stonesword Key - behind wooden platform", "Stonesword Key"),
    ],
    # MARK: Weeping Peninsula
    "Weeping Peninsula":[ # World Locations
        ERLocationData("WP/BS: Irina's Letter - talk to Irina to SE", "Irina's Letter", npc=True, missable=True),
        ERLocationData("WP/OR: Starlight Shards - E of OR", "Starlight Shards"),
        ERLocationData("WP/BCPG: Stonesword Key - head far N", "Stonesword Key"),
        ERLocationData("WP/CP: Bewitching Branch x3 - lower cliff NW of CP", "Bewitching Branch x3"),
        ERLocationData("WP/CP: Sliver of Meat - lower cliff NW of CP", "Sliver of Meat"),
        ERLocationData("WP/EC: Rainbow Stone - SE of EC", "Rainbow Stone"),
        ERLocationData("WP/SLT: Rainbow Stone x5 - to SE", "Rainbow Stone x5"),
        ERLocationData("WP/MT: Golden Rune [2] - N of MT under bridge", "Golden Rune [2]"),
        
        ERLocationData("WP/(FCM): Sacred Tear - by statue", "Sacred Tear", prominent=True),
        
        # Ailing Village
        ERLocationData("WP/AV: Yellow Ember - on way to AV, W of AV", "Yellow Ember"),
        ERLocationData("WP/AV: Golden Rune [2] - on way to AV, SW of AV", "Golden Rune [2]"),
        ERLocationData("WP/(AV): Flame Crest Wooden Shield - in house", "Flame Crest Wooden Shield"),
        ERLocationData("WP/(CBC): The Flame of Frenzy - on corpse", "The Flame of Frenzy"),
        ERLocationData("WP/(CBC): Sacred Tear - by statue", "Sacred Tear", prominent=True),
        
        # Near DHFR
        ERLocationData("WP/DHFR: String x5 - SE of DHFR", "String x5"),
        ERLocationData("WP/DHFR: Gold-Tinged Excrement x2 - SE of DHFR", "Gold-Tinged Excrement x2"),
        ERLocationData("WP/DHFR: Faith-knot Crystal Tear - N of DHFR", "Faith-knot Crystal Tear"),
        ERLocationData("WP/(DHFR): Shield of the Guilty - underground within S ruins", "Shield of the Guilty"),
        ERLocationData("WP/(DHFR): Arteria Leaf x2 - within N ruins", "Arteria Leaf x2"),
        ERLocationData("WP/(DHFR): Demi-Human Queen's Staff - enemy drop", "Demi-Human Queen's Staff", drop=True),
        ERLocationData("WP/(DHFR): Crystal Burst - enemy drop", "Crystal Burst", drop=True),
        
        # Near WR
        ERLocationData("WP/WR: Golden Rune [1] - W of WR on beach", "Golden Rune [1]"),
        ERLocationData("WP/WR: Golden Rune [5] - W of WR on beach", "Golden Rune [5]"),
        ERLocationData("WP/(WR): Ambush Shard - underground", "Ambush Shard"),
        ERLocationData("WP/(WR): Great Dragonfly Head - within ruins", "Great Dragonfly Head"),
        
        # Near TwR
        ERLocationData("WP/TwR: Divine Fortification - scarab SW of TwR, high on ruin", "Divine Fortification", scarab=True),
        ERLocationData("WP/TwR: Golden Rune [2] - on beach NW of TwR", "Golden Rune [2]"),
        ERLocationData("WP/(TwR): Beast Liver - within ruins", "Beast Liver"),
        ERLocationData("WP/(TwR): Winged Scythe - underground", "Winged Scythe"),
        
        # Near FLT
        ERLocationData("WP/FLT: Golden Rune [1] x3 1 - E of FLT", "Golden Rune [1] x3"),
        ERLocationData("WP/FLT: Golden Rune [1] x3 2 - E of FLT", "Golden Rune [1] x3"),
        ERLocationData("WP/(FLT): Hand Ballista - atop tower in chest", "Hand Ballista"),
        ERLocationData("WP/(FLT): Ballista Bolt x5 - atop tower in chest", "Ballista Bolt x5"),
        
        # Near ToR
        ERLocationData("WP/ToR: Golden Rune [1] 1 - graveyard W of ToR", "Golden Rune [1]"),
        ERLocationData("WP/ToR: Golden Rune [1] 2 - graveyard W of ToR", "Golden Rune [1]"),
        ERLocationData("WP/ToR: Golden Rune [1] 3 - graveyard W of ToR", "Golden Rune [1]"),
        ERLocationData("WP/ToR: Golden Rune [1] 4 - graveyard W of ToR", "Golden Rune [1]"),
        ERLocationData("WP/ToR: Golden Rune [2] - graveyard W of ToR", "Golden Rune [2]"),
        ERLocationData("WP/ToR: Golden Rune [3] - graveyard W of ToR", "Golden Rune [3]"),
        ERLocationData("WP/ToR: Great Dragonfly Head x3 - NE of ToR", "Great Dragonfly Head x3"),
        ERLocationData("WP/ToR: Mushroom x4 - E of ToR", "Mushroom x4"),
        
        # Near CMR grace
        ERLocationData("WP/CMR: Map: Weeping Peninsula - to SW", "Map: Weeping Peninsula", prominent=True),
        ERLocationData("WP/CMR: Nightrider Flail - night boss drop to SW", "Nightrider Flail", boss=True),
        ERLocationData("WP/CMR: Ash of War: Barricade Shield - night boss drop to SW", "Ash of War: Barricade Shield", boss=True),
        ERLocationData("WP/CMR: Great Turtle Shell - top of tower to SE", "Great Turtle Shell"),
        ERLocationData("WP/CMR: Warming Stone x2 - top of tower to SE", "Warming Stone x2"),
        ERLocationData("WP/CMR: Smithing Stone [1] - other side of wall to S, long go around", "Smithing Stone [1]"),
        ERLocationData("WP/CMR: Sacrificial Axe - night boss to SW", "Sacrificial Axe", boss=True),
        # North of CMR grace
        ERLocationData("WP/CMR: Ash of War: Mighty Shot - scarab to N", "Ash of War: Mighty Shot", scarab=True),
        ERLocationData("WP/CMR: Smithing Stone [2] - to N", "Smithing Stone [2]"),
        ERLocationData("WP/CMR: Golden Rune [2] - to N", "Golden Rune [2]"),
        ERLocationData("WP/CMR: Strip of White Flesh - to N", "Strip of White Flesh"),
        ERLocationData("WP/CMR: Morning Star - in carriage to N", "Morning Star"),
        # Shop
        ERLocationData("WP/CMR: Smithing Stone [1] x3 - Nomadic Merchant to SE", "Smithing Stone [1] x3",shop=True),
        ERLocationData("WP/CMR: Smithing Stone [2] - Nomadic Merchant to SE", "Smithing Stone [2]",shop=True),
        ERLocationData("WP/CMR: Cracked Pot - Nomadic Merchant to SE", "Cracked Pot",shop=True),
        ERLocationData("WP/CMR: Stonesword Key - Nomadic Merchant to SE", "Stonesword Key",shop=True),
        ERLocationData("WP/CMR: Bastard Sword - Nomadic Merchant to SE", "Bastard Sword",shop=True),
        ERLocationData("WP/CMR: Light Crossbow - Nomadic Merchant to SE", "Light Crossbow",shop=True),
        ERLocationData("WP/CMR: Great Arrow x8 - Nomadic Merchant to SE", "Great Arrow x8",shop=True),
        ERLocationData("WP/CMR: Ballista Bolt x8 - Nomadic Merchant to SE", "Ballista Bolt x8",shop=True),
        ERLocationData("WP/CMR: Red Thorn Roundshield - Nomadic Merchant to SE", "Red Thorn Roundshield",shop=True),
        ERLocationData("WP/CMR: Round Shield - Nomadic Merchant to SE", "Round Shield",shop=True),
        ERLocationData("WP/CMR: Iron Helmet - Nomadic Merchant to SE", "Iron Helmet",shop=True),
        ERLocationData("WP/CMR: Scale Armor - Nomadic Merchant to SE", "Scale Armor",shop=True),
        ERLocationData("WP/CMR: Iron Gauntlets - Nomadic Merchant to SE", "Iron Gauntlets",shop=True),
        ERLocationData("WP/CMR: Leather Trousers - Nomadic Merchant to SE", "Leather Trousers",shop=True),
        ERLocationData("WP/CMR: Crimson Amber Medallion - Nomadic Merchant to SE", "Crimson Amber Medallion",shop=True),
        ERLocationData("WP/CMR: Note: Demi-human Mobs - Nomadic Merchant to SE", "Note: Demi-human Mobs",shop=True),
        
        
        #Near Castle Morne
        ERLocationData("WP/CM: Golden Rune [1] - NW of CM", "Golden Rune [1]"),
        ERLocationData("WP/CM: Somber Smithing Stone [2] - E of CM", "Somber Smithing Stone [2]"),
        ERLocationData("WP/CM: Arteria Leaf - E of CM", "Arteria Leaf"),
        ERLocationData("WP/CM: Golden Rune [4] - NE of CM in swamp", "Golden Rune [4]"),
        ERLocationData("WP/CM: Golden Seed - golden tree N of CM", "Golden Seed", prominent=True),
        ERLocationData("WP/CM: Poison Mist - scarab NE of CM, N of swamp", "Poison Mist", scarab=True),
        
        # da tree
        ERLocationData("WP/ME: Crimsonburst Crystal Tear - boss drop", "Crimsonburst Crystal Tear", boss=True),
        ERLocationData("WP/ME: Opaline Bubbletear - boss drop", "Opaline Bubbletear", boss=True),
        ERLocationData("WP/ME: Eclipse Crest Heater Shield - W of ME, drop off 2 ledges", "Eclipse Crest Heater Shield", hidden=True),
        ERLocationData("WP/ME: Golden Rune [6] - enemy drop S of ME", "Golden Rune [6]", drop=True),
        ERLocationData("WP/ME: Sliver of Meat - S of ME", "Sliver of Meat"),
        ERLocationData("WP/ME: Lightning Strike - scarab E of ME, drop down gravestones", "Lightning Strike", scarab=True),
        
        # Rises
        ERLocationData("WP/(OR): Memory Stone - find the 3 spirits", "Memory Stone", rise_puzzle=True),
        # Evergaol
        ERLocationData("WP/WE: Radagon's Scarseal - boss drop Weeping Evergaol", "Radagon's Scarseal", boss=True), # 1
    ],
    "Impaler's Catacombs":[
        ERLocationData("WP/(IC): Prattling Pate \"Please help\" - start of sewer area", "Prattling Pate \"Please help\""),
        ERLocationData("WP/(IC): Root Resin x3 - back SW of sewer area", "Root Resin x3"),
        ERLocationData("WP/(IC): Demi-Human Ashes - boss drop", "Demi-Human Ashes", boss=True),
    ],
    "Church of Pilgrimage":[
        ERLocationData("WP/(CP): Sacred Tear - in front of statue", "Sacred Tear", prominent=True),
        ERLocationData("WP/(CP): Gilded Iron Shield - in graveyard", "Gilded Iron Shield"),
        ERLocationData("WP/(CP): Blood Grease x2 - in graveyard", "Blood Grease x2"),
    ],
    "Tombsward Catacombs":[
        ERLocationData("WP/(TCC): Nomadic Warrior's Cookbook [9] - behind imp statue", "Nomadic Warrior's Cookbook [9]"), # 1
        ERLocationData("WP/(TCC): Human Bone Shard x5 - in path of fire spitter", "Human Bone Shard x5"),
        ERLocationData("WP/(TCC): Prattling Pate \"Thank you\" - room past fire spitter", "Prattling Pate \"Thank you\""),
        ERLocationData("WP/(TCC): Golden Rune [2] - above fire spitter", "Golden Rune [2]"),
        ERLocationData("WP/(TCC): Lhutel the Headless - boss drop", "Lhutel the Headless", boss=True),
    ],
    "Tombsward Cave":[
        ERLocationData("WP/(TCV): Golden Rune [2] - before big room", "Golden Rune [2]"),
        ERLocationData("WP/(TCV): Immunizing White Cured Meat - item 1 right of big room", "Immunizing White Cured Meat"),
        ERLocationData("WP/(TCV): Nomadic Warrior's Cookbook [8] - item 2 right of big room", "Nomadic Warrior's Cookbook [8]"),
        ERLocationData("WP/(TCV): Arteria Leaf - right of big room, then return path", "Arteria Leaf"),
        ERLocationData("WP/(TCV): Furlcalling Finger Remedy - big room", "Furlcalling Finger Remedy"),
        ERLocationData("WP/(TCV): Poisonbone Dart x6 - room after big room", "Poisonbone Dart x6"),
        ERLocationData("WP/(TCV): Viridian Amber Medallion - boss drop", "Viridian Amber Medallion", boss=True),
    ],
    "Isolated Merchant's Shack":[
        ERLocationData("WP/(IMS): Lantern - Isolated Merchant shop", "Lantern", shop=True),
        ERLocationData("WP/(IMS): Festering Bloody Finger x5 - Isolated Merchant shop", "Festering Bloody Finger x5", shop=True),
        ERLocationData("WP/(IMS): Arteria Leaf x5 - Isolated Merchant shop", "Arteria Leaf x5", shop=True),
        ERLocationData("WP/(IMS): Smithing Stone [2] x3 - Isolated Merchant shop", "Smithing Stone [2] x3", shop=True),
        ERLocationData("WP/(IMS): Stonesword Key x3 - Isolated Merchant shop", "Stonesword Key x3", shop=True),
        ERLocationData("WP/(IMS): Lost Ashes of War - Isolated Merchant shop", "Lost Ashes of War", shop=True),
        ERLocationData("WP/(IMS): Zweihander - Isolated Merchant shop", "Zweihander", shop=True),
        ERLocationData("WP/(IMS): Great Arrow x15 - Isolated Merchant shop", "Great Arrow x15", shop=True),
        ERLocationData("WP/(IMS): Ballista Bolt x15 - Isolated Merchant shop", "Ballista Bolt x15", shop=True),
        ERLocationData("WP/(IMS): Sacrificial Twig x3 - Isolated Merchant shop", "Sacrificial Twig x3", shop=True),
        ERLocationData("WP/(IMS): Note: Wandering Mausoleum - Isolated Merchant shop", "Note: Wandering Mausoleum", shop=True),
    ],
    "Morne Tunnel":[
        ERLocationData("WP/(MT): Arteria Leaf x2 - lower first room", "Arteria Leaf x2"),
        ERLocationData("WP/(MT): Soft Cotton - lower first room to W", "Soft Cotton"),
        ERLocationData("WP/(MT): Golden Rune [2] - second room, on wooden platform", "Golden Rune [2]"),
        ERLocationData("WP/(MT): Stanching Boluses - lower second room under platform", "Stanching Boluses"),
        ERLocationData("WP/(MT): Golden Rune [4] - third room in hut", "Golden Rune [4]"),
        ERLocationData("WP/(MT): Exalted Flesh - third room chest", "Exalted Flesh"),
        ERLocationData("WP/(MT): Large Glintstone Scrap x2 - third room W of hut", "Large Glintstone Scrap x2"),
        ERLocationData("WP/(MT): Rusted Anchor - boss drop", "Rusted Anchor", boss=True),
    ],
    "Earthbore Cave":[
        ERLocationData("WP/(EC): Pickled Turtle Neck x3 - entrance chest", "Pickled Turtle Neck x3"),
        ERLocationData("WP/(EC): Golden Rune [1] - right path from entrance chest", "Golden Rune [1]"),
        ERLocationData("WP/(EC): Glowstone x5 - past skylight", "Glowstone x5"),
        ERLocationData("WP/(EC): Kukri x8 - past skylight", "Kukri x8"),
        ERLocationData("WP/(EC): Smoldering Butterfly x5 - in boss room", "Smoldering Butterfly x5"),
        ERLocationData("WP/(EC): Trina's Lily - in boss room", "Trina's Lily"),
        ERLocationData("WP/(EC): Spelldrake Talisman - boss drop", "Spelldrake Talisman", boss=True),
    ],
    "Castle Morne":[
        ERLocationData("WP/(CM): Smithing Stone [2] - left up stairs from entrance", "Smithing Stone [2]"),
        ERLocationData("WP/(CM): Fire Grease x2 - on pile of corpses", "Fire Grease x2"),
        ERLocationData("WP/(CM): Smithing Stone [1] x3 - S of corpse pile in corner", "Smithing Stone [1] x3"),
        ERLocationData("WP/(CM): Claymore - chest NW of corpse pile in room", "Claymore"),
        ERLocationData("WP/(CM): Furlcalling Finger Remedy - NW roof area, SE from ladder", "Furlcalling Finger Remedy"),
        ERLocationData("WP/(CM): Steel-Wire Torch - NW roof area, end of NE corridor", "Steel-Wire Torch"),
        ERLocationData("WP/(CM): Golden Rune [2] - SW roof area, corpse hanging from bridge", "Golden Rune [2]"),
        ERLocationData("WP/(CM): Smithing Stone [2] x2 - SW roof area, down ladder to SW, far end to NW", "Smithing Stone [2] x2"),
        ERLocationData("WP/(CM): Golden Rune [2] - middle of SE roof area", "Golden Rune [2]"),
        # after BC
        ERLocationData("WP/(CM): Stonesword Key - after BC, off SW side of first building", "Stonesword Key"),
        ERLocationData("WP/(CM): Pickled Turtle Neck - after BC, drop through grate", "Pickled Turtle Neck"),
        ERLocationData("WP/(CM): Twinblade Talisman - after BC, chest top of W tower", "Twinblade Talisman"),
        ERLocationData("WP/(CM): Tarnished Golden Sunflower x3 - after BC, drop to hexagonal building, beside broken tree", "Tarnished Golden Sunflower x3"),
        ERLocationData("WP/(CM): Smithing Stone [2] - after BC, on wooden beam", "Smithing Stone [2]"),
        ERLocationData("WP/(CM): Whip - after BC, room after wooden beam drops", "Whip"),
        # after BRG
        ERLocationData("WP/(CM): Fire Arrow x15 - after BRG, N beach corner", "Fire Arrow x15"),
        ERLocationData("WP/(CM): Throwing Dagger x8 - after BRG, across bridge", "Throwing Dagger x8"),
        ERLocationData("WP/(CM): Somber Smithing Stone [1] - after BRG, behind SW tower on beach", "Somber Smithing Stone [1]"),
        ERLocationData("WP/(CM): Grafted Blade Greatsword - boss drop", "Grafted Blade Greatsword", boss=True),
        
        # Edgar
        ERLocationData("WP/(CM): Sacrificial Twig - talk to Edgar", "Sacrificial Twig", npc=True, missable=True),
        # kill and invader form needed + quest stuff
    ],
    
    # ERLocationData(":  - ", ""),
    # MARK: Liurnia of The Lakes
    "Liurnia of The Lakes":[],

    "Chapel of Anticipation [Return]":[
        ERLocationData("CA Return: The Stormhawk King - top of church", "The Stormhawk King"),
        ERLocationData("CA Return: Stormhawk Deenh - chest top of church", "Stormhawk Deenh"),
    ],

    # "":[],
    # ERLocationData(":  - ", ""),
    # MARK: Caelid
    "Caelid":[
        ERLocationData("CL/:  - ", ""),
        
        # Near ASS grace :)
        ERLocationData("CL/ASS: Ash of War: Poisonous Mist - scarab to SE", "Ash of War: Poisonous Mist", scarab=True),
        
        # Near SSR
        ERLocationData("CL/SSR: Sacramental Bud - NW of SSR up roots", "Sacramental Bud"),
        
        # near FGN grace
        ERLocationData("CL/FGN: Fire Blossom x3 - enemy drop to E", "Fire Blossom x3", drop=True),
        ERLocationData("CL/FGN: Smoldering Butterfly x5 - enemy drop to E", "Smoldering Butterfly x5", drop=True),
        ERLocationData("CL/FGN: Ash of War: Flame of the Redmanes - scarab to NE", "Ash of War: Flame of the Redmanes", scarab=True),
        ERLocationData("CL/FGN: Explosive Greatbolt x5 - to S in camp", "Explosive Greatbolt x5"),
        
        # near ACHN grace
        ERLocationData("CL/ACHN: Ash of War: Lifesteal Fist - scarab to N", "Ash of War: Lifesteal Fist", scarab=True),
        # shop, bro has 6 inf restock items lol
        ERLocationData("CL/ACHN: Preserving Boluses x3 - Nomadic Merchant shop to E", "Preserving Boluses x3", shop=True),
        ERLocationData("CL/ACHN: Aeonian Butterfly x5 - Nomadic Merchant shop to E", "Aeonian Butterfly x5", shop=True),
        
        # near CWR
        ERLocationData("CL/CWR: Poisonbloom x4 - S of CWR", "Poisonbloom x4"),
        
        # near CHS grace
        ERLocationData("CL/CHS: Dragon Heart - boss drop to SE", "Dragon Heart", boss=True),
        ERLocationData("CL/CHS: Golden Rune [3] - to E", "Golden Rune [3]"),
        ERLocationData("CL/CHS: Golden Rune [4] - on top of mound to SE", "Golden Rune [4]"),
        ERLocationData("CL/CHS: Starlight Shards - to W", "Starlight Shards"),
        ERLocationData("CL/CHS: Golden Rune [1] 1 - graveyard to S", "Golden Rune [1]"),
        ERLocationData("CL/CHS: Golden Rune [1] 2 - graveyard to S", "Golden Rune [1]"),
        ERLocationData("CL/CHS: Golden Rune [2] - graveyard to S", "Golden Rune [2]"),
        ERLocationData("CL/CHS: Golden Rune [5] - graveyard to S", "Golden Rune [5]"),
        ERLocationData("CL/CHS: Larval Tear - enemy drop in graveyard to S", "Larval Tear", drop=True),
        
        # near CC
        ERLocationData("CL/CC: Somber Smithing Stone [4] - scarab E of CC", "Somber Smithing Stone [4]", scarab=True),
        
        # near IG grace
        ERLocationData("CL/IG: Mushroom x6 - in tent to N", "Mushroom x6"),
        ERLocationData("CL/IG: Arrow's Sting Talisman - chest top of tower", "Arrow's Sting Talisman"),
        ERLocationData("CL/IG: Smoldering Butterfly x3 - to NW", "Smoldering Butterfly x3"),
        ERLocationData("CL/IG: Ash of War: Cragblade - scarab to W", "Ash of War: Cragblade", scarab=True),
        
        # near SASB grace
        ERLocationData("CL/SASB: Somber Smithing Stone [4] - enemy drop to SE", "Somber Smithing Stone [4]", drop=True),
        ERLocationData("CL/SASB: Beast Blood - enemy drop to SE", "Beast Blood", drop=True),
        ERLocationData("CL/SASB: Old Fang x2 - enemy drop to SE", "Old Fang x2", drop=True),
        ERLocationData("CL/SASB: Beast Blood x3 - to SE", "Beast Blood x3"),
        ERLocationData("CL/SASB: Beast Blood x2 - to SE", "Beast Blood x2"),
        ERLocationData("CL/SASB: Fan Daggers x6 - to S", "Fan Daggers x6"),
        ERLocationData("CL/SASB: Golden Seed - golden tree to S", "Golden Seed", prominent=True),
        ERLocationData("CL/SASB: Windy Crystal Tear - to S", "Windy Crystal Tear"),
        ERLocationData("CL/SASB: Crab Eggs x4 - to W", "Crab Eggs x4"),
        ERLocationData("CL/SASB: Rune Arc - chairs to NW", "Rune Arc"),
        ERLocationData("CL/SASB: Sacramental Bud x2 - chairs to NW", "Sacramental Bud x2"),
        ERLocationData("CL/SASB: Smithing Stone [4] x3 - chairs to NW", "Smithing Stone [4] x3"),
        ERLocationData("CL/SASB: Map: Caelid - to SW", "Map: Caelid"),
        ERLocationData("CL/SASB: Ash of War: Poison Moth Flight - night boss drop to SW", "Ash of War: Poison Moth Flight", boss=True),
        ERLocationData("CL/SASB: Death's Poker - night boss drop to SE", "Death's Poker", boss=True),
        ERLocationData("CL/SASB: Cracked Pot - Nomadic Merchant to SW", "Cracked Pot", shop=True),
        ERLocationData("CL/SASB: Stonesword Key - Nomadic Merchant to SW", "Stonesword Key", shop=True),
        ERLocationData("CL/SASB: Nomadic Warrior's Cookbook [15] - Nomadic Merchant to SW", "Nomadic Warrior's Cookbook [15]", shop=True),
        ERLocationData("CL/SASB: Champion Headband - Nomadic Merchant to SW", "Champion Headband", shop=True),
        ERLocationData("CL/SASB: Greathelm - Nomadic Merchant to SW", "Greathelm", shop=True),
        ERLocationData("CL/SASB: Champion Pauldron - Nomadic Merchant to SW", "Champion Pauldron", shop=True),
        ERLocationData("CL/SASB: Champion Bracers - Nomadic Merchant to SW", "Champion Bracers", shop=True),
        ERLocationData("CL/SASB: Champion Gaiters - Nomadic Merchant to SW", "Champion Gaiters", shop=True),
        ERLocationData("CL/SASB: Note: Gravity's Advantage - Nomadic Merchant to SW", "Note: Gravity's Advantage", shop=True),
        
        # slt
        ERLocationData("CL/SLT: Eternal Darkness - in cage", "Eternal Darkness"),
        
        # near SG
        ERLocationData("CL/SG: Glass Shard x5 - S of SG", "Glass Shard x5"),
        ERLocationData("CL/SG: Golden Rune [5] - S of SG", "Golden Rune [5]"),
        ERLocationData("CL/SG: Golden Rune [2] - S of SG", "Golden Rune [2]"),
        ERLocationData("CL/(SG): Black-Key Bolt x20 - upper part", "Black-Key Bolt x20"),
        ERLocationData("CL/(SG): Golden Rune [4] - upper part", "Golden Rune [4]"),
        
        # church of the plague
        ERLocationData("CL/CP: Golden Rune [9] - enemy drop SW of CP, near branch 1", "Golden Rune [9]", drop=True),
        ERLocationData("CL/CP: Golden Rune [9] - enemy drop SW of CP, near branch 2", "Golden Rune [9]", drop=True),
        ERLocationData("CL/CP: Golden Rune [9] - enemy drop SW of CP, near broken pillars 1", "Golden Rune [9]", drop=True),
        ERLocationData("CL/CP: Golden Rune [9] - enemy drop SW of CP, near broken pillars 2", "Golden Rune [9]", drop=True),
        ERLocationData("CL/CP: Golden Rune [9] - enemy drop SW of CP, near broken pillars 3", "Golden Rune [9]", drop=True),
        ERLocationData("CL/CP: Golden Rune [5] - far S of CP on pillar", "Golden Rune [5]"),
        ERLocationData("CL/CP: Drawstring Poison Grease x3 - S of CP", "Drawstring Poison Grease x3"),
        ERLocationData("CL/CP: Starlight Shards - E of CP", "Starlight Shards"),
        ERLocationData("CL/(CP): Sacred Tear - by statue", "Sacred Tear", prominent=True),
        
        # outside sh
        ERLocationData("CL/SH: Beast Blood x2 - S of SH", "Beast Blood x2"),
        
        # near FF
        ERLocationData("CL/FF: Golden Rune [9] - enemy drop SE of FF", "Golden Rune [9]", drop=True),
        ERLocationData("CL/FF: Dragon Heart x5 - enemy drop W of FF", "Dragon Heart x5", drop=True),
        ERLocationData("CL/FF: Smithing Stone [7] 1 - on skull SW of FF", "Smithing Stone [7]"),
        ERLocationData("CL/FF: Smithing Stone [7] 2 - on skull SW of FF", "Smithing Stone [7]"),
        ERLocationData("CL/FF: Stonesword Key - on skull SW of FF", "Stonesword Key"),
        ERLocationData("CL/FF: Smithing Stone [8] - on skull SW of FF", "Smithing Stone [8]"),
        
        # minor erdtree
        ERLocationData("CL/ME: Opaline Hardtear - boss drop", "Opaline Hardtear", boss=True),
        ERLocationData("CL/ME: Stonebarb Cracked Tear - boss drop", "Stonebarb Cracked Tear", boss=True),
        ERLocationData("CL/ME: Rune Arc - down hidden cliff E of ME", "Rune Arc", hidden=True),
        
        # LR
        ERLocationData("CL/LR: Golden Rune [1] - graveyard SW of LR", "Golden Rune [1]"),
        ERLocationData("CL/LR: Golden Rune [3] - graveyard SW of LR", "Golden Rune [3]"),
        ERLocationData("CL/LR: Golden Rune [6] - graveyard SW of LR", "Golden Rune [6]"),
        ERLocationData("CL/LR: Golden Rune [8] - graveyard SW of LR", "Golden Rune [8]"),
        ERLocationData("CL/LR: Ash of War: Bloodhound's Step - night boss drop N of LR", "Ash of War: Bloodhound's Step", boss=True),
        ERLocationData("CL/LR: Bestial Constitution - scarab W of LR", "Bestial Constitution", scarab=True),
        ERLocationData("CL/(LR): Memory Stone - chest top of tower", "Memory Stone", rise_puzzle=True),
        
        # near FG grace
        ERLocationData("CL/FG: Somber Smithing Stone [9] - scarab to W", "Somber Smithing Stone [9]", scarab=True),
        ERLocationData("CL/FG: Starlight Shards - to NE", "Starlight Shards"),
        ERLocationData("CL/FG: Dragon Heart - boss drop to S", "Dragon Heart", boss=True),
        
        # near BS
        ERLocationData("CL/BS: Gargoyle's Blackblade - boss drop SE of BS", "Gargoyle's Blackblade", boss=True),
        ERLocationData("CL/BS: Gargoyle's Black Halberd - boss drop SE of BS", "Gargoyle's Black Halberd", boss=True),
        ERLocationData("CL/BS: Golden Seed - golden tree SE of BS", "Golden Seed", prominent=True),
        ERLocationData("CL/BS: Soft Cotton x3 - down cliff NW of BS, second layer", "Soft Cotton x3"),
        ERLocationData("CL/BS: Cinquedea - down cliff NW of BS, bottom layer", "Cinquedea"),
        ERLocationData("CL/BS: Dragoncrest Shield Talisman - down cliff N of BS, bottom layer", "Dragoncrest Shield Talisman"),
    ],
    "Smoldering Church":[
        ERLocationData("CL/(SC): Sacred Scorpion Charm - kill invader", "Sacred Scorpion Charm", hostile_npc=True),
        ERLocationData("CL/(SC): Missionary's Cookbook [3] - on corpse", "Missionary's Cookbook [3]"),
        ERLocationData("CL/(SC): Nomadic Warrior's Cookbook [14] - on corpse", "Nomadic Warrior's Cookbook [14]"),
    ],
    "Bestial Sanctum":[
        ERLocationData("CL/(BS): Clawmark Seal - Gurranq, deathroot reward 1", "Clawmark Seal", npc=True, missable=True),
        ERLocationData("CL/(BS): Beast Eye - Gurranq, deathroot reward 1 or kill", "Beast Eye", npc=True),
        ERLocationData("CL/(BS): Bestial Sling - Gurranq, deathroot reward 2", "Bestial Sling", npc=True, missable=True),
        ERLocationData("CL/(BS): Bestial Vitality - Gurranq, deathroot reward 3", "Bestial Vitality", npc=True, missable=True),
        ERLocationData("CL/(BS): Ash of War: Beast's Roar - Gurranq, deathroot reward 4", "Ash of War: Beast's Roar", npc=True, missable=True),
        ERLocationData("CL/(BS): Ancient Dragon Smithing Stone - kill Gurranq", "Ancient Dragon Smithing Stone", npc=True),
    ],
    "Dragonbarrow Cave":[
        ERLocationData("CL/(DC): Golden Rune [12] - first room", "Golden Rune [12]"),
        ERLocationData("CL/(DC): Warming Stone - first room", "Warming Stone"),
        ERLocationData("CL/(DC): Bull-Goat's Talisman - second room, before dropdown", "Bull-Goat's Talisman"),
        ERLocationData("CL/(DC): Beast Blood x3 - bottom of dropdown", "Beast Blood x3"),
        ERLocationData("CL/(DC): Golden Rune [8] - bottom of dropdown", "Golden Rune [8]"),
        ERLocationData("CL/(DC): Flamedrake Talisman +2 - boss drop", "Flamedrake Talisman +2", boss=True),
    ],
    "Fort Faroth":[
        ERLocationData("CL/(FF): Golden Rune [9] - enemy drop 1", "Golden Rune [9]", drop=True),
        ERLocationData("CL/(FF): Golden Rune [9] - enemy drop 2", "Golden Rune [9]", drop=True),
        ERLocationData("CL/(FF): Golden Rune [9] - enemy drop 3", "Golden Rune [9]", drop=True),
        ERLocationData("CL/(FF): Dectus Medallion (Right) - chest top of ladder", "Dectus Medallion (Right)", progression=True),
        ERLocationData("CL/(FF): Neutralizing Boluses x2 - top of fort", "Neutralizing Boluses x2"),
        ERLocationData("CL/(FF): Golden Rune [12] - on fort rafters", "Golden Rune [12]"),
        ERLocationData("CL/(FF): Radagon's Soreseal - after rafters jump in room", "Radagon's Soreseal"),
    ],
    "Sellia Hideaway":[
        ERLocationData("CL/(SH): Golden Rune [3] - in front of the illusory wall", "Golden Rune [3]"),
        ERLocationData("CL/(SH): Golden Rune [5] - first big room, drop to left crystal", "Golden Rune [5]"),
        ERLocationData("CL/(SH): Glowstone x4 - first big room, by camp", "Glowstone x4"),
        ERLocationData("CL/(SH): Ghost Glovewort [4] - enemy drop lower first big room", "Ghost Glovewort [4]", drop=True),
        ERLocationData("CL/(SH): Stimulating Boluses - lower first big room", "Stimulating Boluses"),
        ERLocationData("CL/(SH): Golden Rune [5] - lower first big room", "Golden Rune [5]"),
        ERLocationData("CL/(SH): Lost Ashes of War - lower first big room", "Lost Ashes of War"),
        ERLocationData("CL/(SH): Somber Smithing Stone [4] - route from lower first big room back up", "Somber Smithing Stone [4]"),
        ERLocationData("CL/(SH): Crystalian Ashes - second big room, right of entrance follow crystal drop down path", "Crystalian Ashes", hidden=True),
        ERLocationData("CL/(SH): Preserving Boluses x3 - second big room, follow right side", "Preserving Boluses x3"),
        ERLocationData("CL/(SH): Crystal Spear - chest second big room, follow right side, behind illusory wall near corpse", "Crystal Spear", hidden=True),
        ERLocationData("CL/(SH): Crystal Dart x10 - lower second big room", "Crystal Dart x10"),
        ERLocationData("CL/(SH): Crystal Torrent - boss drop", "Crystal Torrent", boss=True),
    ],
    "Cathedral of Dragon Communion":[
        # dont require dragon kill
        ERLocationData("CL/(CDC): Ancient Dragon Apostle's Cookbook [3] - by dragon", "Ancient Dragon Apostle's Cookbook [3]"),
        ERLocationData("CL/(CDC): Glintstone Breath - Dragon Communion", "Glintstone Breath", shop=True),
        ERLocationData("CL/(CDC): Rotten Breath - Dragon Communion", "Rotten Breath", shop=True),
        ERLocationData("CL/(CDC): Dragonice - Dragon Communion", "Dragonice", shop=True),
        
        # need dragon kill
        ERLocationData("CL/(CDC): Agheel's Flame - Dragon Communion", "Agheel's Flame", shop=True),
        ERLocationData("CL/(CDC): Magma Breath - Dragon Communion", "Magma Breath", shop=True),
        ERLocationData("CL/(CDC): Theodorix's Magma - Dragon Communion", "Theodorix's Magma", shop=True),
        ERLocationData("CL/(CDC): Smarag's Glintstone Breath - Dragon Communion", "Smarag's Glintstone Breath", shop=True),
        ERLocationData("CL/(CDC): Ekzykes's Decay - Dragon Communion", "Ekzykes's Decay", shop=True),
        ERLocationData("CL/(CDC): Borealis's Mist - Dragon Communion", "Borealis's Mist", shop=True),
        ERLocationData("CL/(CDC): Greyoll's Roar - Dragon Communion", "Greyoll's Roar", shop=True),
    ],
    "Caelid Catacombs":[
        ERLocationData("CL/(CC): Miranda Sprout Ashes - illusory wall under stairs", "Miranda Sprout Ashes", hidden=True),
        ERLocationData("CL/(CC): Kindred of Rot Ashes - boss drop", "Kindred of Rot Ashes", boss=True),
    ],
    "Caelid Waypoint Ruins":[
        ERLocationData("CL/(CWR): Great Dragonfly Head x5 - middle of ruins", "Great Dragonfly Head x5"),
        ERLocationData("CL/(CWR): Rot Grease x3 - near tree", "Rot Grease x3"),
        ERLocationData("CL/(CWR): Meteoric Ore Blade - chest underground", "Meteoric Ore Blade"),
    ],
    "Gaol Cave":[ # 2
        ERLocationData("CL/(GC): Rune Arc - chest by grace", "Rune Arc"),
        ERLocationData("CL/(GC): Golden Rune [2] - first room", "Golden Rune [2]"),
        ERLocationData("CL/(GC): Golden Rune [4] - alcove before cage lever room", "Golden Rune [4]"),
        ERLocationData("CL/(GC): Turtle Neck Meat x2 - alcove before cage lever room", "Turtle Neck Meat x2"),
        ERLocationData("CL/(GC): Golden Rune [5] - within lever room", "Golden Rune [5]"),
        ERLocationData("CL/(GC): Somber Smithing Stone [5] - chest in lever room", "Somber Smithing Stone [5]"),
        # after lever
        ERLocationData("CL/(GC): Golden Rune [2] - cage across from broken floor, after lever", "Golden Rune [2]"),
        ERLocationData("CL/(GC): Old Fang x5 - cage beside lever, after lever", "Old Fang x5"),
        ERLocationData("CL/(GC): Pillory Shield - cage beside lever, after lever", "Pillory Shield"),
        ERLocationData("CL/(GC): Golden Rune [2] - cage next to dropdown, after lever", "Golden Rune [2]"),
        ERLocationData("CL/(GC): Wakizashi - cage with 3 items after dropdown, after lever", "Wakizashi"),
        ERLocationData("CL/(GC): Golden Rune [4] - cage with 3 items after dropdown, after lever", "Golden Rune [4]"),
        ERLocationData("CL/(GC): Stonesword Key - cage with 3 items after dropdown, after lever", "Stonesword Key"),
        ERLocationData("CL/(GC): Rainbow Stone - room before boss drop, after lever", "Rainbow Stone"),
        ERLocationData("CL/(GC): Golden Rune [4] - room before boss drop, after lever", "Golden Rune [4]"),
        ERLocationData("CL/(GC): Putrid Corpse Ashes - boss drop", "Putrid Corpse Ashes", boss=True),
        ERLocationData("CL/(GC): Regalia of Eochaid - after boss", "Regalia of Eochaid"),
        ERLocationData("CL/(GC): Glowstone x3 - after boss", "Glowstone x3"),
    ],
    "Fort Gael":[
        # outside
        ERLocationData("CL/(FG): Smoldering Butterfly x6 - in burning pile of corpses outback", "Smoldering Butterfly x6"),
        ERLocationData("CL/(FG): Fire Blossom x3 - enemy drop 1 outback", "Fire Blossom x3", drop=True),
        ERLocationData("CL/(FG): Smoldering Butterfly x5 - enemy drop 1 outback", "Smoldering Butterfly x5", drop=True),
        ERLocationData("CL/(FG): Fire Blossom x3 - enemy drop 2 outback", "Fire Blossom x3", drop=True),
        ERLocationData("CL/(FG): Smoldering Butterfly x5 - enemy drop 2 outback", "Smoldering Butterfly x5", drop=True),
        ERLocationData("CL/(FG): Flame, Grant Me Strength - against wall outback", "Flame, Grant Me Strength"),
        # inside
        ERLocationData("CL/(FG): Warming Stone x2 - walk the plank item", "Warming Stone x2"),
        ERLocationData("CL/(FG): Starscourge Heirloom - chest upper platform", "Starscourge Heirloom"),
        ERLocationData("CL/(FG): Mushroom x10 - wood platform behind a tower near gate lever", "Mushroom x10"),
        ERLocationData("CL/(FG): Katar - chest in lower room", "Katar"),
        ERLocationData("CL/(FG): Ash of War: Lion's Claw - enemy drop in courtyard", "Ash of War: Lion's Claw", drop=True),
        ERLocationData("CL/(FG): Rune Arc - in courtyard", "Rune Arc"),
    ],
    "Street of Sages Ruins":[
        ERLocationData("CL/(SSR): Golden Rune [4] - in SW Ruin", "Golden Rune [4]"),
        ERLocationData("CL/(SSR): Meteorite Staff - on window SW Ruin", "Meteorite Staff"),
        ERLocationData("CL/(SSR): Rock Sling - chest underground", "Rock Sling"),
        # 5 items in 1 check
        ERLocationData("CL/(SSR): Perfume Bottle - in raised ruin", "Perfume Bottle"),
        ERLocationData("CL/(SSR): Traveler's Hat - in raised ruin", "Traveler's Hat"),
        ERLocationData("CL/(SSR): Perfumer's - in raised ruin", "Perfumer's"),
        ERLocationData("CL/(SSR): Traveler's Gloves - in raised ruin", "Traveler's Gloves"),
        ERLocationData("CL/(SSR): Traveler's Slops - in raised ruin", "Traveler's Slops"),
    ],
    
    "":[],
    "Redmane Castle":[
        ERLocationData("CL/(RC): Smithing Stone [3] - behind entrance tower", "Smithing Stone [3]"),
        ERLocationData("CL/(RC): Smithing Stone [6] - on entrance tower", "Smithing Stone [6]"),
        ERLocationData("CL/(RC): Ash of War: Flaming Strike - scarab, graveyard by back entrance", "Ash of War: Flaming Strike", scarab=True),
        ERLocationData("CL/(RC): Golden Rune [9] - enemy drop, graveyard by back entrance", "Golden Rune [9]", drop=True),
        ERLocationData("CL/(RC): Smoldering Butterfly x8 - graveyard by back entrance", "Smoldering Butterfly x8"),
        ERLocationData("CL/(RC): Smithing Stone [5] - by back entrance shortcut door", "Smithing Stone [5]"),
        ERLocationData("CL/(RC): Armorer's Cookbook [5] - by back entrance shortcut door", "Armorer's Cookbook [5]"),
        ERLocationData("CL/(RC): Armorer's Cookbook [4] - room W side of front courtyard", "Armorer's Cookbook [4]"),
        ERLocationData("CL/(RC): Golden Rune [6] - wood structure S side of front courtyard", "Golden Rune [6]"),
        ERLocationData("CL/(RC): Smithing Stone [4] - front courtyard", "Smithing Stone [4]"),
        ERLocationData("CL/(RC): Somber Smithing Stone [4] - enemy 1 drop front courtyard", "Somber Smithing Stone [4]", drop=True),
        ERLocationData("CL/(RC): Beast Blood - enemy 1 drop front courtyard", "Beast Blood", drop=True),
        ERLocationData("CL/(RC): Old Fang x2 - enemy 1 drop front courtyard", "Old Fang x2", drop=True),
        ERLocationData("CL/(RC): Somber Smithing Stone [4] - enemy 2 drop front courtyard", "Somber Smithing Stone [4]", drop=True),
        ERLocationData("CL/(RC): Beast Blood - enemy 2 drop front courtyard", "Beast Blood", drop=True),
        ERLocationData("CL/(RC): Old Fang x2 - enemy 2 drop front courtyard", "Old Fang x2", drop=True),
        ERLocationData("CL/(RC): Red-Hot Whetblade - upper front courtyard in NW room", "Red-Hot Whetblade", prominent=True),
        ERLocationData("CL/(RC): Smithing Stone [6] - upper front courtyard NW room, follow upper path till chest", "Smithing Stone [6]"),
        ERLocationData("CL/(RC): Smithing Stone [4] - out from grace, to W, up wood stairs on platform", "Smithing Stone [4]"),
        ERLocationData("CL/(RC): Flamberge - room S of COP, up ladder, behind enemy", "Flamberge"),
        ERLocationData("CL/(RC): Smithing Stone [3] - room S of COP, up ladder, corpse on ledge", "Smithing Stone [3]"),
        ERLocationData("CL/(RC): Smithing Stone [5] - room S of COP, up ladder x2", "Smithing Stone [5]"),
        ERLocationData("CL/(RC): Ruins Greatsword - boss drop", "Ruins Greatsword", boss=True),
        ERLocationData("CL/(RC): Somber Smithing Stone [5] - to N after boss arena", "Somber Smithing Stone [5]"),
        
        # requires festival
        ERLocationData("CL/(RC): Smithing Stone [6] - in church during festival", "Smithing Stone [6]"),
    ],
    "sand dune place":[],
    "the cata after the dune":[],
    
    # "":[],
    # ERLocationData(":  - ", ""),
    # MARK: Altus
    "Altus Plateau":[],
    
    # "":[],
    # ERLocationData(":  - ", ""),
    # MARK: Leyndell
    "Leyndell, Royal Capital":[],
    "Leyndell, Ashen Capital":[],
    "Divine Bridge":[ # can get to from weeping
        ERLocationData("LRC/(DB): Blessed Dew Talisman - in chest", "Blessed Dew Talisman"), # not missable
    ],

    # "":[],
    # ERLocationData(":  - ", ""),
    # MARK: Miquella's Haligtree
    "Miquella's Haligtree":[
	    # Haligtree Canopy
	    ERLocationData("MH/HC: Sacramental Bud x3 - to S first side branch", "Sacramental Bud x3"),
	    ERLocationData("MH/HC: Stonesword Key - to S behind waygate arrival location", "Stonesword Key"),
    	ERLocationData("MH/HC: Golden Rune [10] - to E after a single drop", "Golden Rune [10]"),
    	ERLocationData("MH/HC: Prattling Pate \"My beloved\" - drop to E, drop onto main branch, go N then up large branch on left, jump up mushrooms", "Prattling Pate \"My beloved\""),
    	ERLocationData("MH/HC: Fire Grease x3 - from main branch, go S take small left branch all the way up then go S", "Fire Grease x3"),
    	ERLocationData("MH/HC: Stonesword Key -  from main branch, go S take small left branch then on a small right branch", "Stonesword Key"),
	    ERLocationData("MH/HC: Aeonian Butterfly x2 - from main branch, go S take small left branch all the way up, go NW and down a small brach on the left", "Aeonian Butterfly"),
    	ERLocationData("MH/HC: Golden Rune [10] - from main branch, go S then left fork", "Golden Rune [10]"),
    	ERLocationData("MH/HC: Envoy Crown - from main branch, go S take left fork then S", "Envoy Crown"),
    	ERLocationData("MH/HC: Dappled Cured Meat - from main branch, go S take right fork", "Dappled Cured Meat"),
    	ERLocationData("MH/HC: Smithing Stone[8] - from main branch, go S take right fork then SE", "Smithing Stone [8]"),
	    ERLocationData("MH/HC: Preserving Boluses - from main branch, go S take small left branch all the way up then go NW", "Preserving Boluses"),
	    ERLocationData("MH/HC: Warming Stone x4 - from main branch, go N", "Warming Stone x4"),
    	ERLocationData("MH/HC: Golden Rune [13] - from main branch, go N then drop on right and cont. N", "Golden Rune [13]"),
	    ERLocationData("MH/HC: Lost Ashes of War - from main branch, go N then drop on right and cont. N, at split go W to small shrine", "Lost Ashes of War"),
	    ERLocationData("MH/HC: Oracle Envoy Ashes - from main branch, go N then drop on right and cont. N, at split go E to top of branch", "Oracle Envoy Ashes"),
	    # Haligtree Town
	    ERLocationData("MH/HC: Flaming Bolt x10 - to E up ladder, S up branch item 2", "Flaming Bolt x10"),
    	ERLocationData("MH/HC: Numen's Rune - to E up ladder, S up branch item 1", "Numen's Rune"),
    	ERLocationData("MH/HT: Golden Rune [10] - to NW by the first ladder", "Golden Rune [10]"),
    	ERLocationData("MH/HT: Rot Grease x2 - to NW up the first ladder", "Rot Grease x2"),
    	ERLocationData("MH/HT: Pearldrake Talisman +2 - to NW up the first ladder, jump SE over a gap", "Pearldrake Talisman +2"),
    	ERLocationData("MH/HT: Smithing Stone [8] - to NW first building top floor", "Smithing Stone [8]"),
    	ERLocationData("MH/HT: Hefty Beast Bone x6 - to NW first building lower floor", "Hefty Beast Bone x6"),
    	ERLocationData("MH/HT: Golden Rune [13] - to NW first building lower floor rear balcony", "Golden Rune [13]"),
    	ERLocationData("MH/HT: Fire Grease x5 - to NW on small wooden bridge", "Fire Grease x5"),
    	ERLocationData("MH/HT: Ancient Dragon Smithing Stone - to N in the courtyard", "Ancient Dragon Smithing Stone"),
    	# Haligtree Town Plaza
    	#ERLocationData("MH/HT: Somber Smithing Stone [8] - to N on a balcony", "Somber Smithing Stone [8]"),
    	ERLocationData("MH/HP: Golden Rune [12] - beside the grace", "Golden Rune [12]"),
    	ERLocationData("MH/HP: Aeonian Butterfly x4 - to E down on a branch", "Aeonian Butterfly x4"),
    	ERLocationData("MH/HP: Somber Smithing Sone [9] - to S first building top floor", "Somber Smithing Stone [9]"),
    	ERLocationData("MH/HP: Smithing Stone [6] - to S first building top roof", "Smithing Stone [6]"),
    	ERLocationData("MH/HP: Golden Rune [10] - to NE first building lower roof", "Golden Rune [10]"),
    	ERLocationData("MH/HP: Golden Rune [12] - to NE first building lower floor", "Golden Rune [12]"),
    	ERLocationData("MH/HP: Viridian Amber Medallion +2 - to NE first building lower floor in chest", "Viridian Amber Medallion +2"),
    	ERLocationData("MH/HP: Smithing Stone [6] - to NE round building roof", "Smithing Stone [6]"),
    	ERLocationData("MH/HP: Sacramental Bud - to NE round building west wing", "Sacramental Bud"),
    	ERLocationData("MH/HP: Smithing Stone [7] - to NE on a bridge by the elevator", "Smithing Stone [7]"),
    	ERLocationData("MH/HP: Hero's Rune [4] - to NE in the small rotunda by the elevator", "Hero's Rune [4]"),
    	ERLocationData("MH/HP: Smithing Stone [8] - NE in the large rotunda by the elevator", "Smithing Stone [8]"),
    	ERLocationData("MH/HP: Loretta's Mastery - boss of HT", "Loretta's Mastery", boss=True),
    	ERLocationData("MH/HP: Loretta's War Sickle - boss of HT", "Loretta's War Sickle", boss=True),
    ],
    "Elphael, Brace of the Haligtree":[
    	# Prayer Room
    	ERLocationData("BH/PR: Ancient Dragon Smithing Stone - chest after HT boss fight", "Ancient Dragon Smithing Stone"),
    	ERLocationData("BH/PR: Holy Grease x3 - to SE on bridge", "Holy Grease x3"),
    	ERLocationData("BH/PR: Golden Rune [12] - just N in small room to the left", "Golden Rune [12]"),
    	ERLocationData("BH/PR: Smithing Stone [8] - N down 2 stairs, left door stairs up to balcony", "Smithing Stone [8]"),
    	ERLocationData("BH/PR: Miquellan Knight's Sword - under large bell along second buttress, look up", "Miquellan Knight's Sword"),
    	ERLocationData("BH/PR: Lightning Greatbolt x5 - N down 3 stairs on a railing", "Lightning Greatbolt x5"),
    	ERLocationData("BH/PR: Triple Rings of Light - exit PR then drop to E, behind imp statue", "Triple Rings of Light"), # 1
    	ERLocationData("BH/PR: Smithing Stone [7] - exit PR then drop to E, go N door on left", "Smithing Stone [7]"),
    	ERLocationData("BH/PR: Immunizing White Cured Meat - N down 3 stairs, S down 2 stairs, N down 2 stairs", "Immunizing White Cured Meat"),
    	ERLocationData("BH/PR: Smithing Stone [7] - in room under crimson scarab", "Smithing Stone [7]"),
    	ERLocationData("BH/PR: Golden Rune [10] - balcony of room under crimson scarab", "Golden Rune [10]"),
    	ERLocationData("BH/PR: Seedbed Curse - before room under crimson scarab jump over railing to small ledge then take stairs", "Seedbed Curse", hidden=True),
    	ERLocationData("BH/PR: Rotten Staff - miniboss E of PR on outer wall", "Rotten Staff", boss=True),
    	ERLocationData("BH/PR: Numen's Rune - S section of outer wall middle of open area", "Numen's Rune"),
    	ERLocationData("BH/PR: Somber Ancient Dragon Smithing Stone - S section of outer wall all the way S", "Somber Ancient Dragon Smithing Stone"),
    	ERLocationData("BH/PR: Marika's Soreseal - behind imp statue at the S end of the bottom area", "Marika's Soreseal"), # 2
    	ERLocationData("BH/PR: Golden Rune [12] - in front of the imp statue at the S end of the bottom area", "Golden Rune [12]"),
    	ERLocationData("BH/PR: Aeonian Butterfly x4 - just N of the imp statue at the S end of the bottom area", "Aeonian Butterfly x4"),
    	ERLocationData("BH/PR: Beast Blood x3 - in a door on the left just N of the imp statue at the S end of the bottom area", "Beast Blood x3"),
    	ERLocationData("BH/PR: Pickled Turtle Neck - large dark room at the bottom, item 1", "Pickled Turtle Neck"),
    	ERLocationData("BH/PR: Somber Smithing Stone [9] - large dark room at the bottom, item 2", "Somber Smithing Stone [9]"),
    	ERLocationData("BH/PR: Lord's Rune - room on right side of bottom area, about halfway", "Lord's Rune"),
    	ERLocationData("BH/PR: Smithing Stone [8] - N end of the bottom area", "Smithing Stone [8]"),
    	ERLocationData("BH/PR: Ghost Glovewort [9] 1 - enemy drop at bottom", "Ghost Glovewort [9]", drop=True),
    	ERLocationData("BH/PR: Ghost Glovewort [9] 2 - enemy drop at bottom", "Ghost Glovewort [9]", drop=True),
    	ERLocationData("BH/PR: Ghost Glovewort [9] 3 - enemy drop at bottom", "Ghost Glovewort [9]", drop=True),
    	ERLocationData("BH/PR: Ghost Glovewort [9] 4 - enemy drop at bottom", "Ghost Glovewort [9]", drop=True),
    	ERLocationData("BH/PR: Ghost Glovewort [9] 5 - enemy drop at bottom", "Ghost Glovewort [9]", drop=True),
    	ERLocationData("BH/PR: Cleanrot Knight Finlay - chest in a room E of crimson scarab", "Cleanrot Knight Finlay"),
    	ERLocationData("BH/PR: Somber Smithing Stone [9] - S section of outer wall in building", "Somber Smithing Stone [9]"),
    	ERLocationData("BH/PR: Somber Ancient Dragon Smithing Stone - up buttress N of crimson scarab in a chest", "Somber Ancient Dragon Smithing Stone"),
    	ERLocationData("BH/PR: Seedbed Curse - up buttress N of crimson scarab in a chair", "Seedbed Curse"),
    	ERLocationData("BH/PR: Old Fang x5 - up root N of room under crimson scarab", "Old Fang x5"),
    	ERLocationData("BH/PR: Warming Stone x2 - N section of outer wall inside room, item 1", "Warming Stone x2"),
        ERLocationData("BH/PR: Spiritflame Arrow x15 - N section of outer wall inside room, item 2", "Spiritflame Arrow x15"),
        ERLocationData("BH/PR: Haligtree Soldier Ashes - N section of outer wall up stairs in front of large basin", "Haligtree Soldier Ashes"),
        ERLocationData("BH/PR: Smithing Stone [8] - N section of outer wall by a drop to main area", "Smithing Stone [8]"),
    	# Elphael Inner Wall
    	ERLocationData("BH/IW: Lord's Rune - miniboss E of IW", "Lord's Rune", boss=True),
    	ERLocationData("BH/IW: Sacramental Bud - to E then hard right", "Sacramental Bud"),
    	ERLocationData("BH/IW: Arteria Leaf - to E on steps to small bridge", "Arteria Leaf"),
    	ERLocationData("BH/IW: Golden Rune [11] - to E on a small bridge", "Golden Rune [11]"),	
    	ERLocationData("BH/IW: Smithing Stone [6] - to N", "Smithing Stone [6]"),
    	ERLocationData("BH/IW: Haligtree Knight Helm - to NE up the ladder", "Haligtree Knight Helm"),
    	ERLocationData("BH/IW: Rotten Crystal Sword - to S then left in a chest", "Rotten Crystal Sword"),
    	ERLocationData("BH/IW: Hero's Rune [5] - to SE behind a basin at the end of the hallway", "Hero's Rune [5]"),
    	ERLocationData("BH/IW: Rot Grease - left at the first rot lake", "Rot Grease"),
    	ERLocationData("BH/IW: Golden Seed - miniboss in second rot lake", "Golden Seed", boss=True),
    	ERLocationData("BH/IW: Great Grave Glovewort - in second rot lake", "Great Grave Glovewort"),
    	#ERLocationData("BH/IW: Rotten Winged Sword Insignia - Millicent quest invasion, help", "Rotten Winged Sword Insignia", missable=True, npc=True),
    	#ERLocationData("BH/IW: Unalloyed Gold Needle - help Millicent talk then reload area", "Unalloyed Gold Needle", missable=True, npc=True),
    	#ERLocationData("BH/IW: Millicent's Prosthesis - Milicent quest invasion, kill", "Millicent's Prosthesis", missable=True, npc=True),
    	# Drainage Channel
    	ERLocationData("BH/DC: Golden Rune [10] - to W up the ladder on the left", "Golden Rune [10]"),
    	ERLocationData("BH/DC: Nascent Butterfly - on the SE balcony of the main building", "Nascent Butterfly"),
    	ERLocationData("BH/DC: Aeonian Butterfly - on the NW balcony of the main building", "Aeonian Butterfly"),
    	ERLocationData("BH/DC: Ghost-Glovewort Picker's Bell Bearing [3] - against a tombstone N of the main building", "Ghost-Glovewort Picker's Bell Bearing [3]"),
    	ERLocationData("BH/DC: Numen's Rune - on a small ledge N of the main building ", "Numen's Rune"),
    	ERLocationData("BH/DC: Arteria Leaf x3 - in a small puddle S of the main building", "Arteria Leaf x3"),
    	ERLocationData("BH/DC: Hero's Rune [5] - against a large tree S of the main building", "Hero's Rune [5]"),
    	ERLocationData("BH/DC: Dragoncrest Greatshield Talisman - dropdown through a hole at the top of the roof, drop W to a ledge in the building, in a chest", "Dragoncrest Greatshield Talisman"), 
    	# Haligtree Roots
    	ERLocationData("BH/HR: Traveler's Clothes - S of HR by the giant rot flower", "Traveler's Clothes"),
    	ERLocationData("BH/HR: Traveler's Manchettes - S of HR by the giant rot flower", "Traveler's Manchettes"),
    	ERLocationData("BH/HR: Traveler's Boots - S of HR by the giant rot flower", "Traveler's Boots"),
    	ERLocationData("BH/HR: Malenia's Great Rune - BH boss fight", "Malenia's Great Rune", mainboss=True),
    	ERLocationData("BH/HR: Remembrance of the Rot Goddess - BH boss fight", "Remembrance of the Rot Goddess", mainboss=True),
    	#ERLocationData("BH/HR: Miquella's Needle - use UGN on flower after BH boss fight & finish Milicent quest", "Miquella's Needle", missable=True, npc=True),
    	#ERLocationData("BH/HR: Somber Ancient Dragon Smithing Stone - use UGN on flower after BH boss fight & finish Milicent quest", "Somber Ancient Dragon Smithing Stone", missable=True, npc=True),
    ],

    # MARK: DLC Locations
    "Gravesite Plain":[
    ],
}

for i, region in enumerate(region_order + region_order_dlc):
    for location in location_tables[region]: location.region_value = i

for region in region_order_dlc:
    for location in location_tables[region]:
        location.dlc = True

for region in [# conditional locations
    #"Hinterlands" # locked behind o mother
]:
    for location in location_tables[region]:
        location.conditional = True

location_name_groups: Dict[str, Set[str]] = {
    # We could insert these locations automatically with setdefault(), but we set them up explicitly
    # instead so we can choose the ordering.
    "Prominent": set(),
    "Progression": set(),
    "Main Boss Rewards": set(),
    "Boss Rewards": set(),
    "Hostile NPC Rewards": set(),
    "Friendly NPC Rewards": set(),
    "Scarab": set(),
    "Rise Puzzle": set(),
    "Hidden": set(),
    "Missable": set(),
}

location_descriptions = {
    "Prominent": "A small number of locations that are in very obvious locations. Mostly boss " + \
                 "drops. Ideal for setting as priority locations.",
    "Progression": "Locations that contain items in vanilla which unlock other locations.",
    "Main Boss Rewards": "Any boss that drops a Great Rune or a Remembrance.",
    "Boss Rewards": "Boss drops. Only includes enemies considered bosses by the " + \
                        "enemy randomizer.",
    "Hostile NPC Rewards": "Drops from NPCs that are hostile to you. This includes scripted " + \
                           "invaders and initially-friendly NPCs that must be fought as part of their quest.",
    "Friendly NPC Rewards": "Items given by friendly NPCs as part of their quests or from " + \
                            "non-violent interaction.",
    "Scarab": "Scarab locations",
    "Rise Puzzle": "Locations that require a rise puzzle to be solved",
    "Hidden": "Locations that are particularly difficult to find, such as behind illusory " + \
              "walls, down hidden drops, and so on. Does not include large locations.",
    "Missable": "Locations that can be missed in vanilla.",
}

location_dictionary: Dict[str, ERLocationData] = {}
for location_name, location_table in location_tables.items():
    location_dictionary.update({location_data.name: location_data for location_data in location_table})

    for location_data in location_table:
        if not location_data.is_event:
            for group_name in location_data.location_groups():
                location_name_groups[group_name].add(location_data.name)

    # Allow entire locations to be added to location sets.
    if not location_name.endswith(" Shop"):
        location_name_groups[location_name] = set([
            location_data.name for location_data in location_table
            if not location_data.is_event
        ])

temp = location_name_groups['Gravesite Plain'] # might work shrug
counter = 0
for location in region_order_dlc:
    if counter > 1:
        temp.union(location_name_groups[location])
    counter += 1

location_name_groups["DLC"] = temp
