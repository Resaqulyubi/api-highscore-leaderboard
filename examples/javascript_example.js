/**
 * Example JavaScript/Node.js code for integrating with HighScore API
 * Can be used in web games or Node.js backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'your-api-key-here'; // Replace with your actual API key

/**
 * Submit a score to the API
 */
async function submitScore(playerName, score, game_metadata = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/scores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                player_name: playerName,
                score: score,
                game_metadata: game_metadata
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Score submitted:', data);
        return data;
    } catch (error) {
        console.error('❌ Failed to submit score:', error);
        throw error;
    }
}

/**
 * Get leaderboard from the API
 */
async function getLeaderboard(limit = 10, period = null) {
    try {
        let url = `${API_BASE_URL}/leaderboard?limit=${limit}`;
        if (period) {
            url += `&period=${period}`;
        }

        const response = await fetch(url, {
            headers: {
                'X-API-Key': API_KEY
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('🏆 Leaderboard received:', data);
        return data;
    } catch (error) {
        console.error('❌ Failed to get leaderboard:', error);
        throw error;
    }
}

/**
 * Get player statistics
 */
async function getPlayerStats(playerName) {
    try {
        const response = await fetch(`${API_BASE_URL}/players/${playerName}/stats`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('📊 Player stats:', data);
        return data;
    } catch (error) {
        console.error('❌ Failed to get player stats:', error);
        throw error;
    }
}

/**
 * Display leaderboard in HTML
 */
function displayLeaderboard(leaderboardData) {
    const leaderboardDiv = document.getElementById('leaderboard');
    
    let html = `<h2>🏆 ${leaderboardData.game_name} Leaderboard</h2>`;
    html += '<table><tr><th>Rank</th><th>Player</th><th>Score</th></tr>';
    
    leaderboardData.entries.forEach(entry => {
        html += `<tr>
            <td>#${entry.rank}</td>
            <td>${entry.player_name}</td>
            <td>${entry.score}</td>
        </tr>`;
    });
    
    html += '</table>';
    leaderboardDiv.innerHTML = html;
}

// ========== Example Usage ==========

// Example 1: Submit score when game ends
async function onGameEnd(playerName, finalScore, gameData) {
    const game_metadata = {
        level: gameData.level,
        kills: gameData.kills,
        time: gameData.timePlayed
    };
    
    await submitScore(playerName, finalScore, game_metadata);
}

// Example 2: Load and display leaderboard
async function loadLeaderboard() {
    const leaderboard = await getLeaderboard(10);
    displayLeaderboard(leaderboard);
}

// Example 3: Show player stats
async function showPlayerStats(playerName) {
    const stats = await getPlayerStats(playerName);
    
    console.log(`
        Player: ${stats.player_name}
        Rank: #${stats.rank}
        Best Score: ${stats.best_score}
        Average: ${stats.average_score}
        Games Played: ${stats.total_scores}
    `);
}

// Example 4: Complete flow
async function exampleFlow() {
    // Player finishes game
    const playerName = 'WebGamer123';
    const score = 8500;
    
    // Submit score
    await submitScore(playerName, score, {
        level: 8,
        accuracy: 0.85,
        time: 420
    });
    
    // Get updated leaderboard
    const leaderboard = await getLeaderboard(10);
    displayLeaderboard(leaderboard);
    
    // Show player stats
    await showPlayerStats(playerName);
}

// Run example (uncomment to test)
// exampleFlow();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        submitScore,
        getLeaderboard,
        getPlayerStats,
        displayLeaderboard
    };
}
