from ev import Room

class WorldRoom(Room):
    """
    Main Room Class
    """

    def at_object_creation(self):
        
        self.db.tiles = {}
        self.db.danger_level = .05
        self.db.scouted = False
        
