import random
from ev import Room, Object, create_object
from src.utils import search

class Zone(Object):
    """
    Main Zone class
    """

    def at_object_creation(self):
        self.db.rooms = search.objects("%s_room" % self.key)
        self.db.mob_map = {}
        self.db.player_map = {}
        self.db.quest_items = []
        self.db.zone_map = {}
        self.db.mob_factory = create_object("game.gamesrc.objects.world.factories.MobFactory", key='%s MobFactory' % self.key)
        self.aliases = [ 'zone_manager']

    def figure_mob_levels(self):
        mf = self.db.mob_factory
        self.db.rooms = search.objects('%s_room' % self.key)
        self.db.mobs = search.objects("%s_mobs" % mf.id)
        for room in self.db.rooms:
            mob_set = []
            print "checking %s" % room.name
            mobs = room.db.mobs

            for mob in room.db.mobs:
                self.db.mob_map['%s' % mob.dbref ] = room

            if len(room.db.mobs) < 2:
                #create mobs
                rn = random.randrange(0,10)
                mob_set = mf.create_mob_set(rn)
                for mob in mob_set:
                    mob.move_to(room, quiet=True)
                    mobs.append(mob)
                    room.db.mobs = mob_set
            else:
                pass
                room.db.mobs +=  mob_set

    def set_zone_manager(self):
        rooms = self.db.rooms
        zone_map = self.db.zone_map
        for room in rooms:
            zone_map['%s' % room.dbref] = room
            room.db.manager = self
        self.db.zone_map = zone_map
            
        
class WorldRoom(Room):
    """
    Main Room Class
    """

    def at_object_creation(self):
        
        self.db.tiles = {}
        self.db.attributes = { 'danger_level': .05, 'scouted': False, }
        self.db.decor_objects = {}
        self.db.mobs = []
        self.db.zone = None
        
