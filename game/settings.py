
######################################################################
# Evennia MU* server configuration file
#
# You may customize your setup by copy&pasting the variables you want
# to change from the master config file src/settings_default.py to
# this file. Try to *only* copy over things you really need to customize
# and do *not* make any changes to src/settings_default.py directly.
# This way you'll always have a sane default to fall back on
# (also, the master config file may change with server updates).
#
######################################################################

from src.settings_default import *

######################################################################
# Custom settings
######################################################################
###################################################
# Evennia Database config 
###################################################
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'zmud'
DATABASE_USER = 'muduser'
DATABASE_PASSWORD = 'muSHmud*'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.mysql',
        'NAME':'zmud',
        'USER':'muduser',
        'PASSWORD':'muSHmud*',
        'HOST':'localhost',
        'PORT':'3306'
        }}


######################################################################
# SECRET_KEY was randomly seeded when settings.py was first created.
# Don't share this with anybody. Warning: if you edit SECRET_KEY
# *after* creating any accounts, your users won't be able to login,
# since SECRET_KEY is used to salt passwords.
######################################################################
SECRET_KEY = 'H$-Z]xVt`QR,:gdzO@y=qUi3T<WvJp/w7j(P"M&|'

BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.world.character.SurvivorClass"
