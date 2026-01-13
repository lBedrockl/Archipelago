from test.bases import WorldTestBase

from worlds.eldenring.items import item_table
from worlds.eldenring.locations import location_tables

class EldenRingTest(WorldTestBase):
    game = "EldenRing"
    options = {
        "world_logic": 1
    }
    def testLocationDefaultItems(self):
        for locations in location_tables.values():
            for location in locations:
                if location.default_item_name:
                    self.assertIn(location.default_item_name, item_table)

    def testLocationsUnique(self):
        names = set()
        for locations in location_tables.values():
            for location in locations:
                self.assertNotIn(location.name, names)
                names.add(location.name)

# class TestAccess(WorldTestBase):
#     game = "EldenRing"
#     options = {
#         "world_logic": 1
#     }
#     def testEnia(self) -> None:
#         """test enia remembrances"""
#         remembrances = [
#             (
#                 "Remembrance of the Grafted",
#                 ["Axe of Godrick", "Grafted Dragon"]
#             ),
#             (
#                 "Remembrance of the Full Moon Queen", 
#                 ["Carian Regal Scepter", "Rennala's Full Moon"]
#             ),
#             (
#                 "Remembrance of the Starscourge",
#                 ["Starscourge Greatsword", "Lion Greatbow"]
#             ),
#             (
#                 "Remembrance of the Regal Ancestor",
#                 ["Winged Greathorn", "Ancestral Spirit's Horn"]
#             ),
#             (
#                 "Remembrance of the Omen King",
#                 ["Morgott's Cursed Sword", "Regal Omen Bairn"]
#             ),
#             (
#                 "Remembrance of the Naturalborn",
#                 ["Ash of War: Waves of Darkness", "Bastard's Stars"]
#             ),
#             (
#                 "Remembrance of the Blasphemous",
#                 ["Rykard's Rancor", "Blasphemous Blade"]
#             ),
#             (
#                 "Remembrance of the Lichdragon",
#                 ["Fortissax's Lightning Spear", "Death Lightning"]
#             ),
#             (
#                 "Remembrance of the Fire Giant",
#                 ["Giant's Red Braid", "Burn, O Flame!"]
#             ),
#             (
#                 "Remembrance of the Blood Lord",
#                 ["Mohgwyn's Sacred Spear", "Bloodboon"]
#             ),
#             (
#                 "Remembrance of the Black Blade",
#                 ["Maliketh's Black Blade", "Black Blade"]
#             ),
#             (
#                 "Remembrance of the Dragonlord",
#                 ["Dragon King's Cragblade", "Placidusax's Ruin"]
#             ),
#             (
#                 "Remembrance of Hoarah Loux",
#                 ["Axe of Godfrey", "Ash of War: Hoarah Loux's Earthshaker"]
#             ),
#             (
#                 "Remembrance of the Rot Goddess",
#                 ["Hand of Malenia", "Scarlet Aeonia"]
#             ),
#             (
#                 "Elden Remembrance",
#                 ["Marika's Hammer", "Sacred Relic Sword"]
#             ),
#         ]
#         for (remembrance, items) in remembrances:
#             location = [f"RH: {item} - Enia for {remembrance}" for item in items]
#             have_items = [[remembrance]]
#             self.assertAccessDependency(location, have_items)

#pytest worlds/eldenring/tests   