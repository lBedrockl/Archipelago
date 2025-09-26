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
    
    **Region Lock:** Each region will require a 'Special item'
    **Open World:** No region locking"""
    #**Glitches:** Glitches in logic"""
    display_name = "World Logic"
    option_region_lock = 0
    option_open_world = 1
    #option_glitches = 2
    default = 0
    
class RegionSoftLogic(DefaultOnToggle):
    """Region Soft Logic
    
    You might get early caelid access but you won't be expected to go there early.
    """
    display_name = "Region Soft Logic"

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
    display_name = "Enemy randomizer"

class MaterialRando(Toggle):
    """Randomizes the indefinitely spawning materials."""
    display_name = "Material Randomizer"

## Item & Location

class RandomizeStartingLoadout(DefaultOnToggle):
    """Randomizes the equipment characters begin with."""
    display_name = "Randomize Starting Loadout"

class AutoEquipOption(Toggle):
    """Automatically equips any received armor or left/right weapons."""
    display_name = "Auto-Equip"
    
class SmithingBellBearingOption(Choice):
    """Choose how smithing stone bell bearings are handled.

    - **Randomize:** Can be anywhere.
    - **Progression Randomize:** Make them a progression item, and be required for the area after they would normally be in.
    - **Do Not Randomize:** Leave them at their normal spots.
    """
    display_name = "Smithing Bell Bearing Behavior"
    option_randomize = 0
    option_progression_randomize = 1
    option_do_not_randomize = 2
    default = 1
    
class LocalItemOnly(Toggle):
    """Only progression or useful items will show up in other players games."""
    display_name = "Local Item Option"
    
class ExcludeLocalItemOnly(OptionDict):
    """If LocalItemOnly is true then these item categories will show up in other players games.
    - [Items] **Item Group**
    - [~600] **Weapon**: All Weapons and Ammo.
    - [621] **Armor**: All Armors.
    - [154] **Accessory**: All Talismans.
    - [105] **AshofWar**: All Ashes of War.
    - [~3700] *Goods*: All Goods.
    
    Goods should always be local only.
    """
    default = frozenset({"Weapon", "Armor", "Accessory"})

class ERExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important item.
    - **dlc**: If you want DLC items but dont wanna do DLC.
    - **hidden: Hard to find items.**"""
    default = frozenset({"Hidden"})
    
class ERImportantLocations(PriorityLocations):
    """Prevent these locations from having an unimportant item.
    - [Checks] **Locations**
    - [25] *Remembrance*: Main boss Remembrances.
    - [33] *Seedtree*: Golden Seed trees.
    - [13] *Basin*: Basins that contain tears.
    - [12] *Church*: Sacred Tears.
    - [24] *Map*: Map pillars.
    - [52] *Fragment*: Scadu Fragments.
    - [13] *Cross*: All cross items.
    - [26] *Revered*: Revered Spirit Ashes.
    - [21] *KeyItem*: Key items.
    
    The total amount of priority checks should be below:
    - **Vanilla**: [95] 
    - **DLC**: [124]
    - THESE CAN CHANGE, need to be updated later
    """
    default = frozenset({"Remembrance", "Seedtree", "Map"})

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

    - **Randomize:** Progression items can be placed in missable locations, don't do this unless you know what your doing, you can make a game impossible.
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
    soft_logic: RegionSoftLogic
    great_runes_required: GreatRunesRequired
    enable_dlc: EnableDLC
    late_dlc: LateDLCOption
    enemy_rando: EnemyRando
    material_rando: MaterialRando
    death_link: DeathLink

    random_start: RandomizeStartingLoadout
    auto_equip: AutoEquipOption

    smithing_bell_bearing_option: SmithingBellBearingOption
    local_item_option: LocalItemOnly
    exclude_local_item_only: ExcludeLocalItemOnly
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
        SmithingBellBearingOption,
        LocalItemOnly,
        ExcludeLocalItemOnly,
        ERImportantLocations,
        ERExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ])
]
