from collections.abc import Sequence
from collections import defaultdict
import json
from logging import warning
from typing import cast, Any, Callable, Dict, Set, List, Optional, TextIO, Union

from BaseClasses import CollectionState, MultiWorld, Region, Location, LocationProgressType, Entrance, Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import CollectionRule, ItemRule, add_rule, add_item_rule

from .items import ERItem, ERItemData, filler_item_names, filler_item_names_vanilla, item_descriptions, item_table, item_table_vanilla, item_name_groups
from .locations import ERLocation, ERLocationData, location_tables, location_descriptions, location_dictionary, location_name_groups, region_order, region_order_dlc
from .options import EROptions, option_groups

#Web stuff
class EldenRingWeb(WebWorld):
    rich_text_options_doc = True
    theme = "stone"
    option_groups = option_groups
    item_descriptions = item_descriptions

#Main World
class EldenRing(World):
    """
    This is the description of the game that will be displayed on the AP website.
    """

    game = "EldenRing"
    options: EROptions
    options_dataclass = EROptions
    web = EldenRingWeb()
    base_id = 69000
    required_client_version = (0, 4, 2) # tbh idk what version is needed
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

    def generate_early(self) -> None:
        self.created_regions = set()
        self.all_excluded_locations.update(self.options.exclude_locations.value)

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
        self.multiworld.get_entrance("New Game", self.player).connect(regions["Chapel of Anticipation"])
        
        create_connection("Limgrave", "Miquella's Haligtree") #TEMP TO MAKE GAME WORK
        
        # Start 
        create_connection("Chapel of Anticipation", "Stranded Graveyard")
        # Limgrave
        create_connection("Stranded Graveyard", "Limgrave")
        create_connection("Stranded Graveyard", "Fringefolk Hero's Grave")
        
        create_connection("Limgrave", "Church of Elleh")
        create_connection("Limgrave", "Coastal Cave")
        create_connection("Limgrave", "Groveside Cave")
        create_connection("Limgrave", "Stormfoot Catacombs")
        create_connection("Limgrave", "Gatefront Ruins")
        create_connection("Limgrave", "Limgrave Tunnels")
        create_connection("Limgrave", "Stormgate")
        create_connection("Limgrave", "Stormhill Shack")
        create_connection("Limgrave", "Waypoint Ruins")
        create_connection("Limgrave", "Dragon-Burnt Ruins")
        create_connection("Limgrave", "Murkwater Cave")
        create_connection("Limgrave", "Mistwood Ruins")
        create_connection("Limgrave", "Fort Haight")
        create_connection("Limgrave", "Third Church of Marika")
        create_connection("Limgrave", "LG Artist's Shack")
        create_connection("Limgrave", "Summonwater Village")
        create_connection("Limgrave", "Murkwater Catacombs")
        create_connection("Limgrave", "Highroad Cave")
        create_connection("Limgrave", "Deathtouched Catacombs")
        create_connection("Limgrave", "Warmaster's Shack")

        create_connection("Limgrave", "Roundtable Hold")
        
        create_connection("Dragon-Burnt Ruins", "Sellia Crystal Tunnel")
        create_connection("Coastal Cave", "Church of Dragon Communion")

        #create_connection("Limgrave", "Stormveil Castle")
        #create_connection("Limgrave", "Siofra River")
        
        
        create_connection("Limgrave", "Bridge of Sacrifice")
        # Weeping Peninsula
        create_connection("Bridge of Sacrifice", "Weeping Peninsula")
        create_connection("Weeping Peninsula", "Impaler's Catacombs")
        create_connection("Weeping Peninsula", "Church of Pilgrimage")
        create_connection("Weeping Peninsula", "Tombsward Catacombs")
        create_connection("Weeping Peninsula", "Tombsward Cave")
        create_connection("Weeping Peninsula", "Isolated Merchant's Shack")
        create_connection("Weeping Peninsula", "Morne Tunnel")
        create_connection("Weeping Peninsula", "Earthbore Cave")

        create_connection("Weeping Peninsula", "Castle Morne")
        create_connection("Weeping Peninsula", "Divine Bridge") # in leyndell
        

        create_connection("Limgrave", "Liurnia of The Lakes")
        #create_connection("Stormveil Castle", "Liurnia of The Lakes")
        # Liurnia of The Lakes
        create_connection("Liurnia of The Lakes", "Chapel of Anticipation [Return]") # add real LL location for ca return
        
        create_connection("Limgrave", "Caelid")
        # Caelid
        create_connection("Caelid", "Smoldering Church")
        create_connection("Caelid", "Bestial Sanctum")
        create_connection("Caelid", "Dragonbarrow Cave")
        create_connection("Caelid", "Fort Faroth")
        create_connection("Caelid", "Sellia Hideaway")
        create_connection("Caelid", "Cathedral of Dragon Communion")
        create_connection("Caelid", "Caelid Catacombs")
        create_connection("Caelid", "Caelid Waypoint Ruins")
        create_connection("Caelid", "Gaol Cave")
        create_connection("Caelid", "Fort Gael")
        create_connection("Caelid", "Street of Sages Ruins")
        create_connection("Caelid", "Sellia, Town of Sorcery")
        create_connection("Caelid", "Gowry's Shack")
        create_connection("Caelid", "Sellia Crystal Tunnel")
        create_connection("Caelid", "Abandoned Cave")
        create_connection("Caelid", "Isolated Merchant's Shack")
        
        create_connection("Caelid", "Redmane Castle")

        # Leyndell Royal
        create_connection("Divine Bridge", "Leyndell, Royal Capital")
        #create_connection("Leyndell, Royal Capital","")
        
        # Leyndell Ashen
        create_connection("Divine Bridge", "Leyndell, Ashen Capital")
        #create_connection("Leyndell, Ashen Capital","")

        #create_connection("Consecrated Snowfield", "Miquella's Haligtree")
        # Haligtree
        create_connection("Miquella's Haligtree", "Elphael, Brace of the Haligtree")



        # Connect DLC Regions
        #if self.options.enable_dlc:
            #create_connection("Mohgwyn Palace", "Gravesite Plain")
        

    # For each region, add the associated locations retrieved from the corresponding location_table
    def create_region(self, region_name, location_table) -> Region:
        new_region = Region(region_name, self.player, self.multiworld)

        # Use this to un-exclude event locations so the fill doesn't complain about items behind
        # them being unreachable.
        excluded = self.options.exclude_locations.value

        for location in location_table:
            if self._is_location_available(location):
                new_location = ERLocation(self.player, location, new_region)
                if (
                    # Exclude missable locations that don't allow useful items
                    location.missable and self.options.missable_location_behavior == "randomize_unimportant"
                    and not (
                        # Unless they are excluded to a higher degree already
                        location.name in self.all_excluded_locations
                        and self.options.missable_location_behavior < self.options.excluded_location_behavior
                    )
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

        # World Logic
        if self.options.world_logic == "region_lock": 
            self._add_entrance_rule("Weeping Peninsula", lambda state: self._has_enough_great_runes(state, 1))
            self._add_entrance_rule("Liurnia of The Lakes", lambda state: self._has_enough_great_runes(state, 2))
            self._add_entrance_rule("Caelid", "Sellia Crystal Tunnel", lambda state: self._has_enough_great_runes(state, 3))
        elif self.options.world_logic == "open_world":
            self._add_entrance_rule("Leyndell, Royal Capital", lambda state: self._has_enough_great_runes(state, self.options.great_runes_required))
        #else: # glitch logic
            #idk any just that leyndell can be done early i think

        # Paintings
        self._add_location_rule("LG/SR: Incantation Scarab - \"Homing Instinct\" Painting reward to NW", 
                                lambda state: state.has("\"Homing Instinct\" Painting", self.player))
        self._add_location_rule("CL/MEE: Ash of War: Rain of Arrows - \"Redmane\" Painting reward down hidden cliff E of MEE", 
                                lambda state: state.has("\"Redmane\" Painting", self.player))
        
        # festival // altus grace touch or ranni quest stuff
        self._add_location_rule("CL/(RC): Smithing Stone [6] - in church during festival", 
                                lambda state: state.can_reach("Altus Plateau"))
        
        
        # ashen capital only after getting farum boss Remembrance
        
        # DLC Access Rules Below
        if self.options.enable_dlc:
            if self.options.late_dlc:
                self._add_entrance_rule("Gravesite Plain",
                    lambda state: state.has("Rold Medallion", self.player)
                    and state.has("Haligtree Secret Medallion (Left)", self.player)
                    and state.has("Haligtree Secret Medallion (Right)", self.player)
                    and self._can_get(state, "MP: Mohg Remembrance - boss drop")
                    and self._can_get(state, "CL/dune place: Radahn Remembrance - boss drop"))
            else:
                # makes Pureblood Knight's Medal progression only when late dlc is off, idk if this works
                item_table["Pureblood Knight's Medal"].classification = ItemClassification.progression
                self._add_entrance_rule("Gravesite Plain", 
                    lambda state: self._can_get(state, "MP: Mohg Remembrance - boss drop")
                    and self._can_get(state, "CL/dune place: Radahn Remembrance - boss drop"))
      
        
        """if self.options.ending_condition == 0:
            if self.options.enable_dlc:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "LAC: Elden Beast Remembrance - boss drop")
            else:
                self.multiworld.completion_condition[self.player] = lambda state: self._can_get(state, "EI: Consort Radahn Remembrance - boss drop")
        elif self.options.ending_condition == 1:
            # all remembrances
            if self.options.enable_dlc:
            else:
        else:
            # all bosses
            if self.options.enable_dlc:
            else:"""
            
        
    #MARK: Special Rules
    def _key_rules(self) -> None:
        # MARK: SSK RULES
        # in order from early game to late game each rule needs to include the last count for an area
        currentKey = 0 #makes dynamic
        # limgrave +3
        currentKey += 3
        self._add_entrance_rule("Fringefolk Hero's Grave", lambda state: self._has_enough_keys(state, currentKey)) # 2
        self._add_location_rule("LG/(SWV): Green Turtle Talisman - behind imp statue", lambda state: self._has_enough_keys(state, currentKey)) # 1
        
        # roundtable +3
        currentKey += 3
        self._add_location_rule("RH: Crepus's Black-Key Crossbow - behind imp statue in chest", lambda state: self._has_enough_keys(state, currentKey)) # 1
        self._add_location_rule("RH: Black-Key Bolt x20 - behind imp statue in chest", lambda state: self._has_enough_keys(state, currentKey)) # with above
        self._add_location_rule("RH: Assassin's Prayerbook - behind second imp statue in chest", lambda state: self._has_enough_keys(state, currentKey)) # 2
        
        # weeping +2
        currentKey += 2
        self._add_location_rule("WP/(TCC): Nomadic Warrior's Cookbook [9] - behind imp statue" , lambda state: self._has_enough_keys(state, currentKey)) # 1
        self._add_location_rule("WP/(WE): Radagon's Scarseal - Weeping Evergaol" , lambda state: self._has_enough_keys(state, currentKey)) # 1
        
        # stormveil +2
        #currentKey += 2
        
        # caelid +3
        currentKey += 3
        self._add_entrance_rule("Gaol Cave", lambda state: self._has_enough_keys(state, currentKey)) # 2
        
        
        # haligtree +3
        currentKey += 3
        self._add_location_rule("BH/PR: Triple Rings of Light - exit PR then drop to E, behind imp statue", lambda state: self._has_enough_keys(state, currentKey)) # 1
        self._add_location_rule("BH/PR: Marika's Soreseal - behind imp statue at the S end of the bottom area", lambda state: self._has_enough_keys(state, currentKey)) # 2
        
    def _dragon_communion_rules(self) -> None:
        """Rules for how dragon hearts are used"""
        # MARK: dragon RULES
        currentHeart = 3 # limgrave dragon communion
        self._add_location_rule("LG/(CDC): Dragonfire - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        self._add_location_rule("LG/(CDC): Dragonclaw - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        self._add_location_rule("LG/(CDC): Dragonmaw - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        
        # caelid dragon communion
        currentHeart += 3 # always here
        currentHeart += 7 # limgrave and caelid
        self._add_location_rule("CL/(CDC): Glintstone Breath - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        self._add_location_rule("CL/(CDC): Rotten Breath - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        self._add_location_rule("CL/(CDC): Dragonice - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        
        self._add_location_rule("CL/(CDC): Agheel's Flame - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 2
        self._add_location_rule("CL/(CDC): Greyoll's Roar - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 3
        self._add_location_rule("CL/(CDC): Ekzykes's Decay - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 2
        
        currentHeart += 7 # todo
        self._add_location_rule("CL/(CDC): Magma Breath - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 1
        self._add_location_rule("CL/(CDC): Theodorix's Magma - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 2
        self._add_location_rule("CL/(CDC): Smarag's Glintstone Breath - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 2
        self._add_location_rule("CL/(CDC): Borealis's Mist - Dragon Communion", lambda state: self._has_enough_hearts(state, currentHeart)) # 2

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
        total_keys = state.count("Stonesword Key", self.player) + (state.count("Stonesword Key x3", self.player) * 3)
        return total_keys >= req_keys
    
    def _has_enough_hearts(self, state: CollectionState, req_hearts: int) -> bool:
        """Returns whether the given state has enough keys."""
        total_hearts = state.count("Dragon Heart", self.player) + (state.count("Dragon Heart x5", self.player) * 5)
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
        # D
        self._add_location_rule([
            "RH: Litany of Proper Death - D shop",
            "RH: Order's Blade - D shop",
        ], lambda state: ( state.can_reach("Bestial Sanctum")))
        
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
        
        """self._add_location_rule(["CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent",
        ], lambda state: ( self._can_get(state, "give Millicent val pro in altus")))"""
        
        self._add_location_rule(["CL/(GS): Desperate Prayer - buy 4th shop item",
        ], lambda state: ( self._can_get(state, "CL/(GS): Pest Threads - Gowry Shop after giving Valkyrie's Prosthesis to Millicent")))
        
        self._add_location_rule(["CL/(GS): Flock's Canvas Talisman - kill Gowry or complete questline",
        ], lambda state: ( self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")))
        
        # MARK: Millicent
        self._add_location_rule(["CL/(CP): Prosthesis-Wearer Heirloom - give Millicent fixed needle",
        ], lambda state: ( state.has("Unalloyed Gold Needle (Fixed)", self.player)))
        
        """self._add_location_rule(["give Millicent val pro in altus",
        ], lambda state: ( state.has("Valkyrie's Prosthesis", self.player)))"""
        
        """self._add_location_rule([
            "EBH/EIW: Rotten Winged Sword Insignia - help Millicent",
            "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area",
            "EBH/EIW: Millicent's Prosthesis - invade Millicent or kill in altus",
        ], lambda state: ( self._can_get(state, "give Millicent val pro in altus")))"""
        
        self._add_location_rule([
            "EBH/HR: Miquella's Needle - use needle on flower in boss arena after Millicent quest",
            "EBH/HR: Somber Ancient Dragon Smithing Stone - use needle on flower in boss arena after Millicent quest",
        ], lambda state: ( 
            self._can_get(state, "EBH/EIW: Unalloyed Gold Needle (Milicent) - help Millicent talk then reload area")
            and state.has("Unalloyed Gold Needle (Milicent)", self.player)
        ))    
            
    def _add_remembrance_rules(self) -> None: # done?
        """Adds rules for items obtainable for trading remembrances."""

        remembrances = [
            (
                "Remembrance of the Grafted", "Godrick",
                ["Axe of Godrick", "Grafted Dragon"]
            ),
            (
                "Remembrance of the Full Moon Queen", "Rennala", 
                ["Carian Regal Scepter", "Rennala's Full Moon"]
            ),
            (
                "Remembrance of the Starscourge", "Radahn",
                ["Starscourge Greatsword", "Lion Greatbow"]
            ),
            (
                "Remembrance of the Regal Ancestor", "Regal Ancestor Spirit",
                ["Winged Greathorn", "Ancestral Spirit's Horn"]
            ),
            (
                "Remembrance of the Omen King", "Morgott",
                ["Morgott's Cursed Sword", "Regal Omen Bairn"]
            ),
            (
                "Remembrance of the Naturalborn", "Astel",
                ["Waves of Darkness", "Bastard's Stars"]
            ),
            (
                "Remembrance of the Blasphemous", "Rykard",
                ["Rykard's Rancor", "Blasphemous Blade"]
            ),
            (
                "Remembrance of the Lichdragon", "Lichdragon",
                ["Fortissax's Lightning Spear", "Death Lightning"]
            ),
            (
                "Remembrance of the Fire Giant", "Fire Giant",
                ["Giant's Red Braid", "Burn, O Flame!"]
            ),
            (
                "Remembrance of the Blood Lord", "Mohg",
                ["Mohgwyn's Sacred Spear", "Bloodboon"]
            ),
            (
                "Remembrance of the Black Blade", "Maliketh",
                ["Maliketh's Black Blade", "Black Blade"]
            ),
            (
                "Remembrance of the Dragonlord", "Placidusax",
                ["Dragon King's Cragblade", "Placidusax's Ruin"]
            ),
            (
                "Remembrance of Hoarah Loux", "Hoarah Loux",
                ["Axe of Godfrey", "Hoarah Loux's Earthshaker"]
            ),
            (
                "Remembrance of the Rot Goddess", "Malenia",
                ["Hand of Malenia", "Scarlet Aeonia"]
            ),
            (
                "Elden Remembrance", "Elden Beast",
                ["Marika's Hammer", "Sacred Relic Sword"]
            ),
        ]

        dlc_remembrances = [
            (
                "Remembrance of the Dancing Lion", "Dancing Lion",
                ["Enraged Divine Beast", "Divine Beast Frost Stomp"]
            ),
            (
                "Remembrance of the Twin Moon Knight", "Rellana",
                ["Rellana's Twin Blades", "Rellana's Twin Moons"]
            ),
            (
                "Remembrance of Putrescence", "Putrescent Knight",
                ["Putrescence Cleaver", "Vortex of Putrescence"]
            ),
            (
                "Remembrance of the Wild Boar Rider", "Commander Gaius", 
                ["Sword Lance", "Blades of Stone"]
            ),
            (
                "Remembrance of the Shadow Sunflower", "Scadutree Avatar",
                ["Shadow Sunflower Blossom", "Land of Shadow"]
            ),
            (
                "Remembrance of the Impaler", "Messmer",
                ["Spear of the Impaler", "Messmer's Orb"]
            ),
            (
                "Remembrance of the Saint of the Bud", "Romina",
                ["Poleblade of the Bud", "Rotten Butterflies"]
            ),
            (
                "Remembrance of the Mother of Fingers", "Metyr",
                ["Staff of the Great Beyond", "Gazing Finger"]
            ),
            (
                "Remembrance of the Lord of Frenzied Flame", "Midra",
                ["Greatsword of Damnation", "Midra's Flame of Frenzy"]
            ),
            (
                "Remembrance of a God and a Lord", "Consort Radahn",
                ["Greatsword of Radahn (Lord) + (Light)", "Light of Miquella"]
            ),
        ]
            
        if self.options.enable_dlc:
            remembrances += dlc_remembrances
            self._add_location_rule("GADC: Bayle's Flame Lightning - Alter for Heart of Bayle", 
                                    lambda state: (state.has("Heart of Bayle", self.player) and state.can_reach("Grand Altar of Dragon Communion")))
            self._add_location_rule("GADC: Bayle's Tyranny - Alter for Heart of Bayle", 
                                    lambda state: (state.has("Heart of Bayle", self.player) and state.can_reach("Grand Altar of Dragon Communion")))

        for (remembrance, remembrance_name, items) in remembrances:
            self._add_location_rule([
                f"RH: {item} - Enia for {remembrance_name}" for item in items
            ], lambda state, r=remembrance: (state.has(r, self.player) and self._has_enough_great_runes(state, 1)
            ))
            
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
                "great_runes_required": self.options.great_runes_required.value,
                "enable_dlc": self.options.enable_dlc.value,
                "late_dlc": self.options.late_dlc.value,
                "death_link": self.options.death_link.value,
                "random_start": self.options.random_start.value,
                "auto_equip": self.options.auto_equip.value,
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