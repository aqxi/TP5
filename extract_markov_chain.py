"""
Q3.1 - Extraction des données pour modélisation par Chaîne de Markov

Ce script extrait les informations nécessaires pour construire une chaîne de Markov
basée sur les séquences de requêtes observées dans les logs.

Approche:
1. Parse les logs et groupe les requêtes par utilisateur et par ordre temporel
2. Pour chaque utilisateur, construit une séquence d'endpoints
3. Calcule les transitions d'un endpoint à un autre
4. Génère une matrice de probabilités de transition
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
import json

LOG_FILE = "logs.txt"

# Regex pour parser chaque ligne
LOG_PATTERN = re.compile(
    r"\[(.*?)\]\[INFO\]\[(.*?)\]\s+(\w+)\s+(/[\w\/]+)"
)


def normalize_endpoint(endpoint):
    """Normalise les endpoints paramétrés"""
    if endpoint.startswith("/profile/"):
        return "/profile/{user_id}"
    if endpoint.startswith("/like/"):
        return "/like/{post_id}"
    if endpoint.startswith("/follow/"):
        return "/follow/{user_id}"
    return endpoint


def parse_logs_for_markov():
    """
    Parse les logs et groupe les requêtes par utilisateur avec leurs timestamps.
    Retourne un dictionnaire {utilisateur: [(timestamp, endpoint), ...]}
    Filtre les requêtes anonymes et les endpoints /login pour ne garder que les actions authentifiées.
    """
    user_sequences = defaultdict(list)
    
    with open(LOG_FILE, "r", encoding='utf-16') as file:
        for line in file:
            match = LOG_PATTERN.search(line)
            if not match:
                continue
            
            timestamp_str, user, _, endpoint = match.groups()

            # Ignore les actions d'authentification et l'utilisateur anonyme
            if user == "anonymous" or endpoint == "/login":
                continue

            ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            normalized = normalize_endpoint(endpoint)
            
            user_sequences[user].append((ts, normalized))
    
    # Trier les requêtes de chaque utilisateur par timestamp
    for user in user_sequences:
        user_sequences[user].sort(key=lambda x: x[0])
    
    return user_sequences


def build_transition_matrix(user_sequences):
    """
    Construit une matrice de transition en comptant les transitions d'un endpoint à un autre.
    Retourne:
    - transitions: dict {from_endpoint: {to_endpoint: count}}
    - transition_probs: dict {from_endpoint: {to_endpoint: probability}}
    - all_endpoints: set de tous les endpoints uniques
    """
    transitions = defaultdict(Counter)
    all_endpoints = set()
    
    for user, sequence in user_sequences.items():
        endpoints = [ep for _, ep in sequence]
        all_endpoints.update(endpoints)
        
        # Pour chaque paire consécutive d'endpoints
        for i in range(len(endpoints) - 1):
            from_ep = endpoints[i]
            to_ep = endpoints[i + 1]
            transitions[from_ep][to_ep] += 1
    
    # Calculer les probabilités
    transition_probs = {}
    for from_ep in transitions:
        total = sum(transitions[from_ep].values())
        transition_probs[from_ep] = {}
        for to_ep, count in transitions[from_ep].items():
            transition_probs[from_ep][to_ep] = count / total
    
    return transitions, transition_probs, all_endpoints


def calculate_initial_distribution(user_sequences):
    """
    Calcule la distribution initiale (première requête de chaque utilisateur).
    Retourne un dict {endpoint: probability}
    """
    first_endpoints = []
    
    for user, sequence in user_sequences.items():
        if sequence:  # S'il y a au moins une requête
            first_ep = sequence[0][1]  # Premier endpoint de l'utilisateur
            first_endpoints.append(first_ep)
    
    counter = Counter(first_endpoints)
    total = sum(counter.values())
    
    initial_dist = {}
    for ep, count in counter.items():
        initial_dist[ep] = count / total
    
    return initial_dist


def print_transition_matrix(transition_probs, all_endpoints):
    """Affiche la matrice de transition de manière lisible et compacte"""
    sorted_endpoints = sorted(all_endpoints)
    
    print("\n=== Matrice de Transition (Probabilités) ===\n")
    
    for from_ep in sorted_endpoints:
        if from_ep in transition_probs:
            transitions = []
            for to_ep in sorted(transition_probs[from_ep].keys()):
                prob = transition_probs[from_ep][to_ep]
                transitions.append(f"{to_ep}: {prob:.2%}")
            print(f"{from_ep}")
            print(f"  → {', '.join(transitions)}")
        print()




def print_user_sequences(user_sequences):
    """Affiche un résumé court des séquences par utilisateur"""
    print("\n=== Séquences de Requêtes par Utilisateur ===\n")
    for user in sorted(user_sequences.keys()):
        sequence = user_sequences[user]
        endpoints = [ep for _, ep in sequence]
        # Afficher seulement les 10 premières requêtes
        if len(endpoints) > 10:
            short_seq = ' → '.join(endpoints[:10]) + " → ..."
        else:
            short_seq = ' → '.join(endpoints)
        print(f"{user}: {short_seq}")


if __name__ == "__main__":
    print("Parsing les logs et construction de la chaîne de Markov...")
    
    # Étape 1: Parser les logs
    user_sequences = parse_logs_for_markov()
    print(f"✓ {len(user_sequences)} utilisateurs trouvés")
    
    # Étape 2: Construire la matrice de transition
    transitions, transition_probs, all_endpoints = build_transition_matrix(user_sequences)
    print(f"✓ {len(all_endpoints)} endpoints uniques trouvés")
    
    # Étape 3: Calculer la distribution initiale
    initial_dist = calculate_initial_distribution(user_sequences)
    
    # Affichage des résultats
    print("\n" + "="*70)
    print("RÉSULTATS DE L'ANALYSE MARKOV - CHAÎNE DE MARKOV")
    print("="*70)
    
    # Statistiques générales
    total_requests = sum(len(seq) for seq in user_sequences.values())
    total_transitions = sum(sum(trans.values()) for trans in transitions.values())
    
    print("\n📊 Statistiques Générales:")
    print(f"   • Utilisateurs: {len(user_sequences)}")
    print(f"   • Requêtes totales: {total_requests}")
    print(f"   • Transitions observées: {total_transitions}")
    print(f"   • Endpoints uniques: {len(all_endpoints)}")
    
    # Distribution initiale
    print("\n🔀 Distribution Initiale (première requête):")
    for ep in sorted(initial_dist.keys(), key=lambda x: initial_dist[x], reverse=True):
        prob = initial_dist[ep]
        print(f"   {ep}: {prob:.2%}")
    
    # Statistiques des endpoints
    print("\n📈 Statistiques des Endpoints:")
    endpoint_counts = Counter()
    for user, sequence in user_sequences.items():
        for ts, ep in sequence:
            endpoint_counts[ep] += 1
    
    total = sum(endpoint_counts.values())
    for ep in sorted(all_endpoints):
        count = endpoint_counts.get(ep, 0)
        pct = (count / total * 100) if total > 0 else 0
        print(f"   {ep}: {count} ({pct:.1f}%)")
    
    # Séquences d'utilisateurs
    print_user_sequences(user_sequences)
    
    # Matrice de transition
    print_transition_matrix(transition_probs, all_endpoints)
    
    # Export JSON pour utilisation future
    export_data = {
        "initial_distribution": initial_dist,
        "transition_matrix": {
            from_ep: dict(transition_probs[from_ep])
            for from_ep in transition_probs
        },
        "endpoints": list(all_endpoints),
        "statistics": {
            "num_users": len(user_sequences),
            "total_requests": total_requests,
            "total_transitions": total_transitions,
            "num_endpoints": len(all_endpoints)
        }
    }
    
    with open("markov_chain_data.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    print("\n✓ Données exportées dans markov_chain_data.json")
