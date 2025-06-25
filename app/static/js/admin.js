// Basic Admin JavaScript
let searchTimeout;
let selectedSuggestionIndex = -1;
let selectedSpotifyTrack = null;

// Spotify search functionality
document.addEventListener('DOMContentLoaded', function() {
    const spotifySearch = document.getElementById('spotifySearch');
    const spotifySuggestions = document.getElementById('spotifySuggestions');
    const selectedSongInfo = document.getElementById('selectedSongInfo');
    const songDetails = document.getElementById('songDetails');
    const processSongBtn = document.getElementById('processSongBtn');
    const processingStatus = document.getElementById('processingStatus');

    if (spotifySearch) {
        spotifySearch.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Clear previous timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            // Hide suggestions if query is too short
            if (query.length < 2) {
                hideSpotifySuggestions();
                return;
            }
            
            // Debounce search requests
            searchTimeout = setTimeout(() => {
                searchSpotify(query);
            }, 300);
        });

        // Handle keyboard navigation
        spotifySearch.addEventListener('keydown', function(e) {
            const suggestions = spotifySuggestions.querySelectorAll('.spotify-suggestion-item');
            
            if (suggestions.length === 0) return;
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
                    updateSelectedSpotifySuggestion(suggestions);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
                    updateSelectedSpotifySuggestion(suggestions);
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
                        selectSpotifySuggestion(suggestions[selectedSuggestionIndex]);
                    }
                    break;
                case 'Escape':
                    hideSpotifySuggestions();
                    selectedSuggestionIndex = -1;
                    break;
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!spotifySearch.contains(e.target) && !spotifySuggestions.contains(e.target)) {
                hideSpotifySuggestions();
                selectedSuggestionIndex = -1;
            }
        });
    }

    if (processSongBtn) {
        processSongBtn.addEventListener('click', function() {
            if (selectedSpotifyTrack) {
                processSpotifySong(selectedSpotifyTrack);
            }
        });
    }

    // Time range handling
    const startTimeInput = document.getElementById('startTime');
    const endTimeInput = document.getElementById('endTime');
    const timeSpanDisplay = document.getElementById('timeSpan');

    if (startTimeInput && endTimeInput && timeSpanDisplay) {
        function updateTimeSpan() {
            const start = parseFloat(startTimeInput.value) || 0;
            const end = parseFloat(endTimeInput.value) || 10;
            const span = Math.max(0, end - start);
            timeSpanDisplay.textContent = span.toFixed(1);
        }

        startTimeInput.addEventListener('input', updateTimeSpan);
        endTimeInput.addEventListener('input', updateTimeSpan);
        
        // Initialize time span
        updateTimeSpan();
    }

    function searchSpotify(query) {
        fetch(`/spotify_search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.tracks && data.tracks.length > 0) {
                    showSpotifySuggestions(data.tracks);
                } else {
                    hideSpotifySuggestions();
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                hideSpotifySuggestions();
            });
    }
    
    function showSpotifySuggestions(tracks) {
        spotifySuggestions.innerHTML = '';
        
        // Limit to first 5 suggestions to keep dropdown small
        const limitedTracks = tracks.slice(0, 5);
        
        limitedTracks.forEach((track, index) => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'spotify-suggestion-item';
            suggestionItem.innerHTML = `
                <div class="suggestion-title">${track.name}</div>
                <div class="suggestion-artist">${track.artist}</div>
                <div class="suggestion-album">${track.album}</div>
            `;
            
            suggestionItem.addEventListener('click', () => selectSpotifySuggestion(suggestionItem, track));
            suggestionItem.addEventListener('mouseenter', () => {
                selectedSuggestionIndex = index;
                updateSelectedSpotifySuggestion(spotifySuggestions.querySelectorAll('.spotify-suggestion-item'));
            });
            
            spotifySuggestions.appendChild(suggestionItem);
        });
        
        spotifySuggestions.style.display = 'block';
        selectedSuggestionIndex = -1;
    }
    
    function hideSpotifySuggestions() {
        spotifySuggestions.style.display = 'none';
        spotifySuggestions.innerHTML = '';
    }
    
    function updateSelectedSpotifySuggestion(suggestions) {
        suggestions.forEach((item, index) => {
            if (index === selectedSuggestionIndex) {
                item.style.backgroundColor = '#e3f2fd';
            } else {
                item.style.backgroundColor = '';
            }
        });
    }
    
    function selectSpotifySuggestion(suggestionItem, track) {
        selectedSpotifyTrack = track;
        
        // Update the search input
        spotifySearch.value = `${track.name} - ${track.artist}`;
        hideSpotifySuggestions();
        selectedSuggestionIndex = -1;
        
        // Show song details
        songDetails.innerHTML = `
            <p><strong>Title:</strong> ${track.name}</p>
            <p><strong>Artist:</strong> ${track.artist}</p>
            <p><strong>Album:</strong> ${track.album}</p>
        `;
        
        selectedSongInfo.style.display = 'block';
        
        // Focus back on search input
        spotifySearch.focus();
    }

    function processSpotifySong(track) {
        const week = document.getElementById('autoWeek').value;
        const startTime = parseFloat(document.getElementById('startTime').value) || 0;
        const endTime = parseFloat(document.getElementById('endTime').value) || 10;
        
        // Validate time range
        if (startTime < 0) {
            alert('Start time cannot be negative');
            return;
        }
        
        if (endTime <= startTime) {
            alert('End time must be greater than start time');
            return;
        }
        
        if (endTime - startTime < 1) {
            alert('Time range must be at least 1 second');
            return;
        }
        
        // Show progress section
        const progressSection = document.getElementById('progressSection');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const progressDetails = document.getElementById('progressDetails');
        
        progressSection.style.display = 'block';
        progressBar.style.width = '0%';
        progressText.textContent = 'Starting download...';
        progressDetails.textContent = `Downloading "${track.name}" by ${track.artist} from YouTube...`;
        
        // Disable the process button
        const processBtn = document.querySelector(`button[onclick*="${track.id}"]`);
        if (processBtn) {
            processBtn.disabled = true;
            processBtn.textContent = 'Processing...';
        }
        
        // Simulate progress updates
        let progress = 0;
        const frequencies = [100, 500, 1000, 2000, 3500, 5000, 7500];
        let currentFreqIndex = 0;
        
        const progressInterval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress > 90) progress = 90; // Cap at 90% until completion
            progressBar.style.width = progress + '%';
            
            if (progress < 20) {
                progressText.textContent = 'Downloading audio...';
                progressDetails.textContent = 'Fetching audio from YouTube...';
            } else if (progress < 40) {
                progressText.textContent = 'Extracting segment...';
                progressDetails.textContent = `Extracting ${startTime}s - ${endTime}s segment...`;
            } else if (progress < 90) {
                // Show which frequency is being generated
                if (currentFreqIndex < frequencies.length) {
                    const currentFreq = frequencies[currentFreqIndex];
                    progressText.textContent = `Generating ${currentFreq} frequencies...`;
                    progressDetails.textContent = `Processing frequency reconstruction (${currentFreqIndex + 1}/${frequencies.length})`;
                    
                    // Move to next frequency every few seconds
                    if (progress > 40 + (currentFreqIndex * 7)) {
                        currentFreqIndex++;
                    }
                } else {
                    progressText.textContent = 'Finalizing...';
                    progressDetails.textContent = 'Completing frequency reconstructions...';
                }
            }
        }, 1000);
        
        fetch('/admin/process_spotify_song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                spotify_id: track.id,
                title: track.name,
                artist: track.artist,
                album: track.album,
                week: parseInt(week),
                start_time: startTime,
                end_time: endTime
            })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            
            if (data.success) {
                progressBar.style.width = '100%';
                progressText.textContent = 'Complete!';
                progressDetails.textContent = data.message;
                
                // Hide progress after 3 seconds
                setTimeout(() => {
                    progressSection.style.display = 'none';
                }, 3000);
                
                // Refresh the page to show the new song
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                progressText.textContent = 'Error!';
                progressDetails.textContent = data.error || 'Processing failed';
                progressBar.style.background = '#dc3545';
            }
            
            // Re-enable the process button
            if (processBtn) {
                processBtn.disabled = false;
                processBtn.textContent = 'Process';
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            progressText.textContent = 'Error!';
            progressDetails.textContent = 'Network error occurred';
            progressBar.style.background = '#dc3545';
            
            // Re-enable the process button
            if (processBtn) {
                processBtn.disabled = false;
                processBtn.textContent = 'Process';
            }
            
            console.error('Error:', error);
        });
    }
});

function playSong(filename) {
    // Play audio file
    const audio = new Audio('/play/' + filename);
    audio.play();
}

function viewFrequencies(songName) {
    // Get available frequencies from the song data
    const songElement = document.querySelector(`[onclick*="${songName}"]`).closest('.song-item');
    const songInfo = songElement.querySelector('.song-info small');
    let frequencies = [];
    
    if (songInfo && songInfo.textContent.includes('Frequencies:')) {
        const freqText = songInfo.textContent.replace('Frequencies: ', '');
        frequencies = freqText.split(', ');
    } else {
        // Fallback to checking what files exist
        frequencies = ['100', '500', '1000', '2000', '3500', '5000', '7500'];
    }
    
    let frequencyHtml = '<html><head><title>Frequency Versions</title><style>';
    frequencyHtml += 'body{font-family:Arial,sans-serif;padding:20px;background:#f4f4f4;}';
    frequencyHtml += '.audio-player{margin:20px 0;padding:15px;background:white;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.1);}';
    frequencyHtml += 'h3{color:#333;margin-bottom:10px;}';
    frequencyHtml += 'audio{width:100%;}';
    frequencyHtml += '</style></head><body>';
    frequencyHtml += '<h2>Frequency Versions for ' + songName + '</h2>';
    
    frequencies.forEach(freq => {
        frequencyHtml += '<div class="audio-player">';
        frequencyHtml += '<h3>' + freq + ' Frequencies</h3>';
        frequencyHtml += '<audio controls>';
        frequencyHtml += '<source src="/play_frequency/' + songName + '/' + freq + '" type="audio/wav">';
        frequencyHtml += 'Your browser does not support the audio element.';
        frequencyHtml += '</audio>';
        frequencyHtml += '</div>';
    });
    
    frequencyHtml += '</body></html>';
    
    const newWindow = window.open('', '_blank');
    newWindow.document.write(frequencyHtml);
    newWindow.document.close();
}

function deleteSong(songId) {
    if (confirm('Are you sure you want to delete this song?')) {
        fetch('/admin/delete/' + songId, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting song');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting song');
        });
    }
} 