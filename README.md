Snapchat for Python
===============

Implementation of the Snapchat protocol in Python. Heavily based on [php-snapchat](https://github.com/dstelljes/php-snapchat).

Install
-------

```
pip install requests
easy_install pycrypto
git clone https://github.com/niothiel/snapchat-python.git
cd snapchat-python/src
python example.py
```

Example
-------
To get started, download snapchat.py and in another file enter the following:

```
from snapchat import Snapchat

s = Snapchat()
s.login('USERNAME', 'PASSWORD')

# Send a snapchat
media_id = s.upload(Snapchat.MEDIA_IMAGE, 'filename.jpg')
s.send(media_id, 'recipient')

# Get all snaps
snaps = s.get_snaps()

# Download a snap
s.get_media(snap['id'])

# Clear snapchat history
s.clear_feed()
```
