from locust import HttpUser, between, task, User
from locust.user.markov_taskset import MarkovTaskSet, transitions
from client import SocialMediaClient


class MarkovNavigation(MarkovTaskSet):

    def __init__(self, user: User):
        super().__init__(user)
        self.social_media_client = SocialMediaClient(self.client)

    def on_start(self):
        self.social_media_client.login()

    # -----------------------------
    # 1. /feed
    # -----------------------------
    @transitions({
        "like": 67,
        "view_profile": 18,
        "post": 15
    })
    @task
    def view_feed(self):
        self.social_media_client.view_feed()

    # -----------------------------
    # 2. /profile/{user_id}
    # -----------------------------
    @transitions({
        "follow": 68,
        "view_feed": 32
    })
    @task
    def view_profile(self):
        self.social_media_client.view_profile()

    # -----------------------------
    # 3. /follow/{user_id}
    # -----------------------------
    @transitions({
        "view_feed": 100
    })
    @task
    def follow(self):
        self.social_media_client.follow_user()

    # -----------------------------
    # 4. /like/{post_id}
    # -----------------------------
    @transitions({
        "view_profile": 69,
        "view_feed": 31
    })
    @task
    def like(self):
        self.social_media_client.like_post()

    # -----------------------------
    # 5. /post
    # -----------------------------
    @transitions({
        "view_feed": 100
    })
    @task
    def post(self):
        self.social_media_client.create_post()


class MarkovUser(HttpUser):
    tasks = [MarkovNavigation]
    wait_time = between(1, 5)
