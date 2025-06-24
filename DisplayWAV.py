import wave
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.widgets import Button
from helpers.read_wav_file import read_wav_file
from helpers.audio_player import AudioPlayer


def plot_voltage_samples(data, sample_rate, num_channels, file_path):
    """
    Plot voltage samples over time for the entire file with playback button
    """
    fig = plt.figure(figsize=(15, 7))
    ax = fig.add_axes([0.1, 0.2, 0.8, 0.7])  # [left, bottom, width, height]
    
    # Calculate total duration and create time axis
    total_duration = len(data) / sample_rate
    time = np.linspace(0, total_duration, len(data))
    
    # Plot the voltage data
    ax.plot(time, data, 'b-', linewidth=0.5, alpha=.7)
    
    # Add grid and labels
    ax.grid(True, alpha=0.3)
    ax.set_ylabel('Voltage (normalized)')
    ax.set_xlabel('Time (seconds)')
    ax.set_title(f'Audio Waveform: {os.path.basename(file_path)}')
    
    # Set y-axis limits to show full voltage range
    ax.set_ylim(-1.1, 1.1)
    
    # Add text box with file information
    info_text = (f'Sample Rate: {sample_rate} Hz\nDuration: {total_duration:.2f}s\n'
                f'Samples: {len(data)}\n'
                f'Press spacebar or click button to play')
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Create button axes and button
    button_ax = fig.add_axes([0.4, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
    player = AudioPlayer(file_path, fig)
    
    # Create button with custom style
    button = Button(button_ax, 'Play Audio (Spacebar)', 
                   color='lightblue', hovercolor='skyblue')
    button.on_clicked(player.play)
    
    # Add keyboard event handler
    fig.canvas.mpl_connect('key_press_event', player.on_key)
    
    # Keep a reference to prevent garbage collection
    fig.player = player # type: ignore

    plt.show()
    

def main(input_file=None):
    try:
        if input_file is None:
            input_file = os.path.join('InputWAVS', 'Input2.wav') #default file incase no file is provided
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Could not find the input file at: {input_file}") #error if not found 
            
        data, sample_rate, num_channels = read_wav_file(input_file) #read the audio file using the wave library and numpy
        
        print(f"File loaded successfully: {input_file}")
        print(f"Data shape: {data.shape}")
        print(f"Sample rate: {sample_rate}")
        
        plot_voltage_samples(data, sample_rate, num_channels, input_file) #plot the audio file 
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

