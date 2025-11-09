/*
 * Example Unity C# code for integrating with HighScore API
 * Add this script to your game manager object
 */

using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class HighScoreManager : MonoBehaviour
{
    // API Configuration
    private const string API_BASE_URL = "http://localhost:8000/api/v1";
    private const string API_KEY = "your-api-key-here"; // Replace with your actual API key
    
    // Data classes matching API schemas
    [Serializable]
    public class ScoreData
    {
        public string player_name;
        public int score;
        public ScoreMetadata game_metadata;
    }
    
    [Serializable]
    public class ScoreMetadata
    {
        public int level;
        public int kills;
        public float time_played;
    }
    
    [Serializable]
    public class ScoreResponse
    {
        public int id;
        public int game_id;
        public string player_name;
        public int score;
        public string created_at;
    }
    
    [Serializable]
    public class LeaderboardResponse
    {
        public int game_id;
        public string game_name;
        public LeaderboardEntry[] entries;
        public int total_entries;
    }
    
    [Serializable]
    public class LeaderboardEntry
    {
        public int rank;
        public string player_name;
        public int score;
        public string created_at;
    }
    
    /// <summary>
    /// Submit a player's score to the API
    /// </summary>
    public void SubmitScore(string playerName, int score, int level = 0, int kills = 0, float timePlayed = 0)
    {
        StartCoroutine(SubmitScoreCoroutine(playerName, score, level, kills, timePlayed));
    }
    
    private IEnumerator SubmitScoreCoroutine(string playerName, int score, int level, int kills, float timePlayed)
    {
        // Prepare score data
        ScoreData scoreData = new ScoreData
        {
            player_name = playerName,
            score = score,
            game_metadata = new ScoreMetadata
            {
                level = level,
                kills = kills,
                time_played = timePlayed
            }
        };
        
        string jsonData = JsonUtility.ToJson(scoreData);
        
        // Create request
        using (UnityWebRequest request = new UnityWebRequest($"{API_BASE_URL}/scores", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("X-API-Key", API_KEY);
            
            // Send request
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                ScoreResponse response = JsonUtility.FromJson<ScoreResponse>(request.downloadHandler.text);
                Debug.Log($"Score submitted successfully! ID: {response.id}");
                OnScoreSubmitted(response);
            }
            else
            {
                Debug.LogError($"Failed to submit score: {request.error}");
                OnScoreSubmitFailed(request.error);
            }
        }
    }
    
    /// <summary>
    /// Get the leaderboard from the API
    /// </summary>
    public void GetLeaderboard(int limit = 10, string period = null)
    {
        StartCoroutine(GetLeaderboardCoroutine(limit, period));
    }
    
    private IEnumerator GetLeaderboardCoroutine(int limit, string period)
    {
        string url = $"{API_BASE_URL}/leaderboard?limit={limit}";
        if (!string.IsNullOrEmpty(period))
        {
            url += $"&period={period}";
        }
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("X-API-Key", API_KEY);
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                LeaderboardResponse response = JsonUtility.FromJson<LeaderboardResponse>(request.downloadHandler.text);
                Debug.Log($"Leaderboard retrieved! Total entries: {response.total_entries}");
                OnLeaderboardReceived(response);
            }
            else
            {
                Debug.LogError($"Failed to get leaderboard: {request.error}");
                OnLeaderboardFailed(request.error);
            }
        }
    }
    
    // Event handlers - override these or use Unity Events
    protected virtual void OnScoreSubmitted(ScoreResponse response)
    {
        // Handle successful score submission
        Debug.Log($"Player {response.player_name} scored {response.score}!");
    }
    
    protected virtual void OnScoreSubmitFailed(string error)
    {
        // Handle score submission failure
        Debug.LogWarning($"Could not submit score: {error}");
    }
    
    protected virtual void OnLeaderboardReceived(LeaderboardResponse leaderboard)
    {
        // Handle leaderboard data
        Debug.Log($"Top {leaderboard.entries.Length} players:");
        foreach (var entry in leaderboard.entries)
        {
            Debug.Log($"#{entry.rank}: {entry.player_name} - {entry.score}");
        }
    }
    
    protected virtual void OnLeaderboardFailed(string error)
    {
        // Handle leaderboard retrieval failure
        Debug.LogWarning($"Could not get leaderboard: {error}");
    }
    
    // Example usage in your game code:
    void Example()
    {
        // Submit score when game ends
        SubmitScore("Player1", 9500, level: 10, kills: 50, timePlayed: 350.5f);
        
        // Get leaderboard
        GetLeaderboard(10); // Top 10 all-time
        GetLeaderboard(5, "today"); // Top 5 today
    }
}
