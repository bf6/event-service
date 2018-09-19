import os
import shutil
import sqlite3
import uuid

import falcon
import requests
from InstagramAPI import InstagramAPI

insta = InstagramAPI(os.environ.get('INSTAGRAM_USER'), os.environ.get('INSTAGRAM_PASS'))
insta.login()

conn = sqlite3.connect('events.db')
db = conn.cursor()

class EventResource:

    def _is_event_processed(self, event_id):
        return db.execute('SELECT * from events WHERE event_id=?', (event_id,)).fetchone()

    def _get_first_hashtag(self, req):
        hashtag = None
        message_body = req.media.get('event', {}).get('text') or \
                       req.media.get('event', {}).get('message', {}).get('text')
        for word in message_body.split(' '):
            if word.startswith('#'):
                hashtag = word
                break
        return hashtag

    def _get_image_url(self, req):
        image_url = req.media.get('event', {}).get('message', {}).get('attachments', [{}])[0].get('image_url', None) or\
                    req.media.get('event', {}).get('message', {}).get('files', [{}])[0].get('url_private', None) or\
                    req.media.get('event', {}).get('files', [{}])[0].get('url_private', None)
        return image_url

    def _download_image(self, image_url):
        r = requests.get(image_url, stream=True, headers={'Authorization': 'Bearer {}'.format(os.environ.get('SLACK_ACCESS_TOKEN'))})
        if r.status_code == 200:
            path = '{}'.format(uuid.uuid4().hex)
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return path

    def on_post(self, req, resp):
        try:
            event_id = req.media.get('event_id')
            if event_id is None:
                return

            if self._is_event_processed(event_id):
                return

            hashtag = self._get_first_hashtag(req)
            if hashtag is None:
                return

            # Get image url
            image_url = self._get_image_url(req)
            if image_url is None:
                return

            path = self._download_image(image_url)

            # Post to IG and save in DB
            insta.uploadPhoto(path, caption=hashtag)
            db.execute('INSERT INTO events VALUES (?)', (event_id,))
            conn.commit()

            # Delete tmp image
            os.remove(path)

        except Exception as e:
            resp.status_code = 500
            resp.media = {'message': e}
            

api = falcon.API()
api.add_route('/event', EventResource())
