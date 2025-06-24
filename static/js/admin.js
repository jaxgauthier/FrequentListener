// Basic Admin JavaScript
function playSong(filename) {
    // Play audio file
    const audio = new Audio('/play/' + filename);
    audio.play();
}

function viewFrequencies(songName) {
    // Open a new window/tab to view frequency versions
    const frequencies = ['10', '100', '500', '1000', '5000'];
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