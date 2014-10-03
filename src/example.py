from snapchat import Snapchat
import getpass
from pprint import pprint

s = Snapchat()

username = raw_input('Enter your username: ')
password = getpass.getpass('Enter your password: ')
s.login(username, password)

snaps = s.get_snaps()
pprint(snaps)