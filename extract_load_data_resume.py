import re
from collections import defaultdict
from datetime import datetime

LOG_FILE = "logs.txt"

# Regex pour parser chaque ligne
LOG_PATTERN = re.compile(
    r"\[(.*?)\]\[INFO\]\[(.*?)\]\s+(\w+)\s+(/[\w\/]+)"
)

# Normalisation des endpoints paramétrés
def normalize_endpoint(endpoint):
    # profils : /profile/42
    if endpoint.startswith("/profile/"):
        return "/profile/{user_id}"

    # likes : /like/77
    if endpoint.startswith("/like/"):
        return "/like/{post_id}"

    # follows : /follow/22
        # follows : /follow/22
    if endpoint.startswith("/follow/"):
        return "/follow/{user_id}"

    return endpoint  # endpoints statiques


def parse_logs():
    endpoint_counts = defaultdict(int)
    method_counts = defaultdict(int)
    users = set()
    timestamps = []

    with open(LOG_FILE, "r", encoding='utf-16') as file:
        for line in file:
            match = LOG_PATTERN.search(line)
            if not match:
                continue

            timestamp_str, user, method, endpoint = match.groups()

            # parsing du timestamp
            ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamps.append(ts)

            users.add(user)
            method_counts[method] += 1

            normalized = normalize_endpoint(endpoint)
            endpoint_counts[normalized] += 1

    return endpoint_counts, method_counts, users, timestamps


if __name__ == "__main__":
    endpoint_counts, method_counts, users, timestamps = parse_logs()

    # Durée totale
    start_time = min(timestamps)
    end_time = max(timestamps)
    duration_sec = (end_time - start_time).total_seconds()

    total_requests = sum(endpoint_counts.values())

    print("\n=== Extraction de la charge globale ===")
    print(f"Première requête : {start_time}")
    print(f"Dernière requête : {end_time}")
    print(f"Durée totale observée : {duration_sec:.0f} sec")
    print(f"\nTotal de requêtes : {total_requests}")
    print(f"Taux moyen : {total_requests / duration_sec:.2f} req/s")

    print("\n--- Utilisateurs distincts ---")
    for u in sorted(users):
        print(f" - {u}")
    print(f"Total : {len(users)} utilisateurs")

    print("\n--- Méthodes HTTP ---")
    for method, count in method_counts.items():
        print(f"{method}: {count}")

    print("\n--- Requêtes par endpoint (normalisé) ---")
    for ep, count in endpoint_counts.items():
        print(f"{ep}: {count}")
