from collections.abc import Sequence
from collections import defaultdict
import settings, typing, json
from logging import warning
from typing import cast, Any, Callable, Dict, Set, List, Optional, TextIO, Union

from BaseClasses import CollectionState, MultiWorld, Region, Location, LocationProgressType, Entrance, Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import CollectionRule, ItemRule, add_rule, add_item_rule

from .items import ERItem, ERItemData, filler_item_names, filler_item_names_vanilla, item_descriptions, item_table, item_table_vanilla, item_name_groups
from .locations import ERLocation, ERLocationData, location_tables, location_descriptions, location_dictionary, location_name_groups, region_order, region_order_dlc
from .options import EROptions, option_groups
from Options import OptionError

# Settings
class EldenRingSettings(settings.Group):
    class DisableExtremeOptions(str):
        """ Disables extreme options, like progression items being in missable locations."""
    disable_extreme_options: typing.Union[DisableExtremeOptions, bool] = False

# Web stuff
class EldenRingWeb(WebWorld):
    rich_text_options_doc = True
    theme = "stone"
    option_groups = option_groups
    item_descriptions = item_descriptions

# Main World
class EldenRing(World):
    """
    This is the description of the game that will be displayed on the AP website.
    """

    game = "EldenRing"
    options: EROptions
    options_dataclass = EROptions
    web = EldenRingWeb()
    settings: typing.ClassVar[EldenRingSettings]
    base_id = 69000
    required_client_version = (0, 4, 2) # tbh idk what version is needed, probs newest
    topology_present = True
    item_name_to_id = {data.name: data.ap_code for data in item_table.values() if data.ap_code is not None}
    location_name_to_id = {
        location.name: location.ap_code
        for locations in location_tables.values()
        for location in locations
        if location.ap_code is not None
    }
    location_name_groups = location_name_groups
    item_name_groups = item_name_groups
    location_descriptions = location_descriptions
    item_descriptions = item_descriptions

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.all_excluded_locations = set()
        self.all_priority_locations = set()

    def generate_early(self) -> None:
        self.created_regions = set()
        self.all_excluded_locations.update(self.options.exclude_locations.value)
        self.all_priority_locations.update(self.options.important_locations.value)
        
        # makes exclude_local_item_only lowercase
        exclude_local_item_only_lowercase = {key.lower(): value for key, value in self.options.exclude_local_item_only.items()}
        
        if self.settings.disable_extreme_options:
            if self.options.missable_location_behavior == "option_randomize":
                # there is code to fix this but its better to just stop generation and tell them this option needs to change
                raise OptionError(f"EldenRing disable_extreme_options Error:"
                                  f"Player {self.player_name} has missable location behavior set to be option_randomize."
                                  f"This means Progression items can be in missable locations.")
            elif not self.options.local_item_option:
                raise OptionError(f"EldenRing disable_extreme_options Error:"
                                  f"Player {self.player_name} has local_item_option false."
                                  f"This being false means over 3.5k checks come from this world.")
            elif "goods" in exclude_local_item_only_lowercase:
                raise OptionError(f"EldenRing disable_extreme_options Error:"
                                  f"Player {self.player_name} has goods enabled in exclude_local_item_only."
                                  f"This being here means over 3.5k checks come from this world and it bypasses local_item_option.")
            elif self.options.ending_condition == 3:
                raise OptionError(f"EldenRing disable_extreme_options Error:"
                                  f"Player {self.player_name} has ending_condition set to all bosses.")      
                
        #if self.options.leyndell_missable:
            for location in location_tables["Leyndell, Royal Capital", "leyndell_throne"]:
                # there might be some exceptions but lazy all missable :)
                if not location.boss:
                    location.missable = True

        if self.options.smithing_bell_bearing_option.value == 1:
            item_table["Smithing-Stone Miner's Bell Bearing [1]","Smithing-Stone Miner's Bell Bearing [2]",
                        "Smithing-Stone Miner's Bell Bearing [3]","Smithing-Stone Miner's Bell Bearing [4]",
                        "Somberstone Miner's Bell Bearing [1]","Somberstone Miner's Bell Bearing [2]",
                        "Somberstone Miner's Bell Bearing [3]","Somberstone Miner's Bell Bearing [4]",
                        "Somberstone Miner's Bell Bearing [5]",].classification = ItemClassification.progression
                
        if self.options.enable_dlc:
            if self.options.late_dlc:
                item_table["Pureblood Knight's Medal"].classification = ItemClassification.progression
        
        # idk if this works, i pray its just this simple
        if self.options.local_item_option:
            # local_items: List[str] = []
            using_table = item_table_vanilla
            if self.options.enable_dlc: using_table = item_table
            for item in using_table.values():
                if item.classification != ItemClassification.progression and item.classification != ItemClassification.useful:
                    # this picks thing might or might not work :)
                    picks, arg = {
                        'goods': 1,
                        'weapon': 2,
                        'armour': 3,
                        'accessory': 4,
                        'ashofwar': 5,
                    }.get(arg, 9)
                    if item.category not in picks[exclude_local_item_only_lowercase]:
                        self.options.local_items.value.add(item.name)
                        # local_items.append(item.name)
            # self.options.local_items.value = set(local_items)

    def create_regions(self) -> None: #MARK: Connections
        # Create Vanilla Regions
        regions: Dict[str, Region] = {"Menu": self.create_region("Menu", {})}
        regions.update({region_name: self.create_region(region_name, location_tables[region_name]) for region_name in region_order})

        # Create DLC Regions
        if self.options.enable_dlc:
            regions.update({region_name: self.create_region(region_name, location_tables[region_name]) for region_name in region_order_dlc})

        # Connect Regions
        def create_connection(from_region: str, to_region: str):
            connection = Entrance(self.player, f"Go To {to_region}", regions[from_region])
            regions[from_region].exits.append(connection)
            connection.connect(regions[to_region])

        regions["Menu"].exits.append(Entrance(self.player, "New Game", regions["Menu"]))
        self.multiworld.get_entrance("New Game", self.player).connect(regions["Limgrave"])
        
        create_connection("Limgrave", "Miquella's Haligtree") #TEMP TO MAKE GAME WORK
        
        # Limgrave
        create_connection("Limgrave", "Fringefolk Hero's Grave")
        create_connection("Limgrave", "Stormhill")
        create_connection("Limgrave", "Coastal Cave")
        create_connection("Limgrave", "Groveside Cave")
        create_connection("Limgrave", "Stormfoot Catacombs")
        create_connection("Limgrave", "Limgrave Tunnels")
        create_connection("Limgrave", "Murkwater Cave")
        create_connection("Limgrave", "Murkwater Catacombs")
        create_connection("Limgrave", "Highroad Cave")
        create_connection("Limgrave", "Deathtouched Catacombs")
        create_connection("Limgrave", "Roundtable Hold")
        
        create_connection("Limgrave", "Sellia Crystal Tunnel") # in caelid
        create_connection("Coastal Cave", "Church of Dragon Communion")
        
        if self.options.late_dlc == False: # for tp medal
            create_connection("Limgrave", "Mohgwyn Dynasty Mausoleum")
            
        create_connection("Stormhill", "Stormveil Start")
        create_connection("Stormveil Start" "Stormveil Castle")
        create_connection("Stormveil Castle", "Stormveil Throne")
        create_connection("Stormveil Castle", "Divine Tower of Limgrave")
        
        create_connection("Limgrave", "Weeping Peninsula")
        # Weeping Peninsula
        create_connection("Weeping Peninsula", "Impaler's Catacombs")
        create_connection("Weeping Peninsula", "Tombsward Catacombs")
        create_connection("Weeping Peninsula", "Tombsward Cave")
        create_connection("Weeping Peninsula", "Morne Tunnel")
        create_connection("Weeping Peninsula", "Earthbore Cave")
        create_connection("Weeping Peninsula", "Divine Bridge") # in leyndell
        
        create_connection("Limgrave", "Siofra River")
        # Siofra
        
        create_connection("Stormhill", "Liurnia of The Lakes")
        create_connection("Stormveil Throne", "Liurnia of The Lakes")
        # Liurnia of The Lakes
        create_connection("Liurnia of The Lakes", "Bellum Highway")
        create_connection("Liurnia of The Lakes", "Road's End Catacombs")
        create_connection("Liurnia of The Lakes", "Black Knife Catacombs")
        create_connection("Liurnia of The Lakes", "Cliffbottom Catacombs")
        create_connection("Liurnia of The Lakes", "Stillwater Cave")
        create_connection("Liurnia of The Lakes", "Lakeside Crystal Cave")
        create_connection("Liurnia of The Lakes", "Academy Crystal Cave")
        create_connection("Liurnia of The Lakes", "Raya Lucaria Crystal Tunnel")
        create_connection("Liurnia of The Lakes", "Caria Manor")
        create_connection("Liurnia of The Lakes", "Carian Study Hall")
        create_connection("Liurnia of The Lakes", "Carian Study Hall (Inverted)")
        create_connection("Liurnia of The Lakes", "Ruin-Strewn Precipice")
        create_connection("Liurnia of The Lakes", "Ainsel River")
        
        create_connection("Liurnia of The Lakes", "The Four Belfries (Chapel of Anticipation)")
        create_connection("Liurnia of The Lakes", "The Four Belfries (Nokron)")
        create_connection("Liurnia of The Lakes", "The Four Belfries (Farum Azula)")
        
        create_connection("Liurnia of The Lakes", "Raya Lucaria Academy")
        create_connection("Raya Lucaria Academy", "Raya Lucaria Academy Main")
        create_connection("Raya Lucaria Academy Main", "Raya Lucaria Academy Chest")
        create_connection("Raya Lucaria Academy Main", "Raya Lucaria Academy Library")
        
        
        #create_connection("Siofra River", "Caelid") # dont really need this but putting it here
        create_connection("Limgrave", "Caelid")
        # Caelid
        create_connection("Caelid", "Caelid Catacombs")
        create_connection("Caelid", "Gaol Cave")
        create_connection("Caelid", "Sellia, Town of Sorcery")
        create_connection("Caelid", "Sellia Crystal Tunnel")
        create_connection("Caelid", "Abandoned Cave")
        create_connection("Caelid", "Great-Jar")
        create_connection("Caelid", "Minor Erdtree Catacombs")
        create_connection("Caelid", "Gale Tunnel")
        create_connection("Caelid", "Redmane Castle Post Radahn")
        
        create_connection("Caelid", "Dragonbarrow")
        create_connection("Dragonbarrow", "Dragonbarrow Cave")
        create_connection("Dragonbarrow", "Sellia Hideaway")
        create_connection("Dragonbarrow", "Divine Tower of Caelid")
        
        create_connection("Caelid", "Wailing Dunes")
        create_connection("Wailing Dunes", "War-Dead Catacombs")
        
        create_connection("Limgrave", "Nokron, Eternal City Start")
        create_connection("Nokron, Eternal City Start", "Nokron, Eternal City")
        create_connection("Nokron, Eternal City", "Deeproot Depths")
        
        create_connection("Deeproot Depths Start", "Deeproot Depths") # oneway
        #create_connection("Deeproot Depths", "Leyndell, Royal Capital") # idk waygate requirements
        #create_connection("Deeproot Depths", "Deeproot Depths Boss")
        
        create_connection("Deeproot Depths", "Ainsel River Main")
        create_connection("Ainsel River Main", "Lake of Rot")
        create_connection("Lake of Rot", "Lake of Rot Boss")
        create_connection("Lake of Rot Boss", "Moonlight Altar")
        
        create_connection("Ruin-Strewn Precipice", "Altus Plateau")
        create_connection("Liurnia of The Lakes", "Altus Plateau")
        # Altus
        create_connection("Altus Plateau", "Sainted Hero's Grave")
        create_connection("Altus Plateau", "Unsightly Catacombs")
        create_connection("Altus Plateau", "Perfumer's Grotto")
        create_connection("Altus Plateau", "Sage's Cave")
        create_connection("Altus Plateau", "Old Altus Tunnel")
        create_connection("Altus Plateau", "Altus Tunnel")
        
        
        #create_connection("Altus Plateau", "Mount Gelmir")
        # Mt Gelmir
        #create_connection("Mount Gelmir", "Wyndham Catacombs")
        #create_connection("Mount Gelmir", "Gelmir Hero's Grave")
        #create_connection("Mount Gelmir", "Seethewater Cave")
        #create_connection("Mount Gelmir", "Volcano Cave")
        
        #create_connection("Mount Gelmir", "Volcano Manor Entrance")
        create_connection("Volcano Manor Entrance", "Volcano Manor Drawing Room")
        create_connection("Volcano Manor Drawing Room", "Volcano Manor")
        create_connection("Volcano Manor", "Volcano Manor Upper")
        
        
        
        
        create_connection("Altus Plateau", "Capital Outskirts")
        # Capital Outskirts
        create_connection("Capital Outskirts", "Auriza Hero's Grave")
        create_connection("Capital Outskirts", "Auriza Side Tomb")
        create_connection("Capital Outskirts", "Sealed Tunnel")
        

        # Leyndell Royal
        #create_connection("Divine Bridge", "Leyndell, Royal Capital")
        #create_connection("Leyndell, Royal Capital","")
        
        # Leyndell Ashen
        #create_connection("Divine Bridge", "Leyndell, Ashen Capital")
        #create_connection("Leyndell, Ashen Capital","")
        
        #create_connection("Leyndell, Royal Capital", "Subterranean Shunning-Grounds")
        create_connection("Subterranean Shunning-Grounds", "Leyndell Catacombs")
        #create_connection("Subterranean Shunning-Grounds", "FFP")
        #create_connection("FFP", "Deeproot Depths Start")
        
        
        #create_connection("Leyndell, Royal Capital", "Forbidden Lands")
        # Forbidden Lands
        #create_connection("Forbidden Lands", "Hidden Path to the Haligtree")
        
        
        #create_connection("Forbidden Lands", "Mountaintops of the Giants")
        # Mountaintops
        #create_connection("Mountaintops of the Giants", "Giant-Conquering Hero's Grave")
        #create_connection("Mountaintops of the Giants", "Giants' Mountaintop Catacombs")
        #create_connection("Mountaintops of the Giants", "Spiritcaller Cave")
        
        
        #create_connection("Hidden Path to the Haligtree", "Consecrated Snowfield")
        # Snowfield
        #create_connection("Consecrated Snowfield", "Consecrated Snowfield Catacombs")
        #create_connection("Consecrated Snowfield", "Cave of the Forlorn")
        #create_connection("Consecrated Snowfield", "Yelough Anix Tunnel")

        #create_connection("Consecrated Snowfield", "Miquella's Haligtree")
        # Haligtree
        create_connection("Miquella's Haligtree", "Elphael, Brace of the Haligtree")
        
        #create_connection("Consecrated Snowfield", "Mohgwyn Palace")
        
        #create_connection("farum", "Leyndell, Ashen Capital")
        create_connection("Leyndell, Ashen Capital", "Leyndell, Ashen Capital Throne")
        create_connection("Leyndell, Ashen Capital Throne", "Erdtree")

        # Connect DLC Regions
        if self.options.enable_dlc: #WIP
            create_connection("Mohgwyn Palace", "Gravesite Plain")
            create_connection("Gravesite Plain", "Fog Rift Catacombs")
            create_connection("Gravesite Plain", "Belurat Gaol")
            create_connection("Gravesite Plain", "Belurat")
            create_connection("Gravesite Plain", "Castle Ensis")
            create_connection("Gravesite Plain", "Dragon's Pit")
            create_connection("Dragon's Pit", "Jagged Peak")
            create_connection("Jagged Peak", "Charo's Hidden Grave")
            create_connection("Charo's Hidden Grave", "Lamenter's Gaol (Entrance)")
            create_connection("Lamenter's Gaol (Entrance)", "Lamenter's Gaol (Upper)")
            create_connection("Lamenter's Gaol (Upper)", "Lamenter's Gaol (Lower)")
            
            create_connection("Castle Ensis", "Scadu Altus")
            create_connection("Scadu Altus", "Bonny Gaol")
            create_connection("Scadu Altus", "Rauh Base")
            create_connection("Rauh Base", "Scorpion River Catacombs")
            
            create_connection("Scadu Altus", "Ellac River")
            create_connection("Ellac River", "Cerulean Coast")
            create_connection("Cerulean Coast", "Stone Coffin")
            create_connection("Cerulean Coast", "Finger Ruins of Rhia")
            
            create_connection("Scadu Altus", "Shadow Keep")
            create_connection("Shadow Keep", "Hinterland")
            create_connection("Hinterland", "Finger Ruins of Dheo")
            
            create_connection("Shadow Keep", "Rauh Ruins")
            create_connection("Rauh Ruins", "Enir Ilim")
            
            create_connection("Shadow Keep", "Recluses' River")
            create_connection("Recluses' River", "Darklight Catacombs")
            create_connection("Darklight Catacombs", "Abyssal Woods")
            create_connection("Abyssal Woods", "Midra's Manse")
        

    # For each region, add the associated locations retrieved from the corresponding location_table
    def create_region(self, region_name, location_table) -> Region:
        new_region = Region(region_name, self.player, self.multiworld)

        # Use this to un-exclude event locations so the fill doesn't complain about items behind
        # them being unreachable.
        excluded = self.options.exclude_locations.value

        for location in location_table:
            if self._is_location_available(location):
                new_location = ERLocation(self.player, location, new_region)
                
                # set priority before excluded so that progression items dont go into excluded locations
                if location.name in self.all_priority_locations:
                    new_location.progress_type = LocationProgressType.PRIORITY
                    
                if (
                    # Exclude missable locations that don't allow useful items
                    location.missable and self.options.missable_location_behavior == "randomize_unimportant"
                    and not (
                        # Unless they are excluded to a higher degree already
                        location.name in self.all_excluded_locations
                        and self.options.missable_location_behavior < self.options.excluded_location_behavior
                    )
                    # always disable randomizing progression into missable if host disables
                    or self.settings.disable_extreme_options and location.missable
                ):
                    new_location.progress_type = LocationProgressType.EXCLUDED
            else:
                # Replace non-randomized items with events that give the default item
                event_item = (
                    self.create_item(location.default_item_name) if location.default_item_name
                    else ERItem.event(location.name, self.player)
                )

                new_location = ERLocation(
                    self.player,
                    location,
                    parent = new_region,
                    event = True,
                )
                event_item.code = None
                new_location.place_locked_item(event_item)
                if location.name in excluded:
                    excluded.remove(location.name)
                    # Only remove from all_excluded if excluded does not have priority over missable
                    if not (self.options.missable_location_behavior < self.options.excluded_location_behavior):
                        self.all_excluded_locations.remove(location.name)

            new_region.locations.append(new_location)

        self.multiworld.regions.append(new_region)
        self.created_regions.add(region_name)
        return new_region
    
    def create_items(self) -> None:
        # Just used to efficiently deduplicate items
        item_set: Set[str] = set()

        # Gather all default items on randomized locations
        self.local_itempool = []
        num_required_extra_items = 0
        for location in cast(List[ERLocation], self.multiworld.get_unfilled_locations(self.player)):
            if not self._is_location_available(location.name):
                raise Exception("ER generation bug: Added an unavailable location.")

            default_item_name = cast(str, location.data.default_item_name)
            item = item_table[default_item_name]
            if item.skip:
                num_required_extra_items += 1
            else:
                # For unique items, make sure there aren't duplicates in the item set even if there
                # are multiple in-game locations that provide them.
                if default_item_name in item_set:
                    num_required_extra_items += 1
                else:
                    item_set.add(default_item_name)
                    self.local_itempool.append(self.create_item(default_item_name))

        injectables = self._create_injectable_items(num_required_extra_items)
        num_required_extra_items -= len(injectables)
        self.local_itempool.extend(injectables)

        # Extra filler items for locations containing skip items
        self.local_itempool.extend(self.create_item(self.get_filler_item_name()) for _ in range(num_required_extra_items))

        # Potentially fill some items locally and remove them from the itempool
        self._fill_local_items()

        # Add items to itempool
        self.multiworld.itempool += self.local_itempool

    def _create_injectable_items(self, num_required_extra_items: int) -> List[ERItem]:
        """Returns a list of items to inject into the multiworld instead of skipped items.

        If there isn't enough room to inject all the necessary progression items
        that are in missable locations by default, this adds them to the
        player's starting inventory.
        """
        if self.options.enable_dlc: # the work around
            all_injectable_items = [
                item for item
                in item_table.values()
            ]
        else:
            all_injectable_items = [
                item for item
                in item_table_vanilla.values()
            ]
        injectable_mandatory = [
            item for item in all_injectable_items
            if item.classification == ItemClassification.progression
        ]
        injectable_optional = [
            item for item in all_injectable_items
            if item.classification != ItemClassification.progression
        ]

        number_to_inject = min(num_required_extra_items, len(all_injectable_items))
        items = (
            self.random.sample(
                injectable_mandatory,
                k=min(len(injectable_mandatory), number_to_inject)
            )
            + self.random.sample(
                injectable_optional,
                k=max(0, number_to_inject - len(injectable_mandatory))
            )
        )

        if number_to_inject < len(injectable_mandatory):
            # It's worth considering the possibility of _removing_ unimportant
            # items from the pool to inject these instead rather than just
            # making them part of the starting health pack
            for item in injectable_mandatory:
                if item in items: continue
                self.multiworld.push_precollected(self.create_item(item))
                warning(
                    f"Couldn't add \"{item.name}\" to the item pool for " + 
                    f"{self.player_name}. Adding it to the starting " +
                    f"inventory instead."
                )

        return [self.create_item(item) for item in items]

    def _fill_local_items(self) -> None:
        """Removes certain items from the item pool and manually places them in the local world.

        We can't do this in pre_fill because the itempool may not be modified after create_items.
        """
        # if self.yhorm_location.name == "Iudex Gundyr":
        #     self._fill_local_item("Storm Ruler", ["Cemetery of Ash"],
        #                           lambda location: location.name != "CA: Coiled Sword - boss drop")         

    def _fill_local_item(
        self, name: str,
        regions: List[str],
        additional_condition: Optional[Callable[[ERLocationData], bool]] = None,
    ) -> None:
        """Chooses a valid location for the item with the given name and places it there.
        
        This always chooses a local location among the given regions. If additional_condition is
        passed, only locations meeting that condition will be considered.

        If the item could not be placed, it will be added to starting inventory.
        """
        item = next((item for item in self.local_itempool if item.name == name), None)
        if not item: return

        candidate_locations = [
            location for location in (
                self.multiworld.get_location(location.name, self.player)
                for region in regions
                for location in location_tables[region]
                if self._is_location_available(location)
                and not location.missable
                and not location.conditional
                and (not additional_condition or additional_condition(location))
            )
            # We can't use location.progress_type here because it's not set
            # until after `set_rules()` runs.
            if not location.item and location.name not in self.all_excluded_locations
            and location.item_rule(item)
        ]

        self.local_itempool.remove(item)

        if not candidate_locations:
            warning(f"Couldn't place \"{name}\" in a valid location for {self.player_name}. Adding it to starting inventory instead.")
            location = next(
                (location for location in self._get_our_locations() if location.data.default_item_name == item.name),
                None
            )
            if location: self._replace_with_filler(location)
            self.multiworld.push_precollected(self.create_item(name))
            return

        location = self.random.choice(candidate_locations)
        location.place_locked_item(item)

    def create_item(self, item: Union[str, ERItemData]) -> ERItem:
        data = item if isinstance(item, ERItemData) else item_table[item]
        return ERItem(self.player, data)

    def _replace_with_filler(self, location: ERLocation) -> None:
        """If possible, choose a filler item to replace location's current contents with."""
        if location.locked: return

        # Try 10 filler items. If none of them work, give up and leave it as-is.
        for _ in range(0, 10):
            candidate = self.create_filler()
            if location.item_rule(candidate):
                location.item = candidate
                return

    def get_filler_item_name(self) -> str:
        if self.options.enable_dlc:
            return self.random.choice(filler_item_names)
        else:
            return self.random.choice(filler_item_names_vanilla)

    def set_rules(self) -> None: #MARK: Rules

        self._key_rules()
        self._dragon_communion_rules()
        self._add_shop_rules()
        self._add_npc_rules()
        #self._add_remembrance_rules() # need to do the locations first
        #self._add_equipment_of_champions_rules() # need to do the locations first

        # World Logic
        if self.options.world_logic == "region_lock": 
            self._region_lock_items()
            if self.options.soft_logic:
                self._add_entrance_rule("Caelid", lambda state: state.can_reach("Altus Plateau"))
                self._add_entrance_rule("Dragonbarrow", lambda state: state.can_reach("Forbidden Lands") and state.has("Rold Medallion", self.player))
                
            #self._add_entrance_rule("Weeping Peninsula", lambda state: "region key")
            self._add_location_rule([ # stuff in WP but not
                "WP/(DHFR): Arteria Leaf x2 - within N ruins",
                "WP/DHFR: Gold-Tinged Excrement x2 - SE of DHFR",
                "WP/DHFR: String x5 - SE of DHFR",
                "WP/EC: Rainbow Stone - SE of EC",
                "WP/FLT: Golden Rune [1] x3 1 - E of FLT",
                "WP/FLT: Golden Rune [1] x3 2 - E of FLT",
                "WP/CP: Sliver of Meat - lower cliff NW of CP",
                "WP/CP: Bewitching Branch x3 - lower cliff NW of CP",
                "WP/CP: Warhawk Ashes - \"Prophecy\" Painting reward to N",
            ], lambda state: state.can_reach("Weeping Peninsula"))
            "BS: Stonesword Key - behind wooden platform" 
            "BS: Smithing Stone [1] x3 - corpse hanging off edge" # on Bridge of Sacrifice idk where wall for WP will be
            
            #self._add_entrance_rule(["Stormveil Start", "Stormveil Castle"], lambda state: "region key")
            self._add_location_rule([ # stuff in SV but not
                "SV: Talisman Pouch - boss drop",
            ], lambda state: state.can_reach("Stormveil Start"))
    
            #self._add_entrance_rule("Liurnia of The Lakes", lambda state: "region key")
            self._add_entrance_rule("Altus Plateau", lambda state: # only in region lock since it can be bypassed by ruin-strewn precipice
                state.has("Dectus Medallion (Left)", self.player) and
                state.has("Dectus Medallion (Right)", self.player))
            
            #self._add_entrance_rule(["Caelid", "Sellia Crystal Tunnel"], lambda state: "region key")
            
            self._add_location_rule([ # stuff in CL but not
                "CL/(SC): Missionary's Cookbook [3] - on corpse",
                "CL/(SC): Sacred Scorpion Charm - invader drop",
                "CL/RB: Golden Rune [1] - graveyard to SW",
                "CL/RB: Golden Rune [2] - graveyard to SW",
                "CL/RB: Golden Rune [3] - graveyard to SW",
                "CL/RB: Nascent Butterfly x2 - to E",
                "CL/RB: Golden Rune [3] - in stable to N",
                "CL/RB: Preserving Boluses x5 - in shack to SW",
                "CL/RB: Drawstring Lightning Grease x2 - to W",
                "CL/MEW: Rune Arc - W of MEW high on root",
            ], lambda state: state.can_reach("Caelid"))
            
        elif self.options.world_logic == "open_world":
            self._add_entrance_rule("Leyndell, Royal Capital", lambda state: self._has_enough_great_runes(state, self.options.great_runes_required))
        #else: # glitch logic
            #idk any just that leyndell can be done early i think

        # Paintings
        self._add_location_rule("LG/SR: Incantation Scarab - \"Homing Instinct\" Painting reward to NW", 
                                lambda state: state.has("\"Homing Instinct\" Painting", self.player))
        self._add_location_rule("CL/MEE: Ash of War: Rain of Arrows - \"Redmane\" Painting reward down hidden cliff E of MEE", 
                                lambda state: state.has("\"Redmane\" Painting", self.player))
        self._add_location_rule("WP/CP: Warhawk Ashes - \"Prophecy\" Painting reward to N", 
                                lambda state: state.has("\"Prophecy\" Painting", self.player))
        
        # Imbued Keys
        self._add_entrance_rule([
            "The Four Belfries (Chapel of Anticipation)",
            "The Four Belfries (Nokron)",
            "The Four Belfries (Farum Azula)"], 
            lambda state: state.has("Imbued Sword Key", self.player, count=3))
        
        # Other Rules
        
        if self.options.enemy_rando == False: # funny shackle rule
            self._add_entrance_rule("Stormveil Castle", lambda state: state.has("Margit's Shackle", self.player))
            self._add_entrance_rule("Mohgwyn Palace", lambda state: state.has("Mohg's Shackle", self.player))
        
        # Vanilla Rules
        
        # you can kill gostoc and not open main gate
        self._add_entrance_rule("Stormveil Castle", lambda state: state.has("Rusty Key", self.player))
        self._add_entrance_rule("Raya Lucaria Academy", lambda state: state.has("Academy Glintstone Key", self.player))
        self._add_location_rule([ # stuff in RLA but not
                "RLA/MAG: Strip of White Flesh x2 - down SE ramp before gate",
                "RLA/MAG: Celestial Dew - down SE ramp by gate",
            ], lambda state: state.can_reach("Raya Lucaria Academy"))
        
        self._add_entrance_rule("Carian Study Hall (Inverted)", 
            lambda state: state.has("Carian Inverted Statue", self.player))
        
        # festival // altus grace touch or ranni quest stuff
        self._add_location_rule([
            "CL/(RC): Smithing Stone [6] - in church during festival",
        ], lambda state: state.can_reach("Altus Plateau"))
        self._add_entrance_rule("Wailing Dunes", lambda state: state.can_reach("Altus Plateau"))
        
        self._add_entrance_rule("Nokron, Eternal City Start", lambda state: self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop"))
           
        self._add_entrance_rule("Moonlight Altar", lambda state: state.has("Dark Moon Ring", self.player))
        
        # ashen capital only after getting farum boss Remembrance
        
        
        self._add_entrance_rule("Hidden Path to the Haligtree", lambda state: 
            state.has("Haligtree Secret Medallion (Left)", self.player) and
            state.has("Haligtree Secret Medallion (Right)", self.player))
        
        # Smithing bell bearing rules
        if self.options.smithing_bell_bearing_option.value == 1: # wip not all places have names
            self._add_entrance_rule("Altus Plateau", lambda state: state.has("Smithing-Stone Miner's Bell Bearing [1]", self.player))
            self._add_entrance_rule("Capital Outskirts", lambda state: state.has("Smithing-Stone Miner's Bell Bearing [2]", self.player))
            self._add_entrance_rule("motg_flamepeak", lambda state: state.has("Smithing-Stone Miner's Bell Bearing [3]", self.player))
            self._add_entrance_rule("farumazula_main", lambda state: state.has("Smithing-Stone Miner's Bell Bearing [4]", self.player))
            
            self._add_entrance_rule("Dragonbarrow", lambda state: state.has("Somberstone Miner's Bell Bearing [1]", self.player))
            self._add_entrance_rule("Capital Outskirts", lambda state: state.has("Somberstone Miner's Bell Bearing [2]", self.player))
            self._add_entrance_rule("motg_flamepeak", lambda state: state.has("Somberstone Miner's Bell Bearing [3]", self.player))
            self._add_entrance_rule("farumazula_main", lambda state: state.has("Somberstone Miner's Bell Bearing [4]", self.player))
            self._add_entrance_rule("Leyndell, Ashen Capital", lambda state: state.has("Somberstone Miner's Bell Bearing [5]", self.player))
        
        # DLC Access Rules Below
        if self.options.enable_dlc:
            if self.options.late_dlc:
                self._add_entrance_rule("Gravesite Plain",
                    lambda state: state.has("Rold Medallion", self.player)
                    and state.has("Haligtree Secret Medallion (Left)", self.player)
                    and state.has("Haligtree Secret Medallion (Right)", self.player)
                    and self._can_get(state, "MP/(MDM): Remembrance of the Blood Lord - mainboss drop")
                    and self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop"))
            else:
                self._add_entrance_rule("Mohgwyn Palace", # can get to normal way or funny medal
                    lambda state: state.has("Pureblood Knight's Medal", self.player) or state.can_reach("Consecrated Snowfield"))
                self._add_entrance_rule("Gravesite Plain", 
                    lambda state: self._can_get(state, "MP/(MDM): Remembrance of the Blood Lord - mainboss drop")
                    and self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop"))
                
            # the funny gaol
            self._add_entrance_rule("Lamenter's Gaol (Upper)", lambda state: state.has("Gaol Upper Level Key", self.player))
            self._add_entrance_rule("Lamenter's Gaol (Lower)", lambda state: state.has("Gaol Lower Level Key", self.player))
                    
        
        if self.options.ending_condition <= 1:
            if self.options.enable_dlc and self.options.ending_condition == 0:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "EI: Remembrance of a God and a Lord - mainboss drop")
                # "EI: Circlet of Light - Acquired by interacting with the memory after defeating Promised Consort Radahn" # real end
            else:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "ET: Elden Remembrance - mainboss drop")
                # make this the mend the elden ring event, idk how todo that rn       
        elif self.options.ending_condition == 2:
            self.multiworld.completion_condition[self.player] = [ lambda state: 
                self._can_get(state, "SV/SC: Remembrance of the Grafted - mainboss drop")
                and self._can_get(state, "RLA: Remembrance of the Full Moon Queen - mainboss drop")
                and self._can_get(state, "CL/(WD): Remembrance of the Starscourge - mainboss drop")
                and self._can_get(state, "NR/(HG): Remembrance of the Regal Ancestor - boss drop")
                and self._can_get(state, "VM/AP: Remembrance of the Blasphemous - mainboss drop")
                and self._can_get(state, "LRC/QB: Remembrance of the Omen King - mainboss drop")
                and self._can_get(state, "LR: Remembrance of the Naturalborn - mainboss drop")
                and self._can_get(state, "MP/(MDM): Remembrance of the Blood Lord - mainboss drop")
                and self._can_get(state, "FA/BGB: Remembrance of the Dragonlord - alt mainboss drop")
                # i think this is missable   and self._can_get(state, "DD/AR: Remembrance of the Lichdragon - mainboss drop")
                and self._can_get(state, "EBH/HR: Remembrance of the Rot Goddess - mainboss drop")
                and self._can_get(state, "MotG/FF: Remembrance of the Fire Giant - mainboss drop")
                and self._can_get(state, "FA/BGB: Remembrance of the Black Blade - mainboss drop")
                and self._can_get(state, "LAC/QB: Remembrance of Hoarah Loux - mainboss drop")
                and self._can_get(state, "ET: Elden Remembrance - mainboss drop")
            ]
            if self.options.enable_dlc:
                self.multiworld.completion_condition[self.player] += [ lambda state: 
                    self._can_get(state, "BTS/SF: Remembrance of the Dancing Lion - mainboss drop")
                    and self._can_get(state, "CE/CLC: Remembrance of the Twin Moon Knight - mainboss drop")
                    and self._can_get(state, "SK/DCE: Remembrance of the Impaler - mainboss drop")
                    and self._can_get(state, "STB/TWS: Remembrance of the Shadow Sunflower - mainboss drop")
                    and self._can_get(state, "SV/SKBG: Remembrance of the Wild Boar Rider - mainboss drop")
                    and self._can_get(state, "SCF/FD: Remembrance of Putrescence - mainboss drop")
                    and self._can_get(state, "MM/SFC: Remembrance of the Lord of Frenzied Flame - mainboss drop")
                    and self._can_get(state, "FRM/CMM: Remembrance of the Mother of Fingers - mainboss drop")
                    and self._can_get(state, "ARR/CBME: Remembrance of the Saint of the Bud - mainboss drop")
                    and self._can_get(state, "JP/JPS: Heart of Bayle - mainboss drop")
                    and self._can_get(state, "EI: Remembrance of a God and a Lord - mainboss drop")
                ]
        # else:
        #     # all bosses # need one check from each boss :skull:
        #     if self.options.enable_dlc:
            
    
    def _region_lock_items(self) -> None:
        """All region lock items set to not be skipped when doing region lock."""
        # MARK: Region Lock Items
        item_table["Region Lock Key"].skip = False
        
    def _key_rules(self) -> None:
        # MARK: SSK RULES
        # this needs to be fixed, the order needs to be the sphere order, and idk how todo that
        # in order from early game to late game each rule needs to include the last count for an area
        currentKey = 0 #makes dynamic
        
        # limgrave
        currentKey += 3
        self._add_entrance_rule("Fringefolk Hero's Grave", lambda state: self._has_enough_keys(state, currentKey)) # 2
        self._add_location_rule("LG/(SWV): Green Turtle Talisman - behind imp statue", lambda state: self._has_enough_keys(state, currentKey)) # 1
        
        # roundtable
        currentKey += 3
        self._add_location_rule([
            "RH: Crepus's Black-Key Crossbow - behind imp statue in chest", "RH: Black-Key Bolt x20 - behind imp statue in chest", # 1
            "RH: Assassin's Prayerbook - behind second imp statue in chest", # 2
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # weeping
        currentKey += 2
        self._add_location_rule([
            "WP/(TCC): Nomadic Warrior's Cookbook [9] - behind imp statue", # 1
            "WP/(WE): Radagon's Scarseal - boss drop Evergaol", # 1
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # stormveil
        currentKey += 2
        self._add_location_rule([
            "SV/LC: Godslayer's Seal - left chest behind imp statue in storeroom SE of massive courtyard", # 1a
            "SV/LC: Godskin Prayerbook - right chest behind imp statue in storeroom SE of massive courtyard", # 1a
            "SV/RT: Iron Whetblade - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            "SV/RT: Hawk Crest Wooden Shield - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            "SV/RT: Miséricorde - shortcut elevator to SE, to N through door, behind imp statue", # 1b
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # siofra
        currentKey += 2
        # for leaving siofra to caelid ravine
        self._add_location_rule([
            "CL/DSW: Spiked Palisade Shield - to W follow ravine",
            "CL/DSW: Stonesword Key - to S",
            "CL/CCO: Great-Jar's Arsenal - beat Great Jar's knights",
            ], lambda state: self._has_enough_keys(state, currentKey) and 
            state.can_reach("Caelid") and state.can_reach("Siofra River")) # 2
        
        # liurnia
        currentKey += 4
        self._add_location_rule([
            "LL/(BKC): Rosus' Axe - behind imp statue near boss door", # 1a
            "LL/(CC): Nox Mirrorhelm - behind imp statue, in SW corner", # 1b
            ], lambda state: self._has_enough_keys(state, currentKey))
        self._add_entrance_rule("Academy Crystal Cave", lambda state: self._has_enough_keys(state, currentKey)) # 2
        
        # altus
        currentKey += 2 #wip
        self._add_location_rule([
            "AP/(SHG): Crimson Seed Talisman - behind imp statue", # 1a
            "AP/(SHG): Dragoncrest Shield Talisman +1 - ride up first cleaver, behind imp statue", # 1b
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # caelid
        currentKey += 3
        self._add_entrance_rule("Gaol Cave", lambda state: self._has_enough_keys(state, currentKey)) # 2
        self._add_location_rule("CL/(FR): Sword of St. Trina - chest underground behind imp statue", 
                                lambda state: self._has_enough_keys(state, currentKey)) # 1
        
        # nokron
        currentKey += 1
        self._add_location_rule([
            "NR/(NSG): Mimic Tear Ashes - in chest behind imp statue upper interior", # 1a
            "NR/(NSG): Smithing Stone [3] - behind imp statue upper interior", # 1a
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # mt gelmir
        currentKey += 1 #wip
        self._add_location_rule([
            "MG/(WC): Lightning Scorpion Charm - behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # capital outskirts
        currentKey += 1 #wip
        self._add_location_rule([
            "CO/(AHG): Golden Epitaph - behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # nokstella
        currentKey += 1
        self._add_location_rule([
            "NS/NEC: Nightmaiden & Swordstress Puppets - in chest behind imp statue to W up stairs, left before bridge", # 1
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # moonlight altar
        currentKey += 1
        self._add_location_rule([
            "MA/(LER): Cerulean Amber Medallion +2 - in chest under illusory floor behind imp statue", # 1
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # mountaintops
        currentKey += 2 #wip
        self._add_location_rule([
            "MG/(GCHG): Flame, Protect Me - behind imp statue", # 1a
            "MG/(GCHG): Cranial Vessel Candlestand - upper room after fire spitter, behind imp statue", # 1b
            ], lambda state: self._has_enough_keys(state, currentKey))
        
        # haligtree +3
        currentKey += 3
        self._add_location_rule([
            "BH/PR: Triple Rings of Light - exit PR then drop to E, behind imp statue", # 1
            "BH/PR: Marika's Soreseal - behind imp statue at the S end of the bottom area", # 2
            ], lambda state: self._has_enough_keys(state, currentKey))
        
    def _dragon_communion_rules(self) -> None:
        """Rules for dragon communion"""
        # MARK: dragon RULES
        currentHeart = 3 # limgrave dragon communion
        self._add_location_rule([
            "LG/(CDC): Dragonfire - Dragon Communion", # 1
            "LG/(CDC): Dragonclaw - Dragon Communion", # 1
            "LG/(CDC): Dragonmaw - Dragon Communion", # 1
            ], lambda state: self._has_enough_hearts(state, currentHeart)) 
        
        # caelid dragon communion
        currentHeart += 10 # always here + LG and CL boss ones
        self._add_location_rule([
            "CL/(CDC): Glintstone Breath - Dragon Communion", # 1
            "CL/(CDC): Rotten Breath - Dragon Communion", # 1
            "CL/(CDC): Dragonice - Dragon Communion", # 1
            "CL/(CDC): Agheel's Flame - Dragon Communion, kill boss in LG, NW of DBR", # 2
            "CL/(CDC): Greyoll's Roar - Dragon Communion, kill enemy in CL, W of FF", # 3
            "CL/(CDC): Ekzykes's Decay - Dragon Communion, kill boss to NW of here", # 2
            ], lambda state: self._has_enough_hearts(state, currentHeart)) 
        
        currentHeart += 2
        self._add_location_rule("CL/(CDC): Smarag's Glintstone Breath - Dragon Communion, kill boss in LL, SW of ACC", 
            lambda state: self._has_enough_hearts(state, currentHeart) and state.can_reach("Liurnia of The Lakes")) # 2
        currentHeart += 1
        self._add_location_rule("CL/(CDC): Magma Breath - Dragon Communion, kill boss in MtG, S of FL", 
            lambda state: self._has_enough_hearts(state, currentHeart) and state.can_reach("Mount Gelmir")) # 1
        currentHeart += 2
        self._add_location_rule("CL/(CDC): Borealis's Mist - Dragon Communion, kill boss in MotG, N of FCM", 
            lambda state: self._has_enough_hearts(state, currentHeart) and state.can_reach("Mountaintops of the Giants")) # 2
        currentHeart += 2
        self._add_location_rule("CL/(CDC): Theodorix's Magma - Dragon Communion, kill boss in CS, SE of CF", 
            lambda state: self._has_enough_hearts(state, currentHeart) and state.can_reach("Consecrated Snowfield")) # 2
        
        if(self.options.enable_dlc): # dlc
            currentHeart += 3
            self._add_location_rule("JP/GADC: Ghostflame Breath - Grand Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 3
    
    def _has_enough_great_runes(self, state: CollectionState, runes_required: int) -> bool:
        """Returns whether the given state has enough great runes."""
        runeCount = 0
        if state.has("Godrick's Great Rune", self.player): runeCount += 1
        if state.has("Rykard's Great Rune", self.player): runeCount += 1
        if state.has("Radahn's Great Rune", self.player): runeCount += 1
        if state.has("Morgott's Great Rune", self.player): runeCount += 1
        if state.has("Mohg's Great Rune", self.player): runeCount += 1
        if state.has("Malenia's Great Rune", self.player): runeCount += 1
        if state.has("Great Rune of the Unborn", self.player): runeCount += 1
        return runes_required >= runeCount
    
    def _has_enough_keys(self, state: CollectionState, req_keys: int) -> bool:
        """Returns whether the given state has enough keys."""
        total_keys = state.count("Stonesword Key", self.player) + (state.count("Stonesword Key x3", self.player) * 3) + (state.count("Stonesword Key x5", self.player) * 5)
        return total_keys >= req_keys
    
    def _has_enough_hearts(self, state: CollectionState, req_hearts: int) -> bool:
        """Returns whether the given state has enough keys."""
        total_hearts = state.count("Dragon Heart", self.player) + (state.count("Dragon Heart x3", self.player) * 3) + (state.count("Dragon Heart x5", self.player) * 5)
        return total_hearts >= req_hearts
    
    def _add_shop_rules(self) -> None: # needs bell bearing rules for husks if the items aren't inf
        """Adds rules for items unlocked in shops."""

        # Scrolls
        scrolls = {
            "Academy Scroll": ["Great Glintstone Shard", "Swift Glintstone Shard"],
            "Conspectus Scroll": ["Glintstone Cometshard", "Star Shower"],
            "Royal House Scroll": ["Glintblade Phalanx", "Carian Slicer"]
        }

        # Prayerbooks
        books = {
            "Two Fingers' Prayerbook": ["Lord's Heal", "Lord's Aid"],
            "Assassin's Prayerbook": ["Assassin's Approach", "Darkness"],
            "Golden Order Principia": ["Radagon's Rings of Light", "Law of Regression"],
            "Dragon Cult Prayerbook": ["Lightning Spear", "Honed Bolt", "Electrify Armament"],
            "Ancient Dragon Prayerbook": ["Ancient Dragons' Lightning Spear", "Ancient Dragons' Lightning Strike"],
            "Fire Monks' Prayerbook": ["O, Flame!", "Surge, O Flame!"],
            "Giant's Prayerbook": ["Giantsflame Take Thee", "Flame, Fall Upon Them"],
            "Godskin Prayerbook": ["Black Flame", "Black Flame Blade"]
        }

        for (scroll, items) in scrolls.items():
            self._add_location_rule([f"LG/(WR): {item} - {scroll}" for item in items], lambda state: state.has(scroll, self.player))
        for (book, items) in books.items():
            self._add_location_rule([f"RH: {item} - {book}" for item in items], lambda state: state.has(book, self.player))        
                
    def _add_npc_rules(self) -> None:
        """Adds rules for items accessible via NPC quests.

        We list missable locations here even though they never contain progression items so that the
        game knows what sphere they're in.

        Generally, for locations that can be accessed early by killing NPCs, we set up requirements
        assuming the player _doesn't_ so they aren't forced to start killing allies to advance the
        quest.
        """
        # MARK: Edgar
        self._add_location_rule([ "WP/BS: Banished Knight's Halberd - kill Edgar at Irina's body or at LL/RS",
        ], lambda state: ( state.can_reach("Liurnia of The Lakes")))
        
        # MARK: Roderika
        self._add_location_rule([ 
            "LG/(SS): Golden Seed - give Roderika Chrysalids' Memento then talk to her at RH, or after SV mainboss item is at SS",
            "SV/RT: Crimson Hood - shortcut elevator to SE, to SE under dead troll, after Roderika becomes a spirit tuner",
        ], lambda state: (state.has("Chrysalids' Memento", self.player)))
        
        # MARK: Ensha
        self._add_location_rule([
            "RH: Clinging Bone - dropped by Ensha, after getting half of secret medallion",
            "RH: Royal Remains Helm - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Armor - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Gauntlets - Ensha's spot, after getting half of secret medallion",
            "RH: Royal Remains Greaves - Ensha's spot, after getting half of secret medallion"
        ], lambda state: (state.has("Haligtree Secret Medallion (Left)", self.player) or
                          state.has("Haligtree Secret Medallion (Right)", self.player)))
        
        
        # MARK: Enia
        self._add_location_rule([ "RH: Talisman Pouch - Enia at 2 great runes or Twin Maiden after farum boss",
        ], lambda state: ( self._has_enough_great_runes(state, 2)))
        
        # MARK: Latenna
        # need to see if armour is missable
        # talk to her with secret medallion right, get ashes        *do you need to talk to albus first or just have item*
        # after take her to apostate derelict in con snow, get mega somber
        self._add_location_rule([ "LL/(SWS): Latenna the Albinauric - talk to Latenna with Haligtree Secret Medallion (Right)",
        ], lambda state: ( state.has("Haligtree Secret Medallion (Right)", self.player)))
        
        # MARK: D
        self._add_location_rule([
            "RH: Litany of Proper Death - D shop, after talking to Gurraq",
            "RH: Order's Blade - D shop, after talking to Gurraq",
        ], lambda state: ( state.can_reach("Dragonbarrow")))
        
        # MARK: D, Twin
        # WIP IDK IF THE WHOLE SET IS NEEDED, OR A SINGLE PIECE
        self._add_location_rule(["DD/AR: Inseparable Sword - kill D Twin at NEC if you killed D, or at end of Fia quest", 
        ], lambda state: ( 
            (state.has("Twinned Helm", self.player) or state.has("Twinned Armor", self.player)
            or state.has("Twinned Gauntlets", self.player) or state.has("Twinned Greaves", self.player))
            and self._can_get(state, "RH: Twinned Helm - on D's body after giving him Weather Dagger during Fia's quest")))
        
        # MARK: Rogier
        self._add_location_rule(["RH: Rogier's Letter - after giving Black Knifeprint, talk to Ranni, talk to Rogier again", 
        ], lambda state: ( state.can_reach("Stormveil Castle") and state.can_reach("Liurnia of The Lakes")
                          and state.has("Black Knifeprint", self.player)))
        
        self._add_location_rule([
            "RH: Spellblade's Pointed Hat - found on Rogier's body",
            "RH: Spellblade's Traveling Attire - found on Rogier's body",
            "RH: Spellblade's Gloves - found on Rogier's body",
            "RH: Spellblade's Trousers - found on Rogier's body",
            "RH: Rogier's Rapier +8 - talk Rogier after beating SV mainboss or on his body after he dies"
        ], lambda state: ( state.can_reach("Stormveil Castle") and state.has("Cursemark of Death", self.player)))
        
        # MARK: Fia
        self._add_location_rule(["RH: Knifeprint Clue - talk to Fia multiple times", 
        ], lambda state: ( state.can_reach("Stormveil Castle")))
        
        self._add_location_rule(["RH: Sacrificial Twig - talk to Fia after giving Black Knifeprint to Rogier", 
        ], lambda state: ( state.has("Black Knifeprint", self.player) and state.can_reach("Stormveil Castle")))
        
        self._add_location_rule(["RH: Weathered Dagger - talk to Fia after reaching altus", 
        ], lambda state: ( state.can_reach("Altus Plateau")))
        
        self._add_location_rule([
            "RH: Twinned Helm - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Armor - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Gauntlets - on D's body after giving him Weather Dagger during Fia's quest",
            "RH: Twinned Greaves - on D's body after giving him Weather Dagger during Fia's quest"
        ], lambda state: ( state.has("Weathered Dagger", self.player) and state.can_reach("Altus Plateau")))
        
        # MARK: Dung Eater
        self._add_location_rule(["RH: Sewer-Gaol Key - talk to Dung Eater while having a Seedbed Curse", 
        ], lambda state: ( state.has("Seedbed Curse", self.player)))
        
        
        # MARK: Nepheli
        # i jumped into her and she died, lol
        # dropped 2 axes
        "SV/SC: Arsenal Charm - talk to Nepheli before and after defeating SV mainboss" # same area so no rule
        "SV/LL: Ancient Dragon Smithing Stone - Gostoc shop after finishing Nepheli and Kenneth Haight's quests"
        "SV/LL: Ancient Dragon Smithing Stone - talk to Nepheli in SV after her and Kenneth's questlines"
        
        # MARK: Thops
        "LL/(CI): Ash of War: Thops's Barrier - scarab in church after Thops moves"
        "LL/(CT): Memory Stone - top of tower, requires Erudition gesture" # you get the gesture from thops normally
        
        # MARK: Gurraq
        self._add_location_rule([
            "CL/(BS): Clawmark Seal - Gurranq, deathroot reward 1",
            "CL/(BS): Beast Eye - Gurranq, deathroot reward 1 or kill",
        ], lambda state: ( state.has("Deathroot", self.player)))
        
        self._add_location_rule([ "CL/(BS): Bestial Sling - Gurranq, deathroot reward 2",
        ], lambda state: ( state.has("Deathroot", self.player, count=2)))
        
        self._add_location_rule(["CL/(BS): Bestial Vitality - Gurranq, deathroot reward 3",
        ], lambda state: ( state.has("Deathroot", self.player, count=3)))
        
        self._add_location_rule(["CL/(BS): Ash of War: Beast's Roar - Gurranq, deathroot reward 4",
        ], lambda state: ( state.has("Deathroot", self.player, count=4)))
        
        # MARK: Gowry
        self._add_location_rule([ 
            "CL/(GS): Sellia's Secret - talk to Gowry with needle",
            "CL/(GS): Unalloyed Gold Needle (Fixed) - talk to Gowry after giving needle",
        ], lambda state: ( state.has("Unalloyed Gold Needle (Broken)", self.player)))
        
        self._add_location_rule([
            "CL/(GS): Glintstone Stars - Gowry Shop",
            "CL/(GS): Night Shard - Gowry Shop",
            "CL/(GS): Night Maiden's Mist - Gowry Shop",
        ], lambda state: ( self._can_get(state, "CL/(CP): Prosthesis-Wearer Heirloom - give Millicent fixed needle")))
        
        self._add_location_rule(["CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent",
        ], lambda state: ( state.has("Valkyrie's Prosthesis", self.player) and state.can_reach("Altus Plateau")
                          and self._can_get(state, "CL/(GS): Night Shard - Gowry Shop")))
        
        self._add_location_rule(["CL/(GS): Desperate Prayer - buy 4th shop item",
        ], lambda state: ( self._can_get(state, "CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent")))
        
        self._add_location_rule(["CL/(GS): Flock's Canvas Talisman - kill Gowry or complete questline",
        ], lambda state: ( self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")))
        
        # MARK: Millicent
        self._add_location_rule(["CL/(CP): Prosthesis-Wearer Heirloom - give Millicent fixed needle",
        ], lambda state: ( state.has("Unalloyed Gold Needle (Fixed)", self.player)))
        
        self._add_location_rule([
            "EBH/EIW: Rotten Winged Sword Insignia - help Millicent",
            "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area",
            "EBH/EIW: Millicent's Prosthesis - invade Millicent or kill in altus",
        ], lambda state: ( self._can_get(state, "CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent")))
        
        self._add_location_rule([
            "EBH/HR: Miquella's Needle - use needle on flower in boss arena after Millicent quest",
            "EBH/HR: Somber Ancient Dragon Smithing Stone - use needle on flower in boss arena after Millicent quest",
        ], lambda state: ( 
            self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")
            and state.has("Unalloyed Gold Needle (Milicent)", self.player)
        ))
        
        # MARK: Rya        
        self._add_location_rule(["LL/SI: Volcano Manor Invitation - give Rya her necklace or reach altus", 
        ], lambda state: ( state.can_reach("Altus Plateau")))
        
        # MARK: Patches 
        
        
        
        # end of quest
        """self._add_location_rule(["LG/(MCV): Glass Shard x3 - Patches chest, after you've given the Dancer's Castanets to Tanith",
        ], lambda state: ( 
            self._can_get(state, "kill the volcano manor mainboss") 
            and state.has("Dancer's Castanets", self.player)
        ))"""
        
        # MARK: Iji
        "LL/RM: Iji's Mirrorhelm - kill Iji or after quest"
        
        # MARK: Ranni
        
        self._add_location_rule([
            "LG/(CE): Spirit Calling Bell - talk to Ranni",
            "LG/(CE): Lone Wolf Ashes - talk to Ranni",
        ], lambda state: ( self._can_get(state, "talk to ranni in her tower, item in rth") )) #finish
        
        self._add_location_rule([
            "NR/(NSG): Fingerslayer Blade - in chest lower area, talk to Ranni in LL",
            "NR/(NSG): Great Ghost Glovewort - in chest lower area, talk to Ranni in LL"
        ], lambda state: ( state.can_reach("Liurnia of the Lakes")))
        
        self._add_location_rule([
            "LL/(ReR): Snow Witch Hat - in chest, after giving Fingerslayer Blade to Ranni",
            "LL/(ReR): Snow Witch Robe - in chest, after giving Fingerslayer Blade to Ranni",
            "LL/(ReR): Snow Witch Skirt - in chest, after giving Fingerslayer Blade to Ranni"
        ], lambda state: ( state.has("Fingerslayer Blade", self.player) and state.can_reach("Nokron, Eternal City")))
        
        self._add_location_rule(["RLA/RLGL: Dark Moon Ring - in chest, requires Discarded Palace Key",
        ], lambda state: ( state.has("Discarded Palace Key", self.player)))
        
        "MA/(CMC): Dark Moon Greatsword - talk to Ranni under CMC" # MA requires the ring to enter, but this check requires nothing
        
        if self.options.enable_dlc: # MARK: DLC NPC
            
            
            "guh"   
            
    def _add_remembrance_rules(self) -> None:
        """Adds rules for items obtainable for trading remembrances."""

        remembrances = [
            (
                "Remembrance of the Grafted",
                ["Axe of Godrick", "Grafted Dragon"]
            ),
            (
                "Remembrance of the Full Moon Queen",
                ["Carian Regal Scepter", "Rennala's Full Moon"]
            ),
            (
                "Remembrance of the Starscourge",
                ["Starscourge Greatsword", "Lion Greatbow"]
            ),
            (
                "Remembrance of the Regal Ancestor",
                ["Winged Greathorn", "Ancestral Spirit's Horn"]
            ),
            (
                "Remembrance of the Omen King",
                ["Morgott's Cursed Sword", "Regal Omen Bairn"]
            ),
            (
                "Remembrance of the Naturalborn",
                ["Ash of War: Waves of Darkness", "Bastard's Stars"]
            ),
            (
                "Remembrance of the Blasphemous",
                ["Rykard's Rancor", "Blasphemous Blade"]
            ),
            (
                "Remembrance of the Lichdragon",
                ["Fortissax's Lightning Spear", "Death Lightning"]
            ),
            (
                "Remembrance of the Fire Giant",
                ["Giant's Red Braid", "Burn, O Flame!"]
            ),
            (
                "Remembrance of the Blood Lord",
                ["Mohgwyn's Sacred Spear", "Bloodboon"]
            ),
            (
                "Remembrance of the Black Blade",
                ["Maliketh's Black Blade", "Black Blade"]
            ),
            (
                "Remembrance of the Dragonlord",
                ["Dragon King's Cragblade", "Placidusax's Ruin"]
            ),
            (
                "Remembrance of Hoarah Loux",
                ["Axe of Godfrey", "Ash of War: Hoarah Loux's Earthshaker"]
            ),
            (
                "Remembrance of the Rot Goddess",
                ["Hand of Malenia", "Scarlet Aeonia"]
            ),
            (
                "Elden Remembrance",
                ["Marika's Hammer", "Sacred Relic Sword"]
            ),
        ]

        dlc_remembrances = [
            (
                "Remembrance of the Dancing Lion",
                ["Enraged Divine Beast", "Ash of War: Divine Beast Frost Stomp"]
            ),
            (
                "Remembrance of the Twin Moon Knight",
                ["Rellana's Twin Blades", "Rellana's Twin Moons"]
            ),
            (
                "Remembrance of Putrescence",
                ["Putrescence Cleaver", "Vortex of Putrescence"]
            ),
            (
                "Remembrance of the Wild Boar Rider",
                ["Sword Lance", "Blades of Stone"]
            ),
            (
                "Remembrance of the Shadow Sunflower",
                ["Shadow Sunflower Blossom", "Land of Shadow"]
            ),
            (
                "Remembrance of the Impaler",
                ["Spear of the Impaler", "Messmer's Orb"]
            ),
            (
                "Remembrance of the Saint of the Bud",
                ["Poleblade of the Bud", "Rotten Butterflies"]
            ),
            (
                "Remembrance of the Mother of Fingers",
                ["Staff of the Great Beyond", "Gazing Finger"]
            ),
            (
                "Remembrance of the Lord of Frenzied Flame",
                ["Greatsword of Damnation", "Midra's Flame of Frenzy"]
            ),
            (
                "Remembrance of a God and a Lord",
                ["Greatsword of Radahn (Lord)", "Greatsword of Radahn (Light)", "Light of Miquella"]
            ),
        ]
            
        if self.options.enable_dlc:
            remembrances += dlc_remembrances
            self._add_location_rule("JP/GADC: Bayle's Flame Lightning - Heart of Bayle", 
                                    lambda state: (state.has("Heart of Bayle", self.player) and state.can_reach("Jagged Peak")))
            self._add_location_rule("JP/GADC: Bayle's Tyranny - Heart of Bayle", 
                                    lambda state: (state.has("Heart of Bayle", self.player) and state.can_reach("Jagged Peak")))

        for (remembrance, items) in remembrances:
            self._add_location_rule([
                f"RH: {item} - Enia for {remembrance}" for item in items
            ], lambda state, r=remembrance: (state.has(r, self.player) and self._has_enough_great_runes(state, 1)
            ))
    
    def _add_equipment_of_champions_rules(self) -> None: # wip needs dlc checks
        """Adds rules for items obtainable from equipment of champions."""

        equipments = [ # done
            ( # RA mainboss
                "RLA mainboss", #"Rennala, Queen of the Full Moon", # boss
                "RLA: Remembrance of the Full Moon Queen - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Queen's Crescent Crown", 
                    "Queen's Robe",
                    "Queen's Leggings", 
                    "Queen's Bracelets"
                ]
            ),
            ( # MH mainboss
                "EBH/HR mainboss", #"Malenia Blade of Miquella", # boss
                "EBH/HR: Remembrance of the Rot Goddess - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Malenia's Winged Helm", 
                    "Malenia's Armor",
                    "Malenia's Gauntlet", 
                    "Malenia's Greaves"
                ]
            ),
            ( # LAC mainboss
                "LAC/QB mainboss", #"Godfrey, First Elden Lord", # boss
                "LAC/QB: Remembrance of Hoarah Loux - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Elden Lord Crown", 
                    "Elden Lord Armor",
                    "Elden Lord Bracers", 
                    "Elden Lord Greaves"
                ]
            ),
            ( # TSC boss
                "TSC/SCIG boss", #"Elemer of the Briar", # boss
                "TSC/SCIG: Briar Greatshield - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Briar Helm", 
                    "Briar Armor",
                    "Briar Gauntlets", 
                    "Briar Greaves"
                ]
            ),
            ( # MH boss
                "MH/HTP boss", #"Loretta, Knight of the Haligtree", # boss
                "MH/HTP: Loretta's Mastery - boss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Royal Knight Helm", 
                    "Royal Knight Armor",
                    "Royal Knight Gauntlet", 
                    "Royal Knight Greaves"
                ]
            ),
            ( # FA mainboss
                "FA/BGB mainboss", #"Maliketh, the Black Blade", # boss
                "FA/BGB: Remembrance of the Black Blade - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Maliketh's Helm", 
                    "Maliketh's Armor",
                    "Maliketh's Gauntlets", 
                    "Maliketh's Greaves"
                ]
            ),
            ( # MotG/(CS) mainboss
                "MotG/(CS) mainboss", #"Commander Niall", # boss
                "MotG/(CS): Veteran's Prosthesis - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Veteran's Helm", 
                    "Veteran's Armor",
                    "Veteran's Gauntlets", 
                    "Veteran's Greaves"
                ]
            ),
            ( # WD mainboss
                "CL/(WD) mainboss", #"Starscourge Radahn", # boss
                "CL/(WD): Remembrance of the Starscourge - mainboss drop", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Radahn's Redmane Helm", 
                    "Radahn's Lion Armor",
                    "Radahn's Gauntlets", 
                    "Radahn's Greaves"
                ]
            ),
            ( # LRC mainboss
                "LRC/QB mainboss", #"Morgott, The Omen King", # boss
                "LRC/QB: Remembrance of the Omen King - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Fell Omen Cloak"]# item
            ),
            ( # MP mainboss
                "MP/(MDM) mainboss" # "Mohg, Lord of Blood", # boss
                "MP/(MDM): Remembrance of the Blood Lord - mainboss drop", # a drop from boss, so we can do 'can get' check
                ["Lord of Blood's Robe"]# item
            ),
        ]

        dlc_equipments = [
            (
                "", #"Messmer the Impaler", # boss
                "", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Messmer's Helm", 
                    "Messmer's Armor",
                    "Messmer's Gauntlets", 
                    "Messmer's Greaves"
                ]
            ),
            (
                "", #"Rellana, Twin Moon Knight", # boss
                "", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Rellana's Helm", 
                    "Rellana's Armor",
                    "Rellana's Gloves", 
                    "Rellana's Greaves"
                ]
            ),
            (
                "", #"Commander Gaius", # boss
                "", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Gaius's Helm", 
                    "Gaius's Armor",
                    "Gaius's Gauntlets", 
                    "Gaius's Greaves"
                ]
            ),
            ( # you cant even get this till the game is beat LMAO
                "", #"Promised Consort Radahn", # boss
                "", # a drop from boss, so we can do 'can get' check
                [   # items
                    "Young Lion's Helm", 
                    "Young Lion's Armor",
                    "Young Lion's Gauntlets", 
                    "Young Lion's Greaves"
                ]
            ),
        ]
            
        if self.options.enable_dlc:
            equipments += dlc_equipments

        for (boss, boss_location, items) in equipments:
            self._add_location_rule([
                f"RH: {item} - Enia shop, defeat {boss}" for item in items
            ], lambda state: self._can_get(boss_location, self.player) and self._has_enough_great_runes(state, 1))
            
    def _add_location_rule(self, location: Union[str, List[str]], rule: Union[CollectionRule, str]) -> None:
        """Sets a rule for the given location if it that location is randomized.

        The rule can just be a single item/event name as well as an explicit rule lambda.
        """
        locations = location if isinstance(location, list) else [location]
        for location in locations:
            data = location_dictionary[location]
            if data.dlc and not self.options.enable_dlc: continue

            if not self._is_location_available(location): continue
            if isinstance(rule, str):
                assert item_table[rule].classification == ItemClassification.progression
                rule = lambda state, item=rule: state.has(item, self.player)
            add_rule(self.multiworld.get_location(location, self.player), rule)
    
    def _add_entrance_rule(self, region: str, rule: Union[CollectionRule, str]) -> None:
        """Sets a rule for the entrance to the given region."""
        assert region in location_tables
        if region not in self.created_regions: return
        if isinstance(rule, str):
            if " -> " not in rule:
                assert item_table[rule].classification == ItemClassification.progression
            rule = lambda state, item=rule: state.has(item, self.player)
        add_rule(self.multiworld.get_entrance("Go To " + region, self.player), rule)

    def _add_item_rule(self, location: str, rule: ItemRule) -> None:
        """Sets a rule for what items are allowed in a given location."""
        if not self._is_location_available(location): return
        add_item_rule(self.multiworld.get_location(location, self.player), rule)

    def _can_go_to(self, state, region) -> bool:
        """Returns whether state can access the given region name."""
        return state.can_reach_entrance(f"Go To {region}", self.player)

    def _can_get(self, state, location) -> bool:
        """Returns whether state can access the given location name."""
        return state.can_reach_location(location, self.player)
    
    def _is_location_available(
        self,
        location: Union[str, ERLocationData, ERLocation]
    ) -> bool:
        """Returns whether the given location is being randomized."""
        if isinstance(location, ERLocationData):
            data = location
        elif isinstance(location, ERLocation):
            data = location.data
        else:
            data = location_dictionary[location]
        
        # dont random smithing bell bearing
        if data.smithingbell and self.options.smithing_bell_bearing_option.value == 2:
            return False

        return (
            not data.is_event
            and (not data.dlc or bool(self.options.enable_dlc))
            and not (
                self.options.excluded_location_behavior == "do_not_randomize"
                and data.name in self.all_excluded_locations
            )
            and not (
                self.options.missable_location_behavior == "do_not_randomize"
                and data.missable
            )
        )
    
    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        text = ""

        if self.options.excluded_location_behavior == "randomize_unimportant":
            text += f"\n{self.player_name}'s world excluded: {sorted(self.all_excluded_locations)}\n"

        if text:
            text = "\n" + text + "\n"
            spoiler_handle.write(text)

    def _shuffle(self, seq: Sequence) -> List:
        """Returns a shuffled copy of a sequence."""
        copy = list(seq)
        self.random.shuffle(copy)
        return copy

    def _pop_item(
        self,
        location: Location,
        items: List[ERItem]
    ) -> ERItem:
        """Returns the next item in items that can be assigned to location."""
        for i, item in enumerate(items):
            if location.can_fill(self.multiworld.state, item, False):
                return items.pop(i)

        # If we can't find a suitable item, give up and assign an unsuitable one.
        return items.pop(0)

    def _get_our_locations(self) -> List[ERLocation]:
        return cast(List[ERLocation], self.multiworld.get_locations(self.player))
    
    def fill_slot_data(self) -> Dict[str, object]:
        slot_data: Dict[str, object] = {}

        # Once all clients support overlapping item IDs, adjust the ER AP item IDs to encode the
        # in-game ID as well as the count so that we don't need to send this information at all.
        #
        # We include all the items the game knows about so that users can manually request items
        # that aren't randomized, and then we _also_ include all the items that are placed in
        # practice.
        items_by_name = {
            location.item.name: cast(ERItem, location.item).data
            for location in self.multiworld.get_filled_locations()
            # item.code None is used for events, which we want to skip
            if location.item.code is not None and location.item.player == self.player
        }
        for item in item_table.values():
            if item.name not in items_by_name:
                items_by_name[item.name] = item

        ap_ids_to_er_ids: Dict[str, int] = {}
        item_counts: Dict[str, int] = {}
        for item in items_by_name.values():
            if item.ap_code is None: continue
            if item.er_code: ap_ids_to_er_ids[str(item.ap_code)] = item.er_code
            if item.count != 1: item_counts[str(item.ap_code)] = item.count

        # A map from Archipelago's location IDs to the keys the static randomizer uses to identify
        # locations.
        location_ids_to_keys: Dict[int, str] = {}
        for location in cast(List[ERLocation], self.multiworld.get_filled_locations(self.player)):
            # Skip events and only look at this world's locations
            if (location.address is not None and location.item.code is not None
                    and location.data.static):
                location_ids_to_keys[location.address] = location.data.static

        slot_data = {
            "options": {
                "ending_condition": self.options.ending_condition.value,
                "world_logic": self.options.world_logic.value,
                "soft_logic": self.options.soft_logic.value,
                "great_runes_required": self.options.great_runes_required.value,
                "enable_dlc": self.options.enable_dlc.value,
                "late_dlc": self.options.late_dlc.value,
                "enemy_rando": self.options.enemy_rando.value,
                "material_rando": self.options.material_rando.value,
                "death_link": self.options.death_link.value,
                "random_start": self.options.random_start.value,
                "auto_equip": self.options.auto_equip.value,
                "smithing_bell_bearing_option": self.options.smithing_bell_bearing_option.value,
                "local_item_option": self.options.local_item_option.value,
                "exclude_local_item_only": self.options.exclude_local_item_only.value,
                "important_locations": self.options.important_locations.value,
                "exclude_locations": self.options.exclude_locations.value,
                "excluded_location_behavior": self.options.excluded_location_behavior.value,
                "missable_location_behavior": self.options.missable_location_behavior.value,
            },
            "seed": self.multiworld.seed_name,  # to verify the server's multiworld
            "slot": self.multiworld.player_name[self.player],  # to connect to server
            "apIdsToItemIds": ap_ids_to_er_ids,
            "itemCounts": item_counts,
            "locationIdsToKeys": location_ids_to_keys,
        }

        return slot_data

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return slot_data