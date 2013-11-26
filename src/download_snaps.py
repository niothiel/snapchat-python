import os
from snapchat import Snapchat

PATH = './snaps/'
EXTENSIONS = [
    'jpeg',
    'jpg',
    'mp4'
]

def get_downloaded():
    """Gets the snapchat IDs that have already been downloaded and returns them in a set."""

    result = set()

    for name in os.listdir(PATH):
        filename, ext = name.split('.')
        if ext not in EXTENSIONS:
            continue

        ts, username, id = filename.split('_')
        result.add(id)
    return result

def download(s, snap):
    """Download a specific snap, given output from s.get_snaps()."""

    id = snap['id']
    name = snap['sender']
    ts = str(snap['sent']).replace(':', '-')

    result = s.get_media(id)

    if not result:
        return False

    ext = s.is_media(result)
    filename = '{}_{}_{}.{}'.format(ts, name, id, ext)
    path = PATH + filename
    with open(path, 'wb') as fout:
        fout.write(result)
    return True

def download_snaps(s):
    """Download all snaps that haven't already been downloaded."""

    existing = get_downloaded()

    snaps = s.get_snaps()
    for snap in snaps:
        id = snap['id']
        if id[-1] == 's' or id in existing:
            print 'Skipping:', id
            continue

        result = download(s, snap)

        if not result:
            print 'FAILED:', id
        else:
            print 'Downloaded:', id

if __name__ == '__main__':
    s = Snapchat()
    s.login('USERNAME', 'PASSWORD')
    download_snaps(s)