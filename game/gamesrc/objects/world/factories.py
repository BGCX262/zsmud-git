from ev import Object, create_object
import random

class ItemFactory(Object):
    """
    Main Item generator.  generates items based on list seeds.
    """

    def at_object_creation(self):
        self.db.gun_weapon_types = [ 'pistol', 'rifle', 'shotgun', 'smg' ]
        self.db.melee_weapon_types = [ 'bladed', 'non-bladed']
        self.db.gun_pistol_names = [ 'Glock 9mm', 'CZ 75', 'P22', 'Springfield 1911', 'P95', 'SR22', 'LC9' ]
        self.db.gun_rifle_names = [ 'AR-15', 'AK-47', 'SKS', '10/22', 'M4', 'M1A', 'M1 Garand', 'M1 Carbine']
        self.db.gun_shotgun_names = [ 'SPAS-12', 'UTS-15', 'KSG', 'Mossberg 500', 'Remington 870' ]
        self.db.gun_smg_names =  [ 'AK74U', 'Uzi', 'Mac 11', 'MP5K', 'MP5', 'Sepctre M4' ]
        self.db.loot_ratings = ['below average', 'fair', 'good', 'excellent']
        self.db.scavenging_items = {'Can of Beans': .08, 'Bag of Rice': .10, 'Metal Scraps': .35, 'Wood Scraps':.35, 'Wood planks':.15, 'Sheet metal': .10, 'Old tire rubber':.40, 
                                    'Old can of Spinach':.12, 'Bottle of Water':.07, 'Old can of Soda': .20, 'Candybar': .20, 'Can of Carrots': .15, 'Can of Green beans': .20,
                                    'Bag of Northern Beans': .30, 'Can of Oranges': .15, 'Can of Pears': .20, 'Can of Peaches': .20, 'Nails and Screws': .30, 'Nuts and Bolts': .40,
                                    'First Aid Kit': .25, 'Pain Reliever': .40 }

   
    def create_lootset(self, number_of_items, loot_rating='below average'):
        loot_set = []

        for x in range(0, number_of_items):
            mix = ['gun', 'melee', 'scavenging']
            c = random.choice(mix)
            if 'gun' in c:
                type = random.choice(self.db.gun_weapon_types)
                if 'pistol' in type:
                    name = random.choice(self.db.gun_pistol_names)
                    dd = (2,6)
                elif 'rifle' in type:
                    name = random.choice(self.db.gun_rifle_names)
                    dd = (2,10)
                elif 'shotgun' in type:
                    name = random.choice(self.db.gun_rifle_names)
                    dd = (3,10)
                elif 'smg' in type:
                    name = random.choice(self.db.gun_smg_names)
                    dd = (3,6)
        

                if 'below average' in loot_rating:
                    prefix = 'Damaged '
                    name = prefix + name
                elif 'fair' in loot_rating:
                    prefix = 'Used'
                    name = prefix + name
                elif 'good' in loot_rating:
                    prefix = 'New'
                    name = prefix + name
                elif 'excellent' in loot_rating:
                    prefix = random.choice(['Amazing', 'Excellent', 'Spectacular'])
                    name = prefix + name
            
                item = create_object("game.gamesrc.objects.world.item.Item", key=name, location=self)
                a = item.db.attributes
                a['damage_dice'] = dd
                a['weapon_type'] = type
                a['item_slot'] = 'weapon'
                a['equipable'] = True
                item.db.type = c
                item.db.attributes = a
            elif 'scavenging' in c:
                rn = random.random()
                first_pass_choices = {}
                second_pass_choices = []
                for i in self.db.scavenging_items:
                    if self.db.scavenging_items[i] >= rn:
                        first_pass_choices['%s' % i] = self.db.scavenging_items[i]
                
                rn = random.random()        
                for i in first_pass_choices:
                    if first_pass_choices[i] >= rn:
                       second_pass_choices.append(i)
                itemname = random.choice(second_pass_choices)
                item = create_object("game.gamesrc.objects.world.item.Item", key=itemname, location=self)
                a = item.db.attributes
                item.db.type = c
                a['equipable'] = False
                a['consumable'] = True
                item.db.attribtes = a
            elif 'melee' in c:
                pass
            loot_set.append(item)


class MobFactory(Object):
    """
    Main Mob creation class
    """

    def at_object_creation(self):
        self.db.mob_set = []
        self.db.zone_type = None
        self.db.mob_names = ['Irradiated Rat', 'Survivor Scavenger', 'Infected Survivor', 'Shambling Corpse', 'Irradiated Dog', 'Reanimated Corpse', 'Crazed Looter']
        self.db.difficulty = 'average'
        self.db.level_range = (1, 7)

    def create_mob_set(self, number_of_mobs):
        self.db.mob_set = []
        for x in range(0, number_of_mobs):
            mob_name = random.choice(self.db.mob_names)
            mob_obj = create_object("game.gamesrc.objects.world.npc.Npc", key=mob_name, location=self)
            a = mob_obj.db.attributes
            a['level'] = random.randrange(self.db.level_range[0], self.db.level_range[1])
            mob_obj.db.attributes = a
            mob_obj.db.difficulty = self.db.difficulty
            mob_obj.generate_attributes()
            self.db.mob_set.append(mob_obj)
        return self.db.mob_set
            
        
