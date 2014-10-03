import requests
import hashlib
import json
import time

from datetime import datetime
from Crypto.Cipher import AES


if False:
    import logging
    import httplib
    httplib.HTTPConnection.debuglevel = 1

class Snapchat(object):

    URL =                   'https://feelinsonice-hrd.appspot.com/bq'
    SECRET =                'iEk21fuwZApXlz93750dmW22pw389dPwOk'        # API Secret
    STATIC_TOKEN =          'm198sOkJEn37DjqZ32lpRu76xmw288xSQ9'        # API Static Token
    BLOB_ENCRYPTION_KEY =   'M02cnQ51Ji97vwT4'                          # Blob Encryption Key
    HASH_PATTERN =          '0001110111101110001111010101111011010001001110011000110001000110'; # Hash pattern
    USERAGENT =             'Snapchat/6.0.0 (iPhone; iOS 7.0.2; gzip)'  # The default useragent
    SNAPCHAT_VERSION =      '4.0.0'                                     # Snapchat Application Version

    MEDIA_IMAGE =                        0  # Media: Image
    MEDIA_VIDEO =                        1  # Media: Video
    MEDIA_VIDEO_NOAUDIO =                2  # Media: Video without audio
    MEDIA_FRIEND_REQUEST =               3  # Media: Friend Request
    MEDIA_FRIEND_REQUEST_IMAGE =         4  # Media: Image from unconfirmed friend
    MEDIA_FRIEND_REQUEST_VIDEO =         5  # Media: Video from unconfirmed friend
    MEDIA_FRIEND_REQUEST_VIDEO_NOAUDIO = 6  # Media: Video without audio from unconfirmed friend

    STATUS_NONE =                       -1  # Snap status: None
    STATUS_SENT =                        0  # Snap status: Sent
    STATUS_DELIVERED =                   1  # Snap status: Delivered
    STATUS_OPENED =                      2  # Snap status: Opened
    STATUS_SCREENSHOT =                  3  # Snap status: Screenshot

    FRIEND_CONFIRMED =                   0  # Friend status: Confirmed
    FRIEND_UNCONFIRMED =                 1  # Friend status: Unconfirmed
    FRIEND_BLOCKED =                     2  # Friend status: Blocked
    FRIEND_DELETED =                     3  # Friend status: Deleted

    PRIVACY_EVERYONE =                   0  # Privacy setting: Accept snaps from everyone
    PRIVACY_FRIENDS =                    1  # Privacy setting: Accept snaps only from friends

    def __init__(self, username=None, password=None):
        self.username = None
        self.auth_token = None
        self.logged_in = False

        self.cipher = AES.new(Snapchat.BLOB_ENCRYPTION_KEY, AES.MODE_ECB)

        if username and password:
            self.login(username, password)

    def _pad(self, data, blocksize=16):
        """Pads data using PKCS5."""

        pad = blocksize - (len(data) % blocksize)
        return data + chr(pad) * pad

    def _hash(self, first, second):
        """Implementation of Snapchat's weird hashing function."""

        # Append the secret key to the values.
        first = Snapchat.SECRET + str(first)
        second = str(second) + Snapchat.SECRET

        # Hash the values.
        hash1 = hashlib.sha256(first).hexdigest()
        hash2 = hashlib.sha256(second).hexdigest()

        # Create the final hash by combining the two we just made.
        result = ''
        for pos, included in enumerate(Snapchat.HASH_PATTERN):
            if included == '0':
                result += hash1[pos]
            else:
                result += hash2[pos]

        return result

    def _timestamp(self):
        """Generates a timestamp in microseconds."""

        return int(time.time() * 1000)

    def _encrypt(self, data):
        """Encrypt the blob."""

        data = self._pad(data)
        return self.cipher.encrypt(data)

    def _decrypt(self, data):
        """Decrypt the blob."""

        data = self._pad(data)
        return self.cipher.decrypt(data)

    def _parse_field(self, dictionary, key, bool=False):
        """Correctly parse a field from a dictionary object.

        Takes care of missing keys, and empty fields.

        :param dictionary: The dictionary.
        :param key: The key for the dictionary.
        :param bool: Whether or not the value should be a boolean"""

        if key not in dictionary:
            if bool:
                return False
            return None

        value = dictionary[key]
        if not value:
            if bool:
                return False
            return None

        return value

    def _parse_datetime(self, dt):
        """Gracefully concert and parse a text timestamp in microseconds."""

        try:
            return datetime.fromtimestamp(dt / 1000)
        except:
            return dt

    def is_media(self, data):
        """Check if the blob is a valid media type."""

        # Check for JPG header.
        if data[0] == chr(0xff) and data[1] == chr(0xd8):
            return 'jpg'

        # Check for MP4 header.
        if data[0] == chr(0x00) and data[1] == chr(0x00):
            return 'mp4'

        return False

    def post(self, endpoint, data, params, file=None):
        """Submit a post request to the Snapchat API.

        :param endpoint: The service to submit the request to, i.e. '/upload'.
        :param data: The data to upload.
        :param params: Request specific authentication, typically a tuple of form (KEY, TIME).
        :param file: Optional field for submitting file content in multipart messages.
        """

        data['req_token'] = self._hash(params[0], params[1])
        data['version'] = Snapchat.SNAPCHAT_VERSION

        headers = {
            'User-Agent': Snapchat.USERAGENT
        }

        url = Snapchat.URL + endpoint

        if file:
            r = requests.post(url, data, headers=headers, files={'data': file})
        else:
            r = requests.post(url, data, headers=headers)

        # If the status code isn't 200, it's a failed request.
        if r.status_code != 200:
            if False:
                print 'Post returned code: ', r.status_code, 'for request', endpoint, data
                print 'Error content:'
                print r.content
            return False

        # If possible, try to return a json object.
        try:
            return json.loads(r.content)
        except:
            return r.content

    def login(self, username, password):
        """Login to Snapchat."""

        timestamp = self._timestamp()

        data = {
            'username': username,
            'password': password,
            'timestamp': timestamp
        }

        params = [
            Snapchat.STATIC_TOKEN,
            timestamp
        ]

        result = self.post('/login', data, params)

        if 'auth_token' in result:
            self.auth_token = result['auth_token']

        if 'username' in result:
            self.username = result['username']

        if self.auth_token and self.username:
            self.logged_in = True

        return result

    def logout(self):
        """Logout of Snapchat."""

        if not self.logged_in:
            return False

        timestamp = self._timestamp()

        data = {
            'username': username,
            'timestamp': timestamp
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/logout', data, params)
        if not result:
            self.logged_in = False
            return True

        return False

    def register(self, username, password, email, birthday):
        """Registers a new username for the Snapchat service.

        :param username: The username of the new user.
        :param password: The password of the new user.
        :param email: The email of the new user.
        :param birthday: The birthday of the new user (yyyy-mm-dd).
        """

        timestamp = self._timestamp()

        data = {
            'birthday': birthday,
            'password': password,
            'email': email,
            'timestamp': timestamp
        }

        params = [
            Snapchat.STATIC_TOKEN,
            timestamp
        ]

        # Perform email/password registration.
        result = self.post('/register', data, params)

        timestamp = self._timestamp()

        if 'token' not in result:
            return False

        data = {
            'email': email,
            'username': username,
            'timestamp': timestamp
        }

        params = [
            Snapchat.STATIC_TOKEN,
            timestamp
        ]

        # Perform username registration.
        result = self.post('/registeru', data, params)

        # Store the authentication token if the server sent one.
        if 'auth_token' in result:
            self.auth_token = result['auth_token']

        # Store the username if the server sent it.
        if 'username' in result:
            self.username = result['username']

        return result

    def upload(self, type, filename):
        """Upload a video or image to Snapchat.

        You must call send() after uploading the image for someone the receive it.

        :param type: The type of content being uploaded, i.e. Snapchat.MEDIA_VIDEO.
        :param filename: The filename of the content.
        :returns: The media_id of the file if successful.
        """

        if not self.logged_in:
            return False

        timestamp = self._timestamp()

        # TODO: media_ids are GUIDs now.
        media_id = self.username.upper() + '~' + str(timestamp)

        data = {
            'media_id': media_id,
            'type': type,
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        # Read the file and encrypt it.
        with open(filename, 'rb') as fin:
            encrypted_data = self._encrypt(fin.read())

        result = self.post('/upload', data, params, encrypted_data)

        if result:
            return False
        return media_id

    def send(self, media_id, recipients, time=10):
        """Send a Snapchat.

        You must have uploaded the video or image using upload() to get the media_id.

        :param media_id: The unique id for the media.
        :param recipients: A list of usernames to send the Snap to.
        :param time: Viewing time for the Snap (in seconds).
        """

        if not self.logged_in:
            return False

        # If we only have one recipient, convert it to a list.
        if not isinstance(recipients, list):
            recipients = [recipients]

        timestamp = self._timestamp()

        data = {
            'media_id': media_id,
            'recipient': ','.join(recipients),
            'time': time,
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/send', data, params)
        return result <> False

    def set_story(self, media_id, media_type, time=10):
        """Send a Snapchat.

        You must have uploaded the video or image using upload() to get the media_id.

        :param media_id: The unique id for the media.
        :param media_type: 0 for photo, 1 for video.
        :param time: Viewing time for the Snap (in seconds).
        """
        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        print media_id
        data = {
            'client_id': media_id,
            'media_id': media_id,
            'time': time,
            'timestamp': timestamp,
            'username': self.username,
            'caption_text_display': '#YOLO',
            'type': 0,
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/post_story', data, params)
        return result <> False

    def get_updates(self):
        """Get all events pertaining to the user. (User, Snaps, Friends)."""

        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        data = {
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/all_updates', data, params)
        return result

    def get_snaps(self):
        """Get all snaps for the user."""

        updates = self.get_updates()

        if not updates:
            return False

        snaps = updates['updates_response']['snaps']
        result = []

        print self._timestamp()
        for snap in snaps:
            # Make the fields more readable.
            snap_readable = {
                'id': self._parse_field(snap, 'id'),
                'media_id': self._parse_field(snap, 'c_id'),
                'media_type': self._parse_field(snap, 'm'),
                'time': self._parse_field(snap, 't'),
                'sender': self._parse_field(snap, 'sn'),
                'recipient': self._parse_field(snap, 'rp'),
                'status': self._parse_field(snap, 'st'),
                'screenshot_count': self._parse_field(snap, 'c'),
                'sent': self._parse_datetime(snap['sts']),
                'opened': self._parse_datetime(snap['ts'])
            }
            result.append(snap_readable)

        return result

    def get_stories(self):
        """Get all stories."""

        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        data = {
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/stories', data, params)
        
        return result

    def get_media(self, id):
        """Download a snap.

        :param id: The unique id of the snap (NOT media_id).
        :returns: The media in a byte string.
        """

        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        data = {
            'id': id,
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/blob', data, params)

        if not result:
            return False

        if self.is_media(result):
            return result

        result = self._decrypt(result)

        if self.is_media(result):
            return result

        return False

    def find_friends(self, numbers, country='US'):
        """Finds friends based on phone numbers.

        :param numbers: A list of phone numbers.
        :param country: The country code (US is default).
        :returns: List of user objects found.
        """

        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        data = {
            'countryCode': country,
            'numbers': json.dumps(numbers),
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/find_friends', data, params)

        print result

        if 'results' in result:
            return result['results']

        return result

    def clear_feed(self):
        """Clear the user's feed."""

        if not self.logged_in:
            return False

        timestamp = self._timestamp()
        data = {
            'timestamp': timestamp,
            'username': self.username
        }

        params = [
            self.auth_token,
            timestamp
        ]

        result = self.post('/clear', data, params)

        if not result:
            return True

        return False
