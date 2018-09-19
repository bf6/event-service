import falcon

class EventResource:
    def on_post(self, req, resp):
        try:
            # Get first hashtag
            hashtag = None
            message_body = req.media['event']['text']
            for word in message_body.split(' '):
                if word.startswith('#'):
                    hashtag = word 
                    break
            if hashtag is None:
                return

            # Get image url
            image_url = None
            if 'attachments' in req.media['event']:
                image_url = req.media['event']['attachments'][0]['image_url']
            else if 'files' in req.media['event']:
                image_url = req.media['event']['files'][0]['url_private']
            if image_url is None:
                return

            # TODO: Post to instagram, internal social feed, facebook, twitter, etc
            print('hashtag: ', hashtag, 'image: ', image_url)
        except:
            pass
            

api = falcon.API()
api.add_route('/event', EventResource())
