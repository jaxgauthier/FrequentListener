"""
Audio processing service for DFT operations
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import soundfile as sf
import tempfile
from pydub import AudioSegment
import yt_dlp
import glob
from flask import current_app

class AudioService:
    """Service for audio processing and management"""
    
    @staticmethod
    def get_available_frequencies(song_name):
        """Get available frequency levels for a song"""
        song_folder = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], song_name)
        
        if not os.path.exists(song_folder):
            # Fallback to old mapping system
            song_folders = {
                'MrBrightside': 'MrBrighstide',
                'GhostTown': 'GhostTown',
                'Milan': 'Milan',
                'TeenageDirtbag': 'TeenageDirtbag'
            }
            
            folder_name = song_folders.get(song_name)
            if not folder_name:
                return []
            song_folder = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], folder_name)
        
        available_frequencies = []
        if os.path.exists(song_folder):
            for file in os.listdir(song_folder):
                if file.startswith('reconstructed_audio_') and file.endswith('.wav'):
                    freq = file.replace('reconstructed_audio_', '').replace('.wav', '')
                    available_frequencies.append(freq)
        
        # Sort frequencies numerically
        return sorted(available_frequencies, key=int)
    
    @staticmethod
    def download_from_youtube(song_title, artist, output_path, start_time=0, end_time=None):
        """Download audio from YouTube"""
        try:
            search_query = f"{song_title} {artist} audio"
            
            # Create temp file template
            with tempfile.NamedTemporaryFile(suffix='', delete=False) as temp_audio_file:
                temp_audio_path_base = temp_audio_file.name
            temp_audio_tmpl = temp_audio_path_base + ".%(ext)s"
            
            # yt-dlp options
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
                'outtmpl': temp_audio_tmpl,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'postprocessors': [],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                if not search_results or 'entries' not in search_results or not search_results['entries']:
                    raise Exception(f"No YouTube videos found for: {search_query}")
                
                video_info = search_results['entries'][0]
                video_url = video_info['url']
                ydl.download([video_url])
            
            # Find downloaded file
            downloaded_files = glob.glob(temp_audio_path_base + ".*")
            if not downloaded_files:
                raise Exception("Download completed but file not found")
            
            temp_audio_path = downloaded_files[0]
            
            # Extract segment
            audio = AudioSegment.from_file(temp_audio_path)
            if end_time is not None:
                segment = audio[start_time*1000:end_time*1000]
            else:
                segment = audio[start_time*1000:]
            
            # Export as WAV
            segment.export(output_path, format="wav")
            
            # Clean up temp files
            for f in downloaded_files:
                os.remove(f)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error downloading from YouTube: {e}")
            return False
    
    @staticmethod
    def process_through_dft(input_file, output_folder, base_filename):
        """Process audio through DFT pipeline"""
        try:
            # Import using absolute paths for reliability
            import sys
            import os
            
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Add project root to path if not already there
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Import the required functions
            from audio.layersFFT import read_audio_file
            from audio.manim_to_audio import save_audio
            
            # Read audio file
            data, sample_rate, num_channels = read_audio_file(input_file)
            
            # Compute FFT
            fft_result = np.fft.fft(data)
            freq = np.fft.fftfreq(len(data), 1/sample_rate)
            magnitude = np.abs(fft_result)
            
            # Filter noise
            min_magnitude_threshold = np.max(magnitude) * 0.01
            significant_indices = magnitude > min_magnitude_threshold
            
            # Get frequency levels from config
            frequency_counts = current_app.config['FREQUENCY_LEVELS']
            available_indices = np.where(significant_indices)[0]
            
            # Create output folder
            song_output_folder = os.path.join(current_app.config['AUDIO_OUTPUT_FOLDER'], output_folder)
            os.makedirs(song_output_folder, exist_ok=True)
            
            for freq_count in frequency_counts:
                # Get top frequencies
                top_indices = available_indices[np.argsort(magnitude[available_indices])[-freq_count:][::-1]]
                top_freqs = freq[top_indices]
                top_magnitudes = magnitude[top_indices]
                
                # Create filtered FFT result
                filtered_fft = np.zeros_like(fft_result)
                
                # Copy significant frequency components
                for freq_val, mag_val in zip(top_freqs, top_magnitudes):
                    freq_index = np.argmin(np.abs(freq - freq_val))
                    filtered_fft[freq_index] = fft_result[freq_index]
                    if freq_index > 0:
                        filtered_fft[len(fft_result) - freq_index] = np.conj(fft_result[freq_index])
                
                # Reconstruct audio
                reconstructed_audio = np.real(np.fft.ifft(filtered_fft))
                reconstructed_audio = reconstructed_audio / np.max(np.abs(reconstructed_audio))
                
                # Save reconstructed audio
                output_file = os.path.join(song_output_folder, f'reconstructed_audio_{freq_count}.wav')
                save_audio(reconstructed_audio, sample_rate, output_file)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error processing song through DFT: {e}")
            return False 