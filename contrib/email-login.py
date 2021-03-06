"""
Email-based login system

Evennia contrib - Griatch 2012


This is a variant of the login system that requires a email-adress
instead of a username to login.

This used to be the default Evennia login before replacing it with a
more standard username + password system (having to supply an email
for some reason caused a lot of confusion when people wanted to expand
on it. The email is not strictly needed internally, nor is any
confirmation email sent out anyway).


Install is simple:

To your settings file, add/edit the line:

CMDSET_UNLOGGEDIN = "contrib.email_login.UnloggedInCmdSet"

That's it. Reload the server and try to log in to see it.

The initial login "graphic" is taken from strings in the module given
by settings.CONNECTION_SCREEN_MODULE. You will want to copy the
template file in game/gamesrc/conf/examples up one level and re-point
the settings file to this custom module. you can then edit the string
in that module (at least comment out the default string that mentions
commands that are not available) and add something more suitable for
the initial splash screen.

"""
import re
import traceback
from django.conf import settings
from django.contrib.auth.models import User
from src.players.models import PlayerDB
from src.objects.models import ObjectDB
from src.server.models import ServerConfig
from src.comms.models import Channel

from src.commands.cmdset import CmdSet
from src.utils import create, logger, utils, ansi
from src.commands.default.muxcommand import MuxCommand
from src.commands.cmdhandler import CMD_LOGINSTART

# limit symbol import for API
__all__ = ("CmdUnconnectedConnect", "CmdUnconnectedCreate", "CmdUnconnectedQuit", "CmdUnconnectedLook", "CmdUnconnectedHelp")

CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE
CONNECTION_SCREEN = ""
try:
    CONNECTION_SCREEN = ansi.parse_ansi(utils.string_from_module(CONNECTION_SCREEN_MODULE))
except Exception:
    pass
if not CONNECTION_SCREEN:
    CONNECTION_SCREEN = "\nEvennia: Error in CONNECTION_SCREEN MODULE (randomly picked connection screen variable is not a string). \nEnter 'help' for aid."

class CmdUnconnectedConnect(MuxCommand):
    """
    Connect to the game.

    Usage (at login screen):
      connect <email> <password>

    Use the create command to first create an account before logging in.
    """
    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()" # not really needed

    def func(self):
        """
        Uses the Django admin api. Note that unlogged-in commands
        have a unique position in that their func() receives
        a session object instead of a source_object like all
        other types of logged-in commands (this is because
        there is no object yet before the player has logged in)
        """

        session = self.caller
        arglist = self.arglist

        if not arglist or len(arglist) < 2:
            session.msg("\n\r Usage (without <>): connect <email> <password>")
            return
        email = arglist[0]
        password = arglist[1]

        # Match an email address to an account.
        player = PlayerDB.objects.get_player_from_email(email)
        # No playername match
        if not player:
            string = "The email '%s' does not match any accounts." % email
            string += "\n\r\n\rIf you are new you should first create a new account "
            string += "using the 'create' command."
            session.msg(string)
            return
        # We have at least one result, so we can check the password.
        if not player.user.check_password(password):
            session.msg("Incorrect password.")
            return

        # Check IP and/or name bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (any(tup[0]==player.name for tup in bans)
                     or
                     any(tup[2].match(session.address[0]) for tup in bans if tup[2])):
            # this is a banned IP or name!
            string = "{rYou have been banned and cannot continue from here."
            string += "\nIf you feel this ban is in error, please email an admin.{x"
            session.msg(string)
            session.execute_cmd("quit")
            return

        # actually do the login. This will call all hooks.
        session.session_login(player)

        # we are logged in. Look around.
        character = player.character
        if character:
            character.execute_cmd("look")
        else:
            # we have no character yet; use player's look, if it exists
            player.execute_cmd("look")


class CmdUnconnectedCreate(MuxCommand):
    """
    Create a new account.

    Usage (at login screen):
      create \"playername\" <email> <password>

    This creates a new player account.

    """
    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"

    def parse(self):
        """
        The parser must handle the multiple-word player
        name enclosed in quotes:
        connect "Long name with many words" my@myserv.com mypassw
        """
        super(CmdUnconnectedCreate, self).parse()

        self.playerinfo = []
        if len(self.arglist) < 3:
            return
        if len(self.arglist) > 3:
            # this means we have a multi_word playername. pop from the back.
            password = self.arglist.pop()
            email = self.arglist.pop()
            # what remains is the playername.
            playername = " ".join(self.arglist)
        else:
            playername, email, password = self.arglist

        playername = playername.replace('"', '') # remove "
        playername = playername.replace("'", "")
        self.playerinfo = (playername, email, password)

    def func(self):
        "Do checks and create account"

        session = self.caller

        try:
            playername, email, password = self.playerinfo
        except ValueError:
            string = "\n\r Usage (without <>): create \"<playername>\" <email> <password>"
            session.msg(string)
            return
        if not re.findall('^[\w. @+-]+$', playername) or not (0 < len(playername) <= 30):
            session.msg("\n\r Playername can max be 30 characters or fewer. Letters, spaces, dig\
its and @/./+/-/_ only.") # this echoes the restrictions made by django's auth module.
            return
        if not email or not password:
            session.msg("\n\r You have to supply an e-mail address followed by a password." )
            return

        if not utils.validate_email_address(email):
            # check so the email at least looks ok.
            session.msg("'%s' is not a valid e-mail address." % email)
            return

        # Run sanity and security checks

        if PlayerDB.objects.get_player_from_name(playername) or User.objects.filter(username=playername):
            # player already exists
            session.msg("Sorry, there is already a player with the name '%s'." % playername)
            return
        if PlayerDB.objects.get_player_from_email(email):
            # email already set on a player
            session.msg("Sorry, there is already a player with that email address.")
            return
        if len(password) < 3:
            # too short password
            string = "Your password must be at least 3 characters or longer."
            string += "\n\rFor best security, make it at least 8 characters long, "
            string += "avoid making it a real word and mix numbers into it."
            session.msg(string)
            return

        # everything's ok. Create the new player account.
        try:
            default_home = ObjectDB.objects.get_id(settings.CHARACTER_DEFAULT_HOME)

            typeclass = settings.BASE_CHARACTER_TYPECLASS
            permissions = settings.PERMISSION_PLAYER_DEFAULT

            try:
                new_character = create.create_player(playername, email, password,
                                                     permissions=permissions,
                                                     character_typeclass=typeclass,
                                                     character_location=default_home,
                                                     character_home=default_home)
            except Exception, e:
                session.msg("There was an error creating the default Character/Player:\n%s\n If this problem persists, contact an admin.")
                return
            new_player = new_character.player

            # This needs to be called so the engine knows this player is logging in for the first time.
            # (so it knows to call the right hooks during login later)
            utils.init_new_player(new_player)

            # join the new player to the public channel
            pchanneldef = settings.CHANNEL_PUBLIC
            if pchanneldef:
                pchannel = Channel.objects.get_channel(pchanneldef[0])
                if not pchannel.connect_to(new_player):
                    string = "New player '%s' could not connect to public channel!" % new_player.key
                    logger.log_errmsg(string)

            # allow only the character itself and the player to puppet this character (and Immortals).
            new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                    (new_character.id, new_player.id))


            # set a default description
            new_character.db.desc = "This is a Player."

            # tell the caller everything went well.
            string = "A new account '%s' was created with the email address %s. Welcome!"
            string += "\n\nYou can now log with the command 'connect %s <your password>'."
            session.msg(string % (playername, email, email))

        except Exception:
            # We are in the middle between logged in and -not, so we have to handle tracebacks
            # ourselves at this point. If we don't, we won't see any errors at all.
            string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
            session.msg(string % (traceback.format_exc()))
            logger.log_errmsg(traceback.format_exc())

class CmdUnconnectedQuit(MuxCommand):
    """
    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "quit"
    aliases = ["q", "qu"]
    locks = "cmd:all()"

    def func(self):
        "Simply close the connection."
        session = self.caller
        session.msg("Good bye! Disconnecting ...")
        session.session_disconnect()

class CmdUnconnectedLook(MuxCommand):
    """
    This is an unconnected version of the look command for simplicity.

    This is called by the server and kicks everything in gear.
    All it does is display the connect screen.
    """
    key = CMD_LOGINSTART
    aliases = ["look", "l"]
    locks = "cmd:all()"

    def func(self):
        "Show the connect screen."
        self.caller.msg(CONNECTION_SCREEN)

class CmdUnconnectedHelp(MuxCommand):
    """
    This is an unconnected version of the help command,
    for simplicity. It shows a pane of info.
    """
    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def func(self):
        "Shows help"

        string = \
            """
You are not yet logged into the game. Commands available at this point:
  {wcreate, connect, look, help, quit{n

To login to the system, you need to do one of the following:

{w1){n If you have no previous account, you need to use the 'create'
   command like this:

     {wcreate "Anna the Barbarian" anna@myemail.com c67jHL8p{n

   It's always a good idea (not only here, but everywhere on the net)
   to not use a regular word for your password. Make it longer than
   3 characters (ideally 6 or more) and mix numbers and capitalization
   into it.

{w2){n If you have an account already, either because you just created
   one in {w1){n above or you are returning, use the 'connect' command:

     {wconnect anna@myemail.com c67jHL8p{n

   This should log you in. Run {whelp{n again once you're logged in
   to get more aid. Hope you enjoy your stay!

You can use the {wlook{n command if you want to see the connect screen again.
"""
        self.caller.msg(string)

# command set for the mux-like login

class UnloggedinCmdSet(CmdSet):
    """
    Sets up the unlogged cmdset.
    """
    key = "Unloggedin"
    priority = 0

    def at_cmdset_creation(self):
        "Populate the cmdset"
        self.add(CmdUnconnectedConnect())
        self.add(CmdUnconnectedCreate())
        self.add(CmdUnconnectedQuit())
        self.add(CmdUnconnectedLook())
        self.add(CmdUnconnectedHelp())
