"""
Simple test script to verify the HighScore API is working
Run this after starting the API with: python run.py
"""
import sys
import os
import requests

# Fix encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("HighScore API - Simple Test")
print("=" * 60)

# Test 1: Health check
print("\n[TEST 1] Health check...")
try:
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        print("[PASS] API is running!")
    else:
        print(f"[FAIL] Health check failed: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Cannot connect to API: {e}")
    print("Make sure the API is running with: python run.py")
    sys.exit(1)

# Test 2: Create a game
print("\n[TEST 2] Creating a game...")
try:
    response = requests.post(
        f"{API_BASE_URL}/games",
        json={"name": "Test Game", "description": "Automated test"}
    )
    if response.status_code == 201:
        api_key = response.json()["api_key"]
        print(f"[PASS] Game created! API Key: {api_key[:20]}...")
    else:
        print(f"[FAIL] Failed to create game: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Error creating game: {e}")
    sys.exit(1)

# Test 3: Submit scores
print("\n[TEST 3] Submitting scores...")
headers = {"X-API-Key": api_key}
test_scores = [
    ("Alice", 1000),
    ("Bob", 1500),
    ("Charlie", 900),
    ("Alice", 1200),  # Alice plays again with better score
]

try:
    for player, score in test_scores:
        response = requests.post(
            f"{API_BASE_URL}/scores",
            headers=headers,
            json={
                "player_name": player,
                "score": score,
                "game_metadata": {"test": True}
            }
        )
        if response.status_code == 201:
            print(f"  [PASS] {player}: {score}")
        else:
            print(f"  [FAIL] Failed to submit score for {player}")
            sys.exit(1)
except Exception as e:
    print(f"[FAIL] Error submitting scores: {e}")
    sys.exit(1)

# Test 4: Get leaderboard
print("\n[TEST 4] Getting leaderboard...")
try:
    response = requests.get(
        f"{API_BASE_URL}/leaderboard?limit=10",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print(f"[PASS] Leaderboard retrieved!")
        print(f"\n  Rank | Player      | Score")
        print(f"  {'-'*30}")
        for entry in data["entries"]:
            print(f"  #{entry['rank']:<3} | {entry['player_name']:<11} | {entry['score']}")
    else:
        print(f"[FAIL] Failed to get leaderboard: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Error getting leaderboard: {e}")
    sys.exit(1)

# Test 5: Get player stats
print("\n[TEST 5] Getting player statistics...")
try:
    response = requests.get(
        f"{API_BASE_URL}/players/Alice/stats",
        headers=headers
    )
    if response.status_code == 200:
        stats = response.json()
        print(f"[PASS] Player stats retrieved!")
        print(f"  Player: {stats['player_name']}")
        print(f"  Rank: #{stats['rank']}")
        print(f"  Best Score: {stats['best_score']}")
        print(f"  Average Score: {stats['average_score']}")
        print(f"  Total Games: {stats['total_scores']}")
    else:
        print(f"[FAIL] Failed to get player stats: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Error getting player stats: {e}")
    sys.exit(1)

# All tests passed!
print("\n" + "=" * 60)
print("[SUCCESS] All tests passed!")
print("=" * 60)
print(f"\nYour API Key: {api_key}")
print("\nNext steps:")
print("  1. Open http://localhost:8000/docs to see interactive API docs")
print("  2. Check examples/ folder for integration code")
print("  3. Use this API key in your game!")
print("=" * 60)
