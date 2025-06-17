import numpy as np
import librosa
import soundfile as sf
import os
import DisplayWAV

# Create input directory if it doesn't exist
os.makedirs('InputWAVS', exist_ok=True)

# Define input file
input_file = os.path.join('InputWAVS', 'Input2.wav')
print(f"\nProcessing input file: {input_file}")

try:
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print("Loading audio file...")
    # Load the audio file
    y, sr = librosa.load(input_file)
    print(f"Audio loaded successfully! Sample rate: {sr}Hz, Duration: {len(y)/sr:.2f} seconds")

    # Process one octave up (+12 semitones)
    print("\nProcessing pitch shift up one octave (+12 semitones)...")
    
    # Shift pitch while preserving duration
    y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=12)
    
    # Export pitch changed sound
    output_wav = "InputWAVS/octave_up_1.0.wav"
    print(f"Saving to: {output_wav}")
    sf.write(output_wav, y_shifted, sr)
    
    # Display waveform with playback button
    print("Displaying waveform...")
    DisplayWAV.main(output_wav)
    
    # Display waveform with playback button for original file
    print("\nDisplaying original file waveform...")
    DisplayWAV.main(input_file)

    print("\nProcessing complete!")

except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
    import traceback
    traceback.print_exc() 