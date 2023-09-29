from atproto import Client, models
from time import sleep
import json
import ai
import logging
import sys

logging.basicConfig(level=logging.INFO)

class ATBotServer:
    def __init__(self, settings_path):
        self.settings = self.load_settings(settings_path)
        self.client = Client()
        self.profile = None

    @staticmethod
    def load_settings(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def login(self):
        login_info = self.settings['login']
        self.profile = self.client.login(login_info['username'], login_info['password'])
        logging.info('Logged in as %s', self.profile.display_name)
        
    def reply_to_post(self, text, parent_ref, root_ref=None):
        """
        Send a reply to a post or reply.

        :param text: The reply text.
        :param parent_ref: The reference to the post or reply you are replying to.
        :param root_ref: The reference to the root post. If replying to a root post, this is the same as parent_ref.
        :return: Strong reference to the created reply.p
        """
        if root_ref is None:
            root_ref = parent_ref

        return models.create_strong_ref(
            self.client.send_post(
                text=text,
                reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent_ref, root=root_ref),
            )
        )
    
    # Temporary loop will be replaced with a loop that actually processes notifications correctly. First I need to get the hang of the protocol itself.
    def loop(self):
        self.login()
        while True:
            try:
                last_seen_at = self.client.get_current_time_iso()
                response = self.client.app.bsky.notification.list_notifications()
                for notification in response.notifications:
                    if not notification.is_read:
                        logging.info('Got new notification! Type: %s; from: %s', notification.reason, notification.author.did)
                        if notification.reason == 'mention':
                            post_uri = notification.uri  
                            post = self.client.app.bsky.feed.get_post_thread({"uri": post_uri}).thread.post
                            root_post_ref = models.create_strong_ref(post)
                            if post.author.did != self.profile.did and post.record.reply is None or post.record.reply.parent is None:
                                text = notification.record.text
                                reply = self.reply_to_post(ai.evaluate_question(text), root_post_ref)
                                logging.info('Replied to post %s with reply %s', root_post_ref, reply)
                self.client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
                sleep(self.settings['FETCH_NOTIFICATIONS_DELAY_SEC'])
            except Exception as e:
                logging.error('Error in loop: %s', e)
                sys.exit()