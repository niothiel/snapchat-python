Snapchat for Python
===================

Implementation of the Snapchat protocol in Python. Heavily based on
**php-snapchat**

Installation:
-------------

Use the python package manager for installation

.. code:: python

    pip install python-snapchat

Example:
--------

.. code:: python

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

License:
---------
MIT, See LICENSE for details
