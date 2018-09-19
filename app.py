import os
import shutil
import uuid

import falcon
import requests
from InstagramAPI import InstagramAPI

insta = InstagramAPI(os.environ.get('INSTAGRAM_USER'), os.environ.get('INSTAGRAM_PASS'))
insta.login()

class EventResource:
    def on_post(self, req, resp):
        try:
            # Get first hashtag
            hashtag = None
            message_body = req.media['event']['message']['text']
            for word in message_body.split(' '):
                if word.startswith('#'):
                    hashtag = word 
                    break
            if hashtag is None:
                return

            # Get image url
            image_url = None
            if 'attachments' in req.media['event']['message']:
                image_url = req.media['event']['message']['attachments'][0]['image_url']
            elif 'files' in req.media['event']['message']:
                image_url = req.media['event']['message']['files'][0]['url_private']
            if image_url is None:
                return
            import pdb; pdb.set_trace()
            r = requests.get(image_url, stream=True, headers={'Authorization': 'Bearer {}'.format(os.environ.get('SLACK_ACCESS_TOKEN'))})
            if r.status_code == 200:
                path = '{}'.format(uuid.uuid4().hex)
                with open(path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                insta.uploadPhoto(path, caption=hashtag)
                os.remove(path)
        except:
            pass
            

api = falcon.API()
api.add_route('/event', EventResource())
