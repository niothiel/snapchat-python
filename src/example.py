from snapchat import Snapchat
import getpass

s = Snapchat()

username = raw_input('Enter your username: ')
password = getpass.getpass('Enter your password: ')
s.login(username, password)

snaps = s.get_snaps()
print snaps