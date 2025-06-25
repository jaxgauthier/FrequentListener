// Progressive Difficulty Audio Game JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const guessForm = document.getElementById('guessForm');
    const resultsSection = document.getElementById('resultsSection');
    const resultMessage = document.getElementById('resultMessage');
    const correctAnswer = document.getElementById('correctAnswer');
    const songGuessInput = document.getElementById('songGuess');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
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
        
        tracks.forEach((track, index) => {
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

    // Global function for adding next difficulty level
    window.addNextDifficulty = function() {
        console.log('Adding next difficulty level');
        
        // Check if we're at the last difficulty level
        if (currentDifficulty >= frequencies.length - 1) {
            // Show results since we've gone through all frequencies
            resultsSection.style.display = 'block';
            resultMessage.innerHTML = '<p style="color: orange; font-weight: bold;">You\'ve revealed all difficulty levels. Here\'s the answer:</p>';
            
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
        
        // If we've shown all difficulties, hide the plus button
        if (currentDifficulty >= frequencies.length - 1) {
            document.querySelector('.plus-button-container').style.display = 'none';
        }
    };

    guessForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted');
        
        const formData = new FormData(guessForm);
        const songGuess = formData.get('song_guess');
        
        console.log('Song guess:', songGuess);
        
        fetch('/submit_guess', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            
            if (data.correct) {
                // Show results when they get it right
                resultsSection.style.display = 'block';
                resultMessage.innerHTML = '<p style="color: green; font-weight: bold;">Correct! Well done!</p>';
                correctAnswer.textContent = data.correct_answer;
                // Don't reveal next difficulty if they got it right
            } else {
                // Only show results if they've gone through all frequencies
                if (shouldShowResults()) {
                    resultsSection.style.display = 'block';
                    resultMessage.innerHTML = '<p style="color: red; font-weight: bold;">Incorrect. Here\'s the answer:</p>';
                    correctAnswer.textContent = data.correct_answer;
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
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error submitting guess');
        });
    });
}); 