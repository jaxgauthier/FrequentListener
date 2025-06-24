import numpy as np
import soundfile as sf
from helpers.audio_player import AudioPlayer
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def generate_audio_from_frequencies(frequencies, amplitudes=None, duration=4.0, sample_rate=44100):
    """
    Generate audio data from a list of frequencies
    
    Args:
        frequencies (list): List of frequencies in Hz
        amplitudes (list): List of amplitudes for each frequency (default: all 1.0)
        duration (float): Duration of the audio in seconds
        sample_rate (int): Number of samples per second
        
    Returns:
        numpy array: The generated audio data
        int: The sample rate
    """
    # Create time array
    num_samples = int(duration * sample_rate)
    time_array = np.arange(num_samples) / sample_rate
    
    # Initialize audio data
    audio_data = np.zeros(num_samples)

    # Add each frequency component
    for i, frequency in enumerate(frequencies):
        amplitude = amplitudes[i] if amplitudes is not None else 1.0
        audio_data += amplitude * np.sin(2 * np.pi * frequency * time_array)

    return audio_data, sample_rate

def save_audio(audio_data, sample_rate, output_file):
    """
    Save audio data to a WAV file
    
    Args:
        audio_data (numpy array): The audio data to save
        sample_rate (int): The sample rate of the audio
        output_file (str): Path to save the WAV file
    """
    sf.write(output_file, audio_data, sample_rate)

def plot_and_play_audio(audio_data, sample_rate, title="Generated Waveform"):
    """
    Plot the audio waveform and provide playback controls
    
    Args:
        audio_data (numpy array): The audio data to plot
        sample_rate (int): The sample rate of the audio
        title (str): Title for the plot    """
    fig = plt.figure(figsize=(15, 7))
    ax = fig.add_axes([0.1, 0.2, 0.8, 0.7])  # [left, bottom, width, height]
    
    # Calculate total duration and create time axis
    total_duration = len(audio_data) / sample_rate
    time = np.linspace(0, total_duration, len(audio_data))
    
    ax.plot(time, audio_data, 'b-', linewidth=0.5, alpha=.7)
    ax.grid(True, alpha=0.3)
    ax.set_ylabel('Voltage (normalized)')
    ax.set_xlabel('Time (seconds)')
    ax.set_title(title)
    


if __name__ == "__main__":
    # Example usage
    frequencies = [440, 880]  # A4 and A5 notes
    amplitudes = [0.7, 0.3]   # 70% and 30% amplitude
    
    # Generate audio
    audio_data, sample_rate = generate_audio_from_frequencies(
        frequencies=frequencies,
        amplitudes=amplitudes,
        duration=2.0  # 2 seconds
    )
    
    # Plot and play
    plot_and_play_audio(audio_data, sample_rate, "Example: A4 + A5 Notes") 