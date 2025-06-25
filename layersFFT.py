from manim_to_audio import generate_audio_from_frequencies, save_audio, plot_and_play_audio
import numpy as np
import soundfile as sf
import os
import DisplayWAV
from helpers.read_wav_file import read_wav_file
import matplotlib.pyplot as plt
from manim import *
from pydub import AudioSegment
import tempfile

def convert_audio_to_wav(input_file):
    """
    Convert MP3 or other audio formats to WAV format
    Returns the path to the converted WAV file
    """
    file_extension = os.path.splitext(input_file)[1].lower()
    
    if file_extension == '.wav':
        return input_file  # Already WAV format
    
    elif file_extension == '.mp3':
        print(f"Converting MP3 file: {input_file}")
        # Load MP3 file
        audio = AudioSegment.from_mp3(input_file)
        
        # Create temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav_path = temp_wav.name
        temp_wav.close()
        
        # Export as WAV
        audio.export(temp_wav_path, format='wav')
        print(f"Converted to temporary WAV: {temp_wav_path}")
        
        return temp_wav_path
    
    else:
        # Try to load with pydub (supports many formats)
        try:
            print(f"Converting audio file: {input_file}")
            audio = AudioSegment.from_file(input_file)
            
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            # Export as WAV
            audio.export(temp_wav_path, format='wav')
            print(f"Converted to temporary WAV: {temp_wav_path}")
            
            return temp_wav_path
        except Exception as e:
            raise ValueError(f"Unsupported audio format: {file_extension}. Error: {e}")

def read_audio_file(input_file):
    """
    Read audio file (MP3, WAV, etc.) and return data, sample_rate, num_channels
    """
    # Convert to WAV if needed
    wav_file = convert_audio_to_wav(input_file)
    
    try:
        # Read the WAV file
        data, sample_rate, num_channels = read_wav_file(wav_file)
        
        # Clean up temporary file if it was created
        if wav_file != input_file:
            os.unlink(wav_file)
            print("Cleaned up temporary WAV file")
        
        return data, sample_rate, num_channels
    
    except Exception as e:
        # Clean up temporary file if it was created
        if wav_file != input_file:
            try:
                os.unlink(wav_file)
            except:
                pass
        raise e

def main(input_file=None, start_time=0, end_time=None):
    if input_file is None:
        input_file = os.path.join('InputWAVS', 'milan.mp3')
        # You can also use MP3 files like this:
        # input_file = os.path.join('InputWAVS', 'your_song.mp3')
    
    print(f"Input file: {input_file}")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Could not find the input file at: {input_file}")

    data, sample_rate, num_channels = read_audio_file(input_file)
    print(f"Original data shape: {data.shape}")
    
    # Calculate total duration
    total_duration = len(data) / sample_rate
    print(f"Total audio duration: {total_duration:.2f} seconds")
    
    # Extract specific time range
    start_sample = int(start_time * sample_rate)
    if end_time is None:
        end_sample = len(data)
    else:
        end_sample = int(end_time * sample_rate)
    
    # Check if time range is valid
    if start_time >= total_duration:
        raise ValueError(f"Start time ({start_time}s) is beyond audio duration ({total_duration:.2f}s)")
    
    if end_time is not None and end_time > total_duration:
        print(f"Warning: End time ({end_time}s) is beyond audio duration ({total_duration:.2f}s). Using end of audio.")
        end_time = total_duration
        end_sample = len(data)
    
    # Ensure we don't go beyond the data length
    end_sample = min(end_sample, len(data))
    start_sample = min(start_sample, len(data))
    
    # Check if we have any data to process
    if start_sample >= end_sample:
        raise ValueError(f"No data in time range {start_time}s to {end_time if end_time else 'end'}s")
    
    # Extract the time range
    data = data[start_sample:end_sample]
    print(f"Extracted {start_time}s to {end_time if end_time else 'end'}s. New data shape: {data.shape}")
    print(f"Duration: {len(data) / sample_rate:.2f} seconds")
    
    # Compute FFT
    fft_result = np.fft.fft(data)

    # Get frequency array
    freq = np.fft.fftfreq(len(data), 1/sample_rate)
    
    # Calculate magnitude (absolute value of complex numbers)
    magnitude = np.abs(fft_result)
    
    # Filter out very small magnitudes (noise)
    min_magnitude_threshold = np.max(magnitude) * 0.01  # 1% of max magnitude
    significant_indices = magnitude > min_magnitude_threshold
    
    # Find top frequencies by magnitude (limit to reasonable number)
    top_n = [100, 500, 1000, 2000, 3500, 5000, 7500]
    available_indices = np.where(significant_indices)[0]

    for i in range(len(top_n)):
        top_indices = available_indices[np.argsort(magnitude[available_indices])[-top_n[i]:][::-1]]
        top_freqs = freq[top_indices]
        top_magnitudes = magnitude[top_indices]

        print(f"\nMagnitude thres jhold: {min_magnitude_threshold:.2f}")
        print(f"Significant frequencies found: {len(available_indices)}")
        print(f"Using top {len(top_freqs)} frequencies")

        print(f"\nTop {len(top_freqs)} frequencies by magnitude:")
        print("Frequency (Hz) | Magnitude")
        print("-" * 30)
        for j, (freq_val, mag_val) in enumerate(zip(top_freqs, top_magnitudes)):
            print(f"{freq_val:12.2f} | {mag_val:10.2f}")

        # Create a filtered FFT result for better reconstruction
        filtered_fft = np.zeros_like(fft_result)

        # Copy the significant frequency components back to their original positions
        for k, (freq_val, mag_val) in enumerate(zip(top_freqs, top_magnitudes)):
            # Find the original index for this frequency
            freq_index = np.argmin(np.abs(freq - freq_val))
            # Copy the original complex value (preserving phase)
            filtered_fft[freq_index] = fft_result[freq_index]
            # Also copy the negative frequency component (for real signal)
            if freq_index > 0:
                filtered_fft[len(fft_result) - freq_index] = np.conj(fft_result[freq_index])

        # Reconstruct audio using inverse FFT
        reconstructed_audio = np.real(np.fft.ifft(filtered_fft))

        # Normalize the reconstructed audio
        reconstructed_audio = reconstructed_audio / np.max(np.abs(reconstructed_audio))

        print(f"\nReconstructed audio shape: {reconstructed_audio.shape}")
        print(f"Audio duration: {len(reconstructed_audio) / sample_rate:.2f} seconds")

        print(f"Saving audio to OutputWAVS/reconstructed_audio_{top_n[i]}.wav")
        save_audio(reconstructed_audio, sample_rate, f"OutputWAVS/reconstructed_audio_{top_n[i]}.wav")
   

if __name__ == "__main__":
    # Example: Extract 1-3 seconds from the audio
    main(start_time=15, end_time=25)
