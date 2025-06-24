// Progressive Difficulty Audio Game JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const guessForm = document.getElementById('guessForm');
    const resultsSection = document.getElementById('resultsSection');
    const resultMessage = document.getElementById('resultMessage');
    const correctAnswer = document.getElementById('correctAnswer');
    
    console.log('DOM loaded, form found:', guessForm);
    
    // Track current difficulty level (0 = 10 frequencies, 1 = 100, etc.)
    let currentDifficulty = 0;
    const frequencies = ['10', '100', '500', '1000', '5000'];
    
    // Initialize: only show the hardest frequency
    showCurrentDifficulty();

    function showCurrentDifficulty() {
        // Hide all audio players
        frequencies.forEach(freq => {
            const audioPlayer = document.getElementById(`audio-${freq}`);
            if (audioPlayer) {
                audioPlayer.style.display = 'none';
            }
        });
        
        // Show only the current difficulty level
        if (currentDifficulty < frequencies.length) {
            const currentAudioPlayer = document.getElementById(`audio-${frequencies[currentDifficulty]}`);
            if (currentAudioPlayer) {
                currentAudioPlayer.style.display = 'block';
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