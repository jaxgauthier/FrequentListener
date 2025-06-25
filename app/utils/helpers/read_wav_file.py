import wave
import numpy as np

def read_wav_file(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        sample_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        frames = wav_file.readframes(params.nframes)

        data = np.frombuffer(frames, dtype=np.int16)
        if num_channels == 2:
            data = data.reshape(-1, 2)
            # Use only left channel instead of averaging to avoid phase cancellation
            data = data[:, 0]
        
        # Normalize the data
        data = data.astype(np.float32) / 32768.0
        return data, sample_rate, num_channels

    
    