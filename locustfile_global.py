"""
Q2.2 - Locust Load Test: Global Load Modeling

Ce fichier de test de charge Locust reproduit la charge utilisateur 
extraite des logs du serveur en utilisant un modèle global.

Statistiques observées dans les logs:
- Taux moyen: 3.36 req/s
- Durée: 304 secondes
- 11 utilisateurs distincts
- Distribution d'endpoints:
  * /feed: 34.5%
  * /like/{post_id}: 23.0%
  * /profile/{user_id}: 21.8%
  * /follow/{user_id}: 14.6%
  * /post: 5.1%

Utilisation:
  locust -f locustfile_global.py --host=http://127.0.0.1:8080
"""

from locust import task, between, TaskSet, User, HttpUser
from client import SocialMediaClient


class GlobalTaskSet(TaskSet):
    
    def __init__(self, user: User):
        super().__init__(user)
        self.social_media_client = SocialMediaClient(self.client)

    def on_start(self):
        self.social_media_client.login()

    @task(35)
    def view_feed_api(self):
        self.social_media_client.view_feed()

    @task(23)
    def like_post_api(self):
        self.social_media_client.like_post()

    @task(22)
    def view_profile_api(self):
        self.social_media_client.view_profile()

    @task(15)
    def follow_user_api(self):
        self.social_media_client.follow_user()

    @task(5)
    def create_post_api(self):
        self.social_media_client.create_post()


class GlobalSocialMediaUser(HttpUser):
    """
    Classe utilisateur simulant un utilisateur du réseau social.
    
    Configuration:
    - wait_time: délai de 1-5 secondes entre les requêtes (comme demandé)
    - tasks: ensemble de tâches GlobalTaskSet
    
    Pour reproduire le taux observé de 3.36 req/s:
    - Avec 11 utilisateurs et délai moyen de 3 secondes
    - Taux approximatif: (11 utilisateurs * 1 requête) / (3 secondes) ≈ 3.67 req/s
    """
    wait_time = between(1, 5)
    tasks = [GlobalTaskSet]
