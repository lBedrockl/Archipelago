from dataclasses import dataclass

from Options import Choice, DeathLink, DefaultOnToggle, ExcludeLocations, PriorityLocations, NamedRange, OptionDict, \
    OptionGroup, PerGameCommonOptions, Range, Removed, Toggle

## Game Options

class EndingCondition(Choice):
    """Ending Condition options
    
    **Final Boss:** Will be Elden Beast, or Consort if DLC is enabled.
    **Elden Beast:** Kill Elden Beast, for short runs with DLC on.
    **All Remembrances:** All remembrance bosses, missable ones excluded.
    **All Bosses:** All bosses, missable ones excluded.
    If DLC is on those bosses / remembrances are included."""
    display_name = "Ending Condition"  # this is the option name as it's displayed to the user on the webhost and in the spoiler log
    option_final_boss = 0
    option_elden_beast = 1
    option_all_remembrances = 2
    option_all_bosses = 3

class WorldLogic(Choice):
    """World Logic options
    
    **Region Lock:** Each region will require '# of great runes or special item'
    **Open World:** No region locking"""
    #**Glitches:** Glitches in logic"""
    display_name = "World Logic"
    option_region_lock = 0
    option_open_world = 1
    #option_glitches = 2
    default = 0

class GreatRunesRequired(Range):
    """How many great runes are required to enter Leyndell
    This option is ignored if Region Lock in On"""
    display_name = "Leyndell Great Runes Required"
    range_start = 1
    range_end = 7
    default = 2


class EnableDLC(Toggle):
    """Enable DLC"""
    display_name = "Enable DLC"  # this is the option name as it's displayed to the user on the webhost and in the spoiler log

class LateDLCOption(Choice):
    """Guarantee that you don't need to enter the DLC until later in the run.

    - **Off:** You may have to enter the DLC with 'Pureblood Knight Medal' item.
    - **Medallion:** You won't have to enter the DLC until after getting Haligtree Secret Medallion and Rold Medallion.
    """
    display_name = "Late DLC"
    option_off = 0
    alias_false = 0
    option_after_medallion = 1
    alias_true = 1
    
class EnemyRando(Toggle):
    """Randomizes the enemies."""
    display_name = "Enemy rando"

## Item & Location

class RandomizeStartingLoadout(DefaultOnToggle):
    """Randomizes the equipment characters begin with."""
    display_name = "Randomize Starting Loadout"


class AutoEquipOption(Toggle):
    """Automatically equips any received armor or left/right weapons."""
    display_name = "Auto-Equip"

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important item."""
    default = frozenset({"Hidden"})
    
class ERImportantLocations(PriorityLocations):
    """Prevent these locations from having an unimportant item."""
    default = frozenset({"Seedtree", "Basin", "Church", "Map", "Fragment", "Cross", "Revered"})

class ExcludedLocationBehaviorOption(Choice):
    """How to choose items for excluded locations in ER.

    - **Randomize:** Progression items can be placed in excluded locations.
    - **Randomize Unimportant:** Progression items can't be placed in excluded locations.
    - **Do Not Randomize:** Excluded locations always contain the same item as in vanilla EldenRing.

    A "progression item" is anything that's required to unlock another location in some game.
    """
    display_name = "Excluded Locations Behavior"
    option_randomize = 0
    option_randomize_unimportant = 1
    option_do_not_randomize = 2
    default = 1

class MissableLocationBehaviorOption(Choice):
    """Which items can be placed in locations that can be permanently missed.

    - **Randomize:** Progression items can be placed in missable locations.
    - **Randomize Unimportant:** Progression items can't be placed in missable locations.
    - **Do Not Randomize:** Missable locations always contain the same item as in vanilla EldenRing.

    A "progression item" is anything that's required to unlock another location in some game.
    """
    display_name = "Missable Locations Behavior"
    option_randomize = 0
    option_randomize_unimportant = 1
    option_do_not_randomize = 2
    default = 1

@dataclass
class EROptions(PerGameCommonOptions):
    ending_condition: EndingCondition
    world_logic: WorldLogic
    great_runes_required: GreatRunesRequired
    enable_dlc: EnableDLC
    late_dlc: LateDLCOption
    enemy_rando: EnemyRando
    death_link: DeathLink

    random_start: RandomizeStartingLoadout
    auto_equip: AutoEquipOption

    important_locations: ERImportantLocations
    exclude_locations: ERExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption

option_groups = [
    OptionGroup("Equipment", [
        RandomizeStartingLoadout,
        AutoEquipOption,
    ]),
    OptionGroup("Item & Location Options", [
        ERImportantLocations,
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ])
]
