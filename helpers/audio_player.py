import sounddevice as sd
import soundfile as sf
import numpy as np

class AudioPlayer:
    def __init__(self, file_path, fig):
        self.file_path = file_path
        self.fig = fig
        self.is_playing = False
        # Load the audio file
        self.data, self.sample_rate = sf.read(file_path)
        # Convert stereo to mono if necessary
        if len(self.data.shape) > 1:
            self.data = np.mean(self.data, axis=1)
        
    def play(self, event=None):
        """Play or stop the audio"""
        if not self.is_playing:
            # Start playing
            sd.play(self.data, self.sample_rate)
            self.is_playing = True
        else:
            # Stop playing
            sd.stop()
            self.is_playing = False
            
    def on_key(self, event):
        """Handle keyboard events"""
        if event.key == ' ':  # spacebar
            self.play()
