from ev import Command, CmdSet

class CmdAttack(Command):
    """
    Begin to fight a target, typically an npc enemy.

    Usage:
        attack target-name

    """

    key = 'attack'
    aliases = ['kill']
    help_category = "Combat"
    locks = "cmd:all()"
    
    def parse(self):
        self.what = self.args.strip()
        
    def func(self):
        caller = self.caller
        mob = caller.search(self.what, global_search=False)
        print mob
        caller.begin_combat(mob)



class CharacterCmdSet(CmdSet):

    key = "CharacterClassCommands"

    def at_cmdset_creation(self):
        self.add(CmdAttack())


