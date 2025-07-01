// Progressive Difficulty Audio Game JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Dropdown functionality
    window.toggleDropdown = function() {
        const dropdown = document.getElementById('dropdownMenu');
        dropdown.classList.toggle('show');
    };

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('dropdownMenu');
        const logoBtn = document.querySelector('.logo-btn');
        
        if (!logoBtn.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    });

    // Get DOM elements
    const guessForm = document.getElementById('guessForm');
    const songGuessInput = document.getElementById('songGuess');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const resultsSection = document.getElementById('resultsSection');
    const resultMessage = document.getElementById('resultMessage');
    const correctAnswer = document.getElementById('correctAnswer');
    
    console.log('DOM loaded, form found:', guessForm);
    
    // Track current difficulty level (0 = first frequency, 1 = second, etc.)
    let currentDifficulty = 0;
    let frequencies = [];
    
    // Get available frequencies from the DOM
    function getAvailableFrequencies() {
        const audioPlayers = document.querySelectorAll('.audio-player');
        frequencies = [];
        audioPlayers.forEach(player => {
            const freq = player.id.replace('audio-', '');
            frequencies.push(freq);
        });
        console.log('Available frequencies:', frequencies);
    }
    
    // Search functionality
    let searchTimeout;
    let selectedSuggestionIndex = -1;
    
    // Initialize: get frequencies and show current difficulty
    getAvailableFrequencies();
    showCurrentDifficulty();
    
    // Set initial difficulty level in hidden input
    const difficultyInput = document.getElementById('difficultyLevel');
    if (difficultyInput) {
        difficultyInput.value = currentDifficulty;
    }
    
    // Set initial score (starts at maximum for hardest difficulty)
    const scoreInput = document.getElementById('currentScore');
    if (scoreInput) {
        const initialScore = Math.max(0, 8 - currentDifficulty);
        scoreInput.value = initialScore;
    }
    
    // Function to update score display
    function updateScoreDisplay() {
        const scoreInput = document.getElementById('currentScore');
        const scoreDisplay = document.getElementById('scoreDisplay');
        if (scoreInput && scoreDisplay) {
            scoreDisplay.textContent = scoreInput.value;
        }
    }
    
    // Initialize score display
    updateScoreDisplay();

    // Spotify search functionality
    songGuessInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Hide suggestions if query is too short
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        // Debounce search requests
        searchTimeout = setTimeout(() => {
            searchSpotify(query);
        }, 300);
    });
    
    // Handle keyboard navigation
    songGuessInput.addEventListener('keydown', function(e) {
        const suggestions = searchSuggestions.querySelectorAll('.search-suggestion-item');
        
        if (suggestions.length === 0) return;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
                updateSelectedSuggestion(suggestions);
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
                updateSelectedSuggestion(suggestions);
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
                    selectSuggestion(suggestions[selectedSuggestionIndex]);
                } else {
                    guessForm.dispatchEvent(new Event('submit'));
                }
                break;
            case 'Escape':
                hideSuggestions();
                selectedSuggestionIndex = -1;
                break;
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!songGuessInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            hideSuggestions();
            selectedSuggestionIndex = -1;
        }
    });
    
    function searchSpotify(query) {
        fetch(`/spotify_search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.tracks && data.tracks.length > 0) {
                    showSuggestions(data.tracks);
                } else {
                    hideSuggestions();
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                hideSuggestions();
            });
    }
    
    function showSuggestions(tracks) {
        searchSuggestions.innerHTML = '';
        
        // Limit to first 5 suggestions to keep dropdown small
        const limitedTracks = tracks.slice(0, 5);
        
        limitedTracks.forEach((track, index) => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'search-suggestion-item';
            suggestionItem.innerHTML = `
                <div class="suggestion-title">${track.name}</div>
                <div class="suggestion-artist">${track.artist}</div>
                <div class="suggestion-album">${track.album}</div>
            `;
            
            suggestionItem.addEventListener('click', () => selectSuggestion(suggestionItem));
            suggestionItem.addEventListener('mouseenter', () => {
                selectedSuggestionIndex = index;
                updateSelectedSuggestion(searchSuggestions.querySelectorAll('.search-suggestion-item'));
            });
            
            searchSuggestions.appendChild(suggestionItem);
        });
        
        searchSuggestions.style.display = 'block';
        selectedSuggestionIndex = -1;
    }
    
    function hideSuggestions() {
        searchSuggestions.style.display = 'none';
        searchSuggestions.innerHTML = '';
    }
    
    function updateSelectedSuggestion(suggestions) {
        suggestions.forEach((item, index) => {
            if (index === selectedSuggestionIndex) {
                item.style.backgroundColor = '#e3f2fd';
            } else {
                item.style.backgroundColor = '';
            }
        });
    }
    
    function selectSuggestion(suggestionItem) {
        const title = suggestionItem.querySelector('.suggestion-title').textContent;
        const artist = suggestionItem.querySelector('.suggestion-artist').textContent;
        
        songGuessInput.value = `${title} - ${artist}`;
        hideSuggestions();
        selectedSuggestionIndex = -1;
        
        // Focus back on input
        songGuessInput.focus();
    }

    function showCurrentDifficulty() {
        // Show all difficulties up to the current level
        for (let i = 0; i <= currentDifficulty; i++) {
            const audioPlayer = document.getElementById(`audio-${frequencies[i]}`);
            if (audioPlayer) {
                audioPlayer.style.display = 'block';
            }
        }
        
        // Hide difficulties beyond the current level
        for (let i = currentDifficulty + 1; i < frequencies.length; i++) {
            const audioPlayer = document.getElementById(`audio-${frequencies[i]}`);
            if (audioPlayer) {
                audioPlayer.style.display = 'none';
            }
        }
    }

    function revealNextDifficulty() {
        currentDifficulty++;
        if (currentDifficulty < frequencies.length) {
            // Add a small delay for dramatic effect
            setTimeout(() => {
                const nextAudioPlayer = document.getElementById(`audio-${frequencies[currentDifficulty]}`);
                if (nextAudioPlayer) {
                    nextAudioPlayer.style.display = 'block';
                    // Scroll to the new audio player
                    nextAudioPlayer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 1000);
        }
    }

    function shouldShowResults() {
        // Show results if they got it right OR if they've gone through all frequencies
        return currentDifficulty >= frequencies.length - 1; // -1 because we start at 0
    }

    // Function to show all frequencies (for after correct guess)
    function showAllFrequencies() {
        // Set difficulty to show all frequencies
        currentDifficulty = frequencies.length - 1;
        showCurrentDifficulty();
        
        // Update the hidden difficulty level input
        const difficultyInput = document.getElementById('difficultyLevel');
        if (difficultyInput) {
            difficultyInput.value = currentDifficulty;
        }
        
        // Update the current score to 0 (since they've seen all difficulties)
        const scoreInput = document.getElementById('currentScore');
        if (scoreInput) {
            scoreInput.value = 0;
            updateScoreDisplay();
        }
        
        // Hide the plus button since we've shown all difficulties
        document.querySelector('.plus-button-container').style.display = 'none';
    }

    // Global function for adding next difficulty level
    window.addNextDifficulty = function() {
        console.log('Adding next difficulty level');
        
        // Check if we're at the last difficulty level
        if (currentDifficulty >= frequencies.length - 1) {
            // Show results since we've gone through all frequencies
            resultsSection.style.display = 'block';
            resultMessage.innerHTML = '<p style="color: orange; font-weight: bold;">You\'ve revealed all difficulty levels. Here\'s the answer:</p>';
            
            // Show stats section after all difficulties revealed
            const statsSection = document.querySelector('.user-stats-section');
            if (statsSection) {
                statsSection.style.display = 'block';
            }
            
            // Get the correct answer from the server
            fetch('/submit_guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    song_title: 'Mr Brightside',
                    artist: 'The Killers',
                    guess: 'skip_all'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.correct) {
                    correctAnswer.innerHTML = `
                        <h4>🎉 Correct!</h4>
                        <p>The song is: ${data.song_title} by ${data.artist}</p>
                    `;
                } else {
                    correctAnswer.innerHTML = `
                        <h4>❌ Incorrect</h4>
                        <p>The correct answer is: ${data.song_title} by ${data.artist}</p>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                correctAnswer.innerHTML = '<p>Error getting answer</p>';
            });
            
            // Hide the plus button since we've shown all difficulties
            document.querySelector('.plus-button-container').style.display = 'none';
            return;
        }
        
        // Move to next difficulty
        currentDifficulty++;
        showCurrentDifficulty();
        
        // Update the hidden difficulty level input
        const difficultyInput = document.getElementById('difficultyLevel');
        if (difficultyInput) {
            difficultyInput.value = currentDifficulty;
        }
        
        // Update the current score (decreases with each difficulty level)
        const scoreInput = document.getElementById('currentScore');
        if (scoreInput) {
            // Score starts at 7 for hardest difficulty (0 difficulty level)
            // and decreases by 1 for each easier level revealed
            const newScore = Math.max(0, 8 - currentDifficulty);
            scoreInput.value = newScore;
            updateScoreDisplay();
        }
        
        // If we've shown all difficulties, hide the plus button
        if (currentDifficulty >= frequencies.length - 1) {
            document.querySelector('.plus-button-container').style.display = 'none';
        }
    };

    // Helper to update the stats section dynamically
    async function updateStatsSection() {
        const statsSection = document.querySelector('.user-stats-section');
        if (!statsSection) return;
        // Fetch latest stats from backend
        const res = await fetch('/current_stats');
        const data = await res.json();
        if (!data.success) return;
        const stats = data.stats;
        const song = data.song;
        // Update average score (global)
        const avgScoreElem = statsSection.querySelector('.average-score-value');
        if (avgScoreElem) {
            avgScoreElem.textContent = stats.song_stats.average_score.toFixed(1);
        }
        // Update explanation
        const avgExpElem = statsSection.querySelector('.average-score-explanation small');
        if (avgExpElem) {
            avgExpElem.textContent = `Average score for ${song.title} by ${song.artist}`;
        }
        // Update bar graph (individual)
        for (let score = 0; score < 8; score++) {
            const bar = statsSection.querySelector(`.bar-group:nth-child(${score+1}) .bar`);
            const count = statsSection.querySelector(`.bar-group:nth-child(${score+1}) .bar-count`);
            if (bar) {
                const pct = stats.individual_stats.max_count > 0 ? (stats.individual_stats.points_distribution[score] || 0) / stats.individual_stats.max_count * 100 : 0;
                bar.style.height = pct + '%';
            }
            if (count) {
                count.textContent = stats.individual_stats.points_distribution[score] || 0;
            }
        }
        // Show/hide already played message
        const alreadyMsg = statsSection.querySelector('.already-played-message');
        if (alreadyMsg) {
            alreadyMsg.style.display = stats.has_played_current ? 'block' : 'none';
        }
        // Show stats section
        statsSection.style.display = 'block';
        // Hide guess UI if already played
        if (stats.has_played_current) {
            if (guessForm) guessForm.style.display = 'none';
            const plusBtn = document.querySelector('.plus-button-container');
            if (plusBtn) plusBtn.style.display = 'none';
        }
    }

    // On page load, check if user has already played and show stats if so
    async function checkIfAlreadyPlayed() {
        try {
            const res = await fetch('/current_stats');
            const data = await res.json();
            if (data.success && data.stats.has_played_current) {
                // User has already played this song, show all frequencies and stats
                showAllFrequencies();
                await updateStatsSection();
            }
        } catch (error) {
            console.error('Error checking if already played:', error);
        }
    }

    // Check on page load
    checkIfAlreadyPlayed();

    guessForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');
        const formData = new FormData(guessForm);
        const songGuess = formData.get('song_guess');
        const difficultyLevel = formData.get('difficulty_level');
        console.log('Song guess:', songGuess);
        
        const response = await fetch('/submit_guess', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                song_guess: songGuess,
                difficulty_level: parseInt(difficultyLevel) || 0
            })
        });
        const data = await response.json();
        console.log('Response data:', data);
        
        // Check if user has already played this song
        if (data.already_played) {
            resultsSection.style.display = 'block';
            resultMessage.innerHTML = `<p style="color: orange; font-weight: bold;">${data.message}</p>`;
            correctAnswer.textContent = data.correct_answer;
            
            // Show stats section since they've already played
            await updateStatsSection();
            return;
        }
        
        if (data.correct) {
            // Show results when they get it right
            resultsSection.style.display = 'block';
            resultMessage.innerHTML = `<p style="color: green; font-weight: bold;">Correct! Well done! Score: ${data.score}</p>`;
            correctAnswer.textContent = data.correct_answer;
            // Show stats section after correct guess
            await updateStatsSection();
            // Show all frequencies after correct guess
            showAllFrequencies();
        } else {
            // Decrease score for incorrect guess (for all users)
            const scoreInput = document.getElementById('currentScore');
            if (scoreInput) {
                const currentScore = parseInt(scoreInput.value);
                const newScore = Math.max(0, currentScore - 1);
                scoreInput.value = newScore;
                updateScoreDisplay();
            }
            
            // Only show results if they've gone through all frequencies
            if (shouldShowResults()) {
                resultsSection.style.display = 'block';
                resultMessage.innerHTML = '<p style="color: red; font-weight: bold;">Incorrect. Here\'s the answer:</p>';
                correctAnswer.textContent = data.correct_answer;
                // Show stats section after all difficulties revealed
                await updateStatsSection();
            } else {
                // Hide results section and just show a simple message
                resultsSection.style.display = 'none';
                // Show a temporary message (optional)
                const tempMessage = document.createElement('div');
                tempMessage.innerHTML = '<p style="color: red; font-weight: bold; text-align: center; margin: 1rem 0;">Incorrect. Try again!</p>';
                tempMessage.id = 'tempMessage';
                
                // Remove any existing temp message
                const existingTemp = document.getElementById('tempMessage');
                if (existingTemp) {
                    existingTemp.remove();
                }
                
                // Insert temp message after the form
                guessForm.parentNode.insertBefore(tempMessage, guessForm.nextSibling);
                
                // Remove temp message after 2 seconds
                setTimeout(() => {
                    const tempMsg = document.getElementById('tempMessage');
                    if (tempMsg) {
                        tempMsg.remove();
                    }
                }, 2000);
            }
            // Reveal next difficulty level after incorrect guess
            revealNextDifficulty();
        }
        
        // Clear the form for the next guess
        guessForm.reset();
    });

    // --- Hybrid State Persistence for Revealed Audio Players ---
    // Assumes a global variable currentSongId and isLoggedIn are available (set in template)

    function getRevealedFrequencies() {
        // Get all revealed audio player frequencies (as strings)
        const revealed = [];
        document.querySelectorAll('.audio-player').forEach(function(player) {
            if (player.style.display !== 'none') {
                const freq = player.id.replace('audio-', '');
                revealed.push(freq);
            }
        });
        return revealed;
    }

    function setRevealedFrequencies(freqs) {
        // Hide all, then show those in freqs
        document.querySelectorAll('.audio-player').forEach(function(player, idx) {
            const freq = player.id.replace('audio-', '');
            if (freqs.includes(freq)) {
                player.style.display = '';
            } else {
                player.style.display = 'none';
            }
        });
        // Update currentDifficulty to match revealed
        if (window.frequencies && Array.isArray(window.frequencies)) {
            window.currentDifficulty = freqs.length - 1;
        } else if (typeof currentDifficulty !== 'undefined') {
            currentDifficulty = freqs.length - 1;
        }
        // Update hidden inputs
        var difficultyInput = document.getElementById('difficultyLevel');
        if (difficultyInput) difficultyInput.value = freqs.length - 1;
        var scoreInput = document.getElementById('currentScore');
        var score = Math.max(8 - (freqs.length - 1), 1);
        if (scoreInput) scoreInput.value = score;
        // Update score display
        var scoreEl = document.getElementById('scoreDisplay');
        if (scoreEl) scoreEl.textContent = score;
    }

    function savePlayerState() {
        const revealed = getRevealedFrequencies();
        if (window.isLoggedIn) {
            // Save to backend
            fetch('/api/save_player_state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song_id: window.currentSongId, revealed_frequencies: revealed })
            });
        } else {
            // Save to localStorage
            const key = 'revealedPlayers_' + window.currentSongId;
            localStorage.setItem(key, JSON.stringify(revealed));
        }
    }

    function loadPlayerState() {
        if (window.isLoggedIn) {
            // Load from backend
            fetch('/api/get_player_state?song_id=' + window.currentSongId)
                .then(resp => resp.json())
                .then(data => {
                    if (data.success && Array.isArray(data.revealed_frequencies) && data.revealed_frequencies.length > 0) {
                        setRevealedFrequencies(data.revealed_frequencies);
                    } else {
                        // Default: show only the first
                        setRevealedFrequencies([document.querySelector('.audio-player').id.replace('audio-', '')]);
                    }
                });
        } else {
            // Load from localStorage
            const key = 'revealedPlayers_' + window.currentSongId;
            const val = localStorage.getItem(key);
            if (val) {
                try {
                    const arr = JSON.parse(val);
                    if (Array.isArray(arr) && arr.length > 0) {
                        setRevealedFrequencies(arr);
                        return;
                    }
                } catch {}
            }
            // Default: show only the first
            setRevealedFrequencies([document.querySelector('.audio-player').id.replace('audio-', '')]);
        }
    }

    // Patch addNextDifficulty to save state after revealing
    const origAddNextDifficulty = window.addNextDifficulty;
    window.addNextDifficulty = function() {
        if (typeof origAddNextDifficulty === 'function') origAddNextDifficulty();
        savePlayerState();
    };

    // Set window.currentSongId and window.isLoggedIn from template context
    // (You need to add these variables in your user.html template)
    loadPlayerState();

    // Custom audio player logic
    document.querySelectorAll('.custom-audio-player').forEach(function(wrapper) {
        var audioId = wrapper.getAttribute('data-audio-id');
        var audio = document.getElementById(audioId);
        var playBtn = wrapper.querySelector('.custom-audio-play');
        var iconSpan = playBtn.querySelector('.custom-audio-icon');
        var timeDisplay = wrapper.querySelector('.custom-audio-time');
        var progress = wrapper.querySelector('.custom-audio-progress');
        if (!audio || !playBtn || !iconSpan || !timeDisplay || !progress) return;

        // SVGs for play and pause
        var playSVG = '<svg class="icon-play" width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"><polygon points="5,3 19,11 5,19" fill="currentColor"/></svg>';
        var pauseSVG = '<svg class="icon-pause" width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="3" width="4" height="16" fill="currentColor"/><rect x="13" y="3" width="4" height="16" fill="currentColor"/></svg>';

        // Play/pause logic
        playBtn.addEventListener('click', function() {
            if (audio.paused) {
                audio.play();
            } else {
                audio.pause();
            }
        });
        audio.addEventListener('play', function() {
            playBtn.setAttribute('data-state', 'pause');
            iconSpan.innerHTML = pauseSVG;
        });
        audio.addEventListener('pause', function() {
            playBtn.setAttribute('data-state', 'play');
            iconSpan.innerHTML = playSVG;
        });
        // Time update
        audio.addEventListener('timeupdate', function() {
            var cur = Math.floor(audio.currentTime);
            var dur = Math.floor(audio.duration) || 0;
            timeDisplay.textContent = formatTime(cur) + ' / ' + formatTime(dur);
            var percent = (audio.currentTime / (audio.duration || 1)) * 100;
            progress.value = percent;
        });
        // Progress bar seeking
        progress.addEventListener('input', function() {
            var seekTime = (progress.value / 100) * (audio.duration || 1);
            audio.currentTime = seekTime;
        });
        // Reset on end
        audio.addEventListener('ended', function() {
            playBtn.setAttribute('data-state', 'play');
            iconSpan.innerHTML = playSVG;
            progress.value = 0;
        });
        // Init
        audio.addEventListener('loadedmetadata', function() {
            var dur = Math.floor(audio.duration) || 0;
            timeDisplay.textContent = '0:00 / ' + formatTime(dur);
        });
    });
    function formatTime(sec) {
        var m = Math.floor(sec / 60);
        var s = Math.floor(sec % 60);
        return m + ':' + (s < 10 ? '0' : '') + s;
    }
}); 