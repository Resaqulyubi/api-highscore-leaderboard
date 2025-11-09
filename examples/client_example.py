"""
Example client code showing how to use the HighScore API from a game
"""
import sys
import os
import requests
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = None  # Will be set after creating game


def create_game():
    """Step 1: Create a game and get API key"""
    print("Creating game...")
    
    response = requests.post(
        f"{API_BASE_URL}/games",
        json={
            "name": "Space Shooter Pro",
            "description": "An awesome space shooter game"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"[SUCCESS] Game created!")
        print(f"   Game ID: {data['id']}")
        print(f"   API Key: {data['api_key']}")
        print(f"   [!] Save this API key - it won't be shown again!\n")
        return data['api_key']
    else:
        print(f"[ERROR] {response.text}")
        return None


def submit_score(api_key, player_name, score, game_metadata=None):
    """Step 2: Submit a player's score"""
    print(f"Submitting score for {player_name}...")
    
    headers = {"X-API-Key": api_key}
    data = {
        "player_name": player_name,
        "score": score
    }
    
    if game_metadata:
        data["game_metadata"] = game_metadata
    
    response = requests.post(
        f"{API_BASE_URL}/scores",
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"[SUCCESS] Score submitted! ID: {result['id']}\n")
        return result
    else:
        print(f"[ERROR] {response.text}")
        return None


def get_leaderboard(api_key, limit=10, period=None):
    """Step 3: Get the leaderboard"""
    print(f"Fetching leaderboard...")
    
    headers = {"X-API-Key": api_key}
    params = {"limit": limit}
    
    if period:
        params["period"] = period
    
    response = requests.get(
        f"{API_BASE_URL}/leaderboard",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Leaderboard for '{data['game_name']}':")
        print(f"   Total players: {data['total_entries']}")
        print(f"\n   {'Rank':<6} {'Player':<20} {'Score':<10}")
        print(f"   {'-'*36}")
        
        for entry in data['entries']:
            print(f"   #{entry['rank']:<5} {entry['player_name']:<20} {entry['score']:<10}")
        
        print()
        return data
    else:
        print(f"[ERROR] {response.text}")
        return None


def get_player_stats(api_key, player_name):
    """Step 4: Get player statistics"""
    print(f"Fetching stats for {player_name}...")
    
    headers = {"X-API-Key": api_key}
    
    response = requests.get(
        f"{API_BASE_URL}/players/{player_name}/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"[SUCCESS] Player Statistics:")
        print(f"   Player: {stats['player_name']}")
        print(f"   Rank: #{stats['rank']}")
        print(f"   Best Score: {stats['best_score']}")
        print(f"   Average Score: {stats['average_score']}")
        print(f"   Total Games: {stats['total_scores']}")
        print(f"   First Played: {stats['first_played']}")
        print(f"   Last Played: {stats['last_played']}")
        print()
        return stats
    else:
        print(f"[ERROR] {response.text}")
        return None


def main():
    """Example usage"""
    print("=" * 50)
    print("HighScore API - Example Client")
    print("=" * 50)
    print()
    
    # Step 1: Create game (only do this once!)
    api_key = create_game()
    
    if not api_key:
        print("Failed to create game. Make sure the API is running!")
        return
    
    # Step 2: Submit some sample scores
    sample_scores = [
        ("ProGamer123", 9500, {"level": 10, "time": 350}),
        ("Player456", 8200, {"level": 9, "time": 420}),
        ("NinjaPlayer", 7800, {"level": 8, "time": 380}),
        ("ProGamer123", 9800, {"level": 11, "time": 340}),  # Same player, better score
        ("CasualGamer", 5500, {"level": 6, "time": 500}),
    ]
    
    for player, score, game_metadata in sample_scores:
        submit_score(api_key, player, score, game_metadata)
    
    # Step 3: Get the leaderboard
    get_leaderboard(api_key, limit=10)
    
    # Step 4: Get player statistics
    get_player_stats(api_key, "ProGamer123")
    
    # Step 5: Get time-based leaderboard
    print("Getting today's leaderboard...")
    get_leaderboard(api_key, limit=5, period="today")
    
    print("=" * 50)
    print("[SUCCESS] Example completed!")
    print(f"[!] Your API Key: {api_key}")
    print(f"[!] Save this key to submit scores from your game!")
    print("=" * 50)


if __name__ == "__main__":
    main()
