from ev import Object
import random

class Npc(Object):
    """
    Main npc class that is used for hostiles and friendlies alike.
    """

    def at_object_creation(self):
        self.db.attributes = { 'strength': 10, 'endurance': 10, 'perception': 10, 'wisdom': 10, 'luck': 5, 'health': 0, 'stamina': 0, 'temp_health': 0, 'temp_stamina': 0, 'level': 1, 'exp_needed': 300, 'exp': 0, 'total_exp': 0, 'exp_reward': 0, 'currency_reward': 0}
        self.db.combat_attributes = {'attack_bonus': 1, 'damage_threshold': 0, 'armor_class': 1, 'defense_rating': 1}
        self.db.equipment = {'weapon': None, 'protection': None}
        attributes = self.db.attributes
        attributes['health'] = attributes['endurance'] * 4
        attributes['temp_health'] = attributes['health']
        attributes['stamina'] = attributes['endurance'] * 2
        attributes['temp_stamina'] = attributes['stamina']
        self.db.attributes = attributes
        self.db.target = None
        

    def take_damage(self, damage):
        a = self.db.attributes
        a['temp_health'] -= damage
        if a['temp_health'] <= 0:
            self.death()
        self.db.attributes = a
    
    def get_damage(self):
        w = self.db.equipment['weapon']
        if w is None:
            damagedice = (1, 4)
            damage = random.randrange(damagedice[0], damagedice[1])
            return damage
        else:
            damagedice = w.db.damage
            damage = random.randrange(damagedice[0], damagedice[1])
            return damage

    def attack_roll(self):
        adice = (1, 20)
        roll = random.randrange(adice[0], adice[1])
        return roll

    def get_initiative(self):
        """
        roll for attack initiative
        """
        idice = (1, 20)
        roll = random.randrange(idice[0], idice[1])
        return roll

    def do_attack_phase(self):
        a = self.db.attributes
        e = self.db.equipment
        t = self.db.target
        w = e['weapon']
        attack_roll = self.attack_roll()
        print "in attack block"
        if attack_roll >= t.db.combat_attributes['defense_rating']:
            damage = self.get_damage()
            unarmed_hit_texts = [ '%s punches you relentlessly for %s damage!' % (self.name, damage),           
                                   '%s pummels the daylights out of you for %s damage.' % (self.name, damage),           
                                   'You attempt to grab %s, but they dodge and uppercut youfor %s damage.' % (self.name, damage),
                                   '%s punches you hard in the mouth for %s damage.' % (self.name, damage),
                                   'As %s lands a hard blow against you, you feel bones breaking under your skin.  You take %s damage.' % (self.name, damage) 
            ]
            if w:
                gun_hit_texts = [ 'As %s rapidly pulls the trigger of their %s, it hits you dead on dealing %s damage' % ( self.name, w.name, damage),
                                'With a squeeze of the trigger and the report of the %s, %s does %s damage to you.' % (w.name, damage, self.name),
                                '%s lets off a volley of shots hitting you dealing %s damage.' % (self.name, damage),
                                '%s unleashes a hail of lead upon you dealing %s damage.' % (self.name, damage) 
                ]
            melee_hit_texts = []
            if w is None:
                ht = random.choice(unarmed_hit_texts)
            elif w is not None and w['type'] is 'gun':
                ht = random.choice(gun_hit_texts)
            t.msg(ht)
            t.take_damage(damage)
    
    def do_skill_phase(self):
        pass


    def death(self):
        self.db.target = None
        self.aliases += 'corpse'
        self.key = "Corpse of %s" % self.name
        
        
 
