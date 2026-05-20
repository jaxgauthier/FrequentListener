// Fouriele player — game logic + circular UI
document.addEventListener('DOMContentLoaded', function() {
    const MAX_SCORE = window.maxScore || 8;

    const TIER_LABELS = {
        '500': 'Hardest (500 Hz)',
        '1000': 'Very hard (1000 Hz)',
        '1500': 'Hard (1500 Hz)',
        '2000': 'Medium-hard (2000 Hz)',
        '2500': 'Medium (2500 Hz)',
        '3500': 'Medium-easy (3500 Hz)',
        '5000': 'Easy (5000 Hz)',
        '7500': 'Easiest (7500 Hz)',
    };

    // User menu dropdown
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenuDropdown = document.getElementById('userMenuDropdown');
    if (userMenuBtn && userMenuDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const open = !userMenuDropdown.classList.contains('hidden');
            userMenuDropdown.classList.toggle('hidden', open);
            userMenuBtn.setAttribute('aria-expanded', open ? 'false' : 'true');
        });
        document.addEventListener('click', function() {
            userMenuDropdown.classList.add('hidden');
            userMenuBtn.setAttribute('aria-expanded', 'false');
        });
    }

    function showGuestNotice(message) {
        if (window.isLoggedIn) return;
        const banner = document.getElementById('guestBanner');
        if (!banner) return;
        const textEl = banner.querySelector('.guest-banner-text');
        if (message && textEl) {
            textEl.textContent = message + ' ';
        }
        banner.classList.remove('hidden');
    }

    // Get DOM elements
    const guessForm = document.getElementById('guessForm');
    if (!guessForm) return;

    const songGuessInput = document.getElementById('songGuess');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const resultsSection = document.getElementById('resultsSection');
    const resultMessage = document.getElementById('resultMessage');
    const correctAnswer = document.getElementById('correctAnswer');
    
    // Track current difficulty level (0 = first frequency, 1 = second, etc.)
    let currentDifficulty = 0;
    let frequencies = [];
    
    function getAvailableFrequencies() {
        const audioPlayers = document.querySelectorAll('.audio-player');
        frequencies = [];
        audioPlayers.forEach(player => {
            const freq = player.id.replace('audio-', '');
            frequencies.push(freq);
        });
        frequencies.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function getActiveAudio() {
        if (!frequencies.length) return null;
        const freq = frequencies[Math.min(currentDifficulty, frequencies.length - 1)];
        return document.getElementById('audio-el-' + freq);
    }

    function buildRingPath(ringIndex) {
        const baseRadius = 40 + ringIndex * 18;
        const waveCount = 4 + ringIndex;
        const amplitude = 8 + ringIndex * 2;
        const rotation = ringIndex * 15;
        const points = [];
        for (let i = 0; i <= 100; i++) {
            const angle = (i / 100) * Math.PI * 2;
            const wave = Math.sin(angle * waveCount + rotation * 0.1) * amplitude;
            const r = baseRadius + wave;
            const x = 150 + r * Math.cos(angle);
            const y = 150 + r * Math.sin(angle);
            points.push(x + ',' + y);
        }
        return 'M ' + points[0] + ' L ' + points.slice(1).join(' L ') + ' Z';
    }

    function updateFrequencyRings() {
        const group = document.getElementById('frequencyRingsGroup');
        if (!group) return;
        group.innerHTML = '';
        const ringCount = Math.min(currentDifficulty + 1, MAX_SCORE);
        for (let i = 0; i < ringCount; i++) {
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', buildRingPath(i));
            path.setAttribute('class', 'ring-path');
            path.setAttribute('stroke', 'url(#ring-gradient-' + ((i % 3) + 1) + ')');
            path.style.animationDuration = (20 + i * 5) + 's';
            group.appendChild(path);
        }
    }

    function updateTierLabel() {
        const el = document.getElementById('tierLabel');
        if (!el || !frequencies.length) return;
        const freq = frequencies[Math.min(currentDifficulty, frequencies.length - 1)];
        el.textContent = TIER_LABELS[freq] || freq + ' Hz';
    }

    function updateRevealButton() {
        const btn = document.getElementById('revealBtn');
        if (!btn) return;
        const atMax = currentDifficulty >= frequencies.length - 1;
        btn.disabled = atMax;
        btn.style.visibility = atMax ? 'hidden' : 'visible';
    }

    function setCenterPlayState(playing) {
        const playIcon = document.getElementById('centerPlayIcon');
        const pauseIcon = document.getElementById('centerPauseIcon');
        if (!playIcon || !pauseIcon) return;
        if (playing) {
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
        } else {
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
        }
    }

    function stopAllPlayback() {
        document.querySelectorAll('.audio-sources audio').forEach(function(a) {
            a.pause();
            a.currentTime = 0;
        });
        setCenterPlayState(false);
    }

    function refreshPlayerUI() {
        updateFrequencyRings();
        updateScoreDisplay();
        updateTierLabel();
        updateRevealButton();
    }

    function initCenterPlayer() {
        const centerPlayBtn = document.getElementById('centerPlayBtn');
        if (!centerPlayBtn) return;

        centerPlayBtn.addEventListener('click', function() {
            const audio = getActiveAudio();
            if (!audio) return;
            document.querySelectorAll('.audio-sources audio').forEach(function(a) {
                if (a !== audio) a.pause();
            });
            if (audio.paused) {
                audio.play().catch(function(err) { console.error('Playback failed:', err); });
            } else {
                audio.pause();
            }
        });

        document.querySelectorAll('.audio-sources audio').forEach(function(audio) {
            if (audio._fourieleBound) return;
            audio._fourieleBound = true;
            audio.addEventListener('play', function() {
                if (audio === getActiveAudio()) setCenterPlayState(true);
            });
            audio.addEventListener('pause', function() {
                if (audio === getActiveAudio()) setCenterPlayState(false);
            });
            audio.addEventListener('ended', function() {
                setCenterPlayState(false);
            });
        });
    }
    
    // Search functionality
    let searchTimeout;
    let selectedSuggestionIndex = -1;
    
    getAvailableFrequencies();
    showCurrentDifficulty();
    initCenterPlayer();
    refreshPlayerUI();
    
    // Set initial difficulty level in hidden input
    const difficultyInput = document.getElementById('difficultyLevel');
    if (difficultyInput) {
        difficultyInput.value = currentDifficulty;
    }
    
    // Set initial score (starts at maximum for hardest difficulty)
    const scoreInput = document.getElementById('currentScore');
    if (scoreInput) {
        const initialScore = Math.max(0, MAX_SCORE - currentDifficulty);
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
                item.style.backgroundColor = 'rgba(51, 65, 85, 0.9)';
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
        refreshPlayerUI();
    }

    function revealNextDifficulty() {
        stopAllPlayback();
        currentDifficulty++;
        const difficultyInput = document.getElementById('difficultyLevel');
        if (difficultyInput) {
            difficultyInput.value = currentDifficulty;
        }
        const scoreInput = document.getElementById('currentScore');
        if (scoreInput) {
            scoreInput.value = Math.max(0, 8 - currentDifficulty);
            updateScoreDisplay();
        }
        if (currentDifficulty < frequencies.length) {
            setTimeout(() => {
                const nextAudioPlayer = document.getElementById(`audio-${frequencies[currentDifficulty]}`);
                if (nextAudioPlayer) {
                    nextAudioPlayer.style.display = 'block';
                    nextAudioPlayer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 1000);
        }
        refreshPlayerUI();
        savePlayerState();
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
        
        updateRevealButton();
        refreshPlayerUI();
    }

    window.addNextDifficulty = function() {
        console.log('Adding next difficulty level');
        stopAllPlayback();

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
            
            // Reveal answer without POST /submit_guess (avoids wrong payload + bogus stats rows)
            fetch('/current_stats')
                .then(response => response.json())
                .then(async (data) => {
                    if (data.success && data.song) {
                        const t = data.song.title;
                        const a = data.song.artist;
                        correctAnswer.innerHTML = `<p>The song is: <strong>${t}</strong> by <strong>${a}</strong></p>`;
                        await updateStatsSection();
                    } else {
                        correctAnswer.innerHTML = '<p>Could not load the answer.</p>';
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    correctAnswer.innerHTML = '<p>Error getting answer</p>';
                });
            
            updateRevealButton();
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
            const newScore = Math.max(0, MAX_SCORE - currentDifficulty);
            scoreInput.value = newScore;
            updateScoreDisplay();
        }
        refreshPlayerUI();
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
        if (avgScoreElem && stats.song_stats) {
            avgScoreElem.textContent = stats.song_stats.average_score.toFixed(1);
        }
        // Update explanation
        const avgExpElem = statsSection.querySelector('.average-score-explanation small');
        if (avgExpElem && song) {
            avgExpElem.textContent = `${song.title} by ${song.artist}`;
        }
        // Update bar graph (logged-in users only)
        const pointsBlock = statsSection.querySelector('.points-distribution');
        if (window.isLoggedIn && stats.individual_stats && pointsBlock) {
            const dist = stats.individual_stats.points_distribution || {};
            const maxCount = stats.individual_stats.max_count || 1;
            for (let score = 0; score < 9; score++) {
                const bar = statsSection.querySelector(`.bar-group:nth-child(${score + 1}) .bar`);
                const count = statsSection.querySelector(`.bar-group:nth-child(${score + 1}) .bar-count`);
                const val = dist[score] || dist[String(score)] || 0;
                if (bar) {
                    const pct = maxCount > 0 ? (val / maxCount) * 100 : 0;
                    bar.style.height = pct + '%';
                }
                if (count) {
                    count.textContent = val;
                }
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
            const revealBtn = document.getElementById('revealBtn');
            if (revealBtn) revealBtn.style.display = 'none';
            const playerSection = document.querySelector('.player-section');
            if (playerSection) playerSection.style.opacity = '0.6';
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
        stopAllPlayback();
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
            resultMessage.innerHTML = `<p style="color: orange; font-weight: bold;">${data.message || 'You already played this song.'}</p>`;
            correctAnswer.textContent = data.correct_answer;
            await updateStatsSection();
            return;
        }

        if (data.guest && data.message) {
            showGuestNotice(data.message);
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
        var score = Math.max(MAX_SCORE - (freqs.length - 1), 0);
        if (scoreInput) scoreInput.value = score;
        refreshPlayerUI();
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
    if (document.querySelector('.audio-sources')) {
        loadPlayerState();
    }
}); 