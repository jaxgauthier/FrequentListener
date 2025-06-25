#!/usr/bin/env python3
"""
Test script to compare audio quality from different sources
"""

import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment

def test_audio_quality():
    """Test audio quality from different sources"""
    print("Testing audio quality...")
    
    # Test 1: Original placeholder file (known good)
    print("\n1. Testing original placeholder file...")
    placeholder_path = "InputWAVS/Mr_Brightside.wav"
    if os.path.exists(placeholder_path):
        audio = AudioSegment.from_wav(placeholder_path)
        print(f"   Duration: {len(audio)/1000:.2f}s")
        print(f"   Sample rate: {audio.frame_rate}Hz")
        print(f"   Channels: {audio.channels}")
        print(f"   Max volume: {audio.max_possible_amplitude}")
        
        # Extract 10 seconds
        segment = audio[0:10000]  # 0-10 seconds
        segment.export("test_placeholder_10s.wav", format="wav")
        print("   ✅ Exported placeholder 10s segment")
    else:
        print("   ❌ Placeholder file not found")
    
    # Test 2: YouTube downloaded file (if exists)
    print("\n2. Testing YouTube downloaded file...")
    youtube_path = "uploads/temp_downloads/Queen_BohemianRhapsody.wav"
    if os.path.exists(youtube_path):
        audio = AudioSegment.from_wav(youtube_path)
        print(f"   Duration: {len(audio)/1000:.2f}s")
        print(f"   Sample rate: {audio.frame_rate}Hz")
        print(f"   Channels: {audio.channels}")
        print(f"   Max volume: {audio.max_possible_amplitude}")
        
        # Check for potential issues
        if audio.frame_rate < 22050:
            print("   ⚠️  Low sample rate detected")
        if audio.channels > 2:
            print("   ⚠️  Unusual channel count")
        
        print("   ✅ YouTube file analyzed")
    else:
        print("   ❌ YouTube file not found")
    
    # Test 3: DFT processed file (if exists)
    print("\n3. Testing DFT processed file...")
    dft_path = "OutputWAVS/Queen_BohemianRhapsody/reconstructed_audio_10.wav"
    if os.path.exists(dft_path):
        audio = AudioSegment.from_wav(dft_path)
        print(f"   Duration: {len(audio)/1000:.2f}s")
        print(f"   Sample rate: {audio.frame_rate}Hz")
        print(f"   Channels: {audio.channels}")
        print(f"   Max volume: {audio.max_possible_amplitude}")
        print("   ✅ DFT file analyzed")
    else:
        print("   ❌ DFT file not found")
    
    print("\nAudio quality test complete!")

if __name__ == "__main__":
    test_audio_quality() 