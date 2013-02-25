from ev import Object, Character, utils, create_object, create_channel
from game.gamesrc.commands.world.character_commands import CharacterCmdSet
import random

class SurvivorClass(Character):
    """
    Main player class
    """
    
    def at_object_creation(self):
        self.db.attributes = { 'name': None, 'strength': 10, 'endurance': 10, 'perception': 10, 'agility': 10, 'luck': 5, 'health': 0, 'stamina': 0, 'temp_health': 0, 'temp_stamina': 0, 'level': 1, 'exp_needed': 300, 'exp': 0, 'total_exp': 0}
        self.db.combat_attributes = { 'attack_bonus': 0, 'damage_threshold': 0, 'armor_class': 1, 'defense_rating': 1}
        self.db.currency = { 'dollars': 0 }
        self.db.skills = { 'scavenging': { 'rating': .05, 'desc': 'The ability to scrounge up items.'},
                           'lockpicking': { 'rating':.01, 'desc': 'Your skill with picking locked doors and items.'},
                            'guns': {'rating': .15, 'desc': 'Base ability with all firearms.'},
                            'martial arts': {'rating': .20, 'desc': 'Base ability to fight hand to to hand.'},
                            'stealth': {'rating': .01, 'desc': 'Ability to move without being seen or heard'},
                            'repair': {'rating': .01, 'desc': 'Ability to fix broken junk found in the world'},
                            }
        self.db.archtypes = { 'soldier': {'level': 1, 'exp_to_level': 100, 'exp': 0, 'total_exp': 0 },
                              'scavenger': {'level': 1, 'exp_to_level': 100, 'exp': 0, 'total_exp': 0 },
                              'builder': {'level': 1, 'exp_to_level': 100, 'exp': 0, 'total_exp': 0 },
                            }        
        self.db.equipment = { 'weapon': None, 'protection': None }
        self.db.attack_phase_queue = []
        self.db.skill_phase_queue = []
        self.db.target = None
        self.db.in_combat = False
        attributes = self.db.attributes
        attributes['health'] = attributes['endurance'] * 4
        attributes['temp_health'] = attributes['health']
        attributes['stamina'] = attributes['endurance'] * 2
        attributes['temp_stamina'] = attributes['stamina']
        self.db.attributes = attributes
        self.aliases += 'character_runner'

    def at_disconnect(self):
        self.prelogout_location = self.location

    def at_post_login(self):
        self.cmdset.add(CharacterCmdSet)
        self.location = self.db.prelogout_location
    
    def award_currency(self, amount, type='dollars'):
        """
        award the passed amount of currency to the characters money levels.
        """
        c = self.db.currency
        c[type] += amount
        self.msg("{CYou have received %s %s.{n" % (amount, type))
        self.db.currency = c
        

    def award_exp(self, exp, archtype=None):
        """
        Award passed amount of experience to character experience levels and
        archtype experience levels.
        """
        attributes = self.db.attributes
        archtypes = self.db.archtypes
        if archtype is None:
            self.msg("{CYou have earned %s experience.{n" % exp)     
        else:
            self.msg("{CYou have earned %s experience in archtype: %s" % (exp, archtype)) 
        if archtype is not None:
            archtypes[archtype]['exp'] += exp
            archtypes[archtype]['total_exp'] += exp
            self.db.archtypes = archtypes
            if archtypes[archtype]['exp'] == archtypes[archtype]['exp_to_level']:
                self.level_up_archtype(archtype='%s' % archtype)
            elif archtypes[archtype]['exp'] > archtypes[archtype]['exp_to_level']:
                offset = archtypes[archtype]['exp'] - archtypes[archtype]['exp_to_level']
                self.level_up_archtype(archtype='%s' % archtype, offset=offset)
        attributes['exp'] += exp
        attributes['total_exp'] += exp
        self.db.attributes = attributes
        if attributes['exp'] == attributes['exp_needed']:
            self.level_up()
        elif attributes['exp'] > attributes['exp_needed']:
            offset = attributes['exp'] - attributes['exp_needed']
            self.level_up(offset=offset)

    def level_up(self, offset=None):
        """
        increase base character level by one level.
        """
        attributes = self.db.attributes
        if offset is not None:
            attributes['exp'] = offset
            attributes['exp_needed'] = attributes['total_exp'] * 2
            attributes['level'] += 1
        else:
            attributes['exp'] = 0
            attributes['exp_needed'] = attributes['total_exp'] * 2
            attributes['level'] += 1
        self.msg("{cYou have gained a level of experience!{n")
        self.db.attributes = attributes

    def level_up_archtype(self, archtype, offset=None):
        archtypes = self.db.archtypes
        if archtype is not None:
            if offset is not None:
                archtypes[archtype]['exp'] = offset
                archtypes[archtype]['exp_to_level'] = archtypes[archtype]['total_exp'] * 1.5
                archtypes[archtype]['level'] += 1
            else:
                archtypes[archtype]['exp'] = 0
                archtypes[archtype]['exp_to_level'] = archtypes[archtype]['total_exp'] * 1.5
                archtypes[archtype]['level'] += 1
                
            self.msg("{cYou have gained an archtype level in: {C%s.{n" % archtype)
            self.db.archtypes = archtypes
        else:
            return

    def tick(self):
        """
        Main function for all things needing to be done/checked every time the mob tick
        script fires itself (health and mana regen, kos checks etc etc)
        """
        a = self.db.attributes
        if a['temp_health'] < a['health'] and not self.db.in_combat:
            pth = int(a['health'] * .02) + 1
            a['temp_health'] = a['temp_health'] + pth
            if a['temp_health'] > a['health']:
                a['temp_health'] = a['health']

        self.db.attributes = a

    def take_damage(self, damage):
        """
        remove health when damage is taken
        """
        a = self.db.attributes
        a['temp_health'] -= damage
        self.db.attributes = a
         
    ###########################
    #COMBAT RELATED FUNCTIONS##
    ###########################

    def begin_combat(self, target):
        """
        begins combat sequence
        """
        self.db.target = target
        target.db.target = self
        self.scripts.add("game.gamesrc.scripts.world_scripts.combat.CombatController")

    def unconcious(self):
        """
        put a character unconcious, which adds a script that checks to see if they
        have woken up yet from their dirt nap.
        """
        attributes = self.db.attributes
        attributes['temp_health'] = attributes['health']
        self.db.attributes = attributes
        self.db.in_combat = False
        
       # self.db.unconcious = True
        
    def get_initiative(self):
        """
        roll for attack initiative
        """
        idice = (1, 20)
        roll = random.randrange(idice[0], idice[1])
        return roll

    def do_attack_phase(self):
        """
        run through attack logic and apply it to self.db.target,
        return gracefully upon None target.
        """
        t = self.db.target
        e = self.db.equipment
        print "subscripting weapons"
        w = e['weapon']
        attack_roll = self.attack_roll()
        print "in attack phase, about to do logic"
        if attack_roll >= t.db.combat_attributes['defense_rating']:
            damage = self.get_damage()
            unarmed_hit_texts = [ 'You punch %s unrelenlessly for %s damage' % (t.name, damage),
                                   'You pummel the daylights out of %s for %s damage.' % (t.name, damage),
                                   'As %s attempts to grab you, you dodge and uppercut them for %s damage.' % (t.name, damage),
                                   'You punch %s hard in the mouth for %s damage' % (t.name, damage),
                                   'As you land a hard blow against %s, you feel bones breaking under your fist.  You deal %s damage.' % (t.name, damage)
                                ]
            if w:
                gun_hit_texts = [ 'You rapidly pull the trigger of your %s, hitting %s dead on and dealing %s damage' % ( w.name, t.name, damage),
                                'With a squeeze of the trigger and the report of the %s you do %s damage to %s.' % (w.name, damage, t.name),
                                'You let off a volley of shots hitting %s dealing %s damage.' % (t.name, damage),
                                'You unlease a hail of lead upon %s dealing %s damage.' % (t.name, damage),
                            ]
            melee_hit_texts = []
            if w is None:
                ht = random.choice(unarmed_hit_texts)
            elif 'gun' in w.db.type:
                ht = random.choice(gun_hit_texts)
            self.msg(ht) 
           
            t.take_damage(damage)
        else:
            #miss
            pass

    def do_skill_phase(self):
        #placeholder
        pass
        
    def get_damage(self):
        e = self.db.equipment
        w = e['weapon']
        if w is None:
            damagedice = (1, 4)
            damage = random.randrange(damagedice[0], damagedice[1])
            return damage
        else:
            damagedice = w.db.attributes['damage_dice']
            damage = random.randrange(damagedice[0], damagedice[1])
            return damage

    def attack_roll(self):
        dice = (1, 20)
        roll = random.randrange(dice[0], dice[1])
        return roll
         
