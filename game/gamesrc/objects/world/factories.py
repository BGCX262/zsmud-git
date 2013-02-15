from ev import Object, create_object


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
        self.db.scavenging_items {'Can of Beans': .08, 'Bag of Rice': .10, 'Metal Scraps': .35, 'Wood Scraps':.35, 'Wood planks':.15, 'Sheet metal': .10, 'Old tire rubber':.40, 
                                    'Old can of Spinach':.12, 'Bottle of Water':.07, 'Old can of Soda': .20, 'Candybar': .20, 'Can of Carrots': .15, 'Can of Green beans': .20,
                                    'Bag of Northern Beans': .30, 'Can of Oranges': .15, 'Can of Pears': .20, 'Can of Peaches': .20, 'Nails and Screws': .30, 'Nuts and Bolts': .40,
                                    'First Aid Kit': .25, 'Pain Reliever': .40 }

   
    def create_lootset(self, loot_rating='below average', number_of_items):
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
                elif 'excellent' in loot_rating
                    prefix = random.choice(['Amazing', 'Excellent', 'Spectacular'])
                    name = prefix + name
            
                gun = create_object("game.gamesrc.objects.world.item.Item", key=name, location=self)
                a = gun.db.attributes
                a['damage_dice'] = dd
                a['weapon_type'] = type
                a['item_slot'] = 'weapon'
                a['equipable'] = True
                gun.db.type = c
            elif 'scavenging' in c:
                pass
            elif 'melee' in c:
                pass


                
