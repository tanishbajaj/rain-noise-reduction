from flask import Flask, request, send_file, send_from_directory
import numpy as np
import soundfile as sf
import io
from flask_cors import CORS
import os

# Serve static files (index.html, script.js, style.css) from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
app = Flask(__name__, static_folder=PROJECT_ROOT, static_url_path="/")
CORS(app)  # Allow frontend JS access

def spectral_subtraction(noisy_signal, noise_reference, alpha=1.8, beta=0.02, frame_size=2048, hop_size=512, sample_rate=44100):
    """
    Spectral Subtraction for noise reduction with voice preservation.
    More effective than LMS for stationary noise like rain.
    
    Parameters:
    - alpha: Over-subtraction factor (reduced to preserve voice)
    - beta: Spectral floor factor (increased to preserve voice)
    - frame_size: FFT window size
    - hop_size: Frame overlap
    - sample_rate: Audio sample rate for frequency calculations
    """
    # Ensure signals are same length
    min_len = min(len(noisy_signal), len(noise_reference))
    noisy_signal = noisy_signal[:min_len]
    noise_reference = noise_reference[:min_len]
    
    # Estimate noise power spectrum from reference
    noise_psd = estimate_noise_psd(noise_reference, frame_size, hop_size)
    
    # Create voice frequency mask (85 Hz to 4000 Hz - human speech range)
    freqs = np.fft.rfftfreq(frame_size, 1.0/sample_rate)
    voice_mask = np.ones(len(freqs))
    # Boost voice frequencies (85-4000 Hz)
    voice_freq_range = (freqs >= 85) & (freqs <= 4000)
    voice_mask[voice_freq_range] = 1.3  # 30% boost for voice frequencies
    
    # Process noisy signal in frames
    output = np.zeros_like(noisy_signal)
    num_frames = (len(noisy_signal) - frame_size) // hop_size + 1
    
    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        
        if end > len(noisy_signal):
            # Pad last frame
            frame = np.pad(noisy_signal[start:], (0, end - len(noisy_signal)), mode='constant')
        else:
            frame = noisy_signal[start:end]
        
        # Apply window (Hann window)
        window = np.hanning(frame_size)
        windowed_frame = frame * window
        
        # FFT
        noisy_fft = np.fft.rfft(windowed_frame)
        noisy_magnitude = np.abs(noisy_fft)
        noisy_phase = np.angle(noisy_fft)
        
        # Spectral subtraction with adaptive alpha based on SNR
        noise_magnitude = np.sqrt(noise_psd[:len(noisy_magnitude)])
        
        # Calculate SNR per frequency bin
        snr = (noisy_magnitude + 1e-10) / (noise_magnitude + 1e-10)
        
        # Adaptive alpha: less aggressive where SNR is high (likely speech)
        adaptive_alpha = alpha * (1.0 - 0.3 * np.minimum(snr / 3.0, 1.0))
        
        # Subtract noise with adaptive over-subtraction
        clean_magnitude = noisy_magnitude - adaptive_alpha * noise_magnitude
        
        # Apply spectral floor (higher for voice frequencies)
        spectral_floor = beta * noisy_magnitude * voice_mask[:len(noisy_magnitude)]
        clean_magnitude = np.maximum(clean_magnitude, spectral_floor)
        
        # Apply voice frequency boost
        clean_magnitude = clean_magnitude * voice_mask[:len(clean_magnitude)]
        
        # Reconstruct signal
        clean_fft = clean_magnitude * np.exp(1j * noisy_phase)
        clean_frame = np.fft.irfft(clean_fft, n=frame_size)
        
        # Apply window again and overlap-add
        clean_frame_windowed = clean_frame * window
        if end <= len(output):
            output[start:end] += clean_frame_windowed
        else:
            output[start:] += clean_frame_windowed[:len(output)-start]
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val * 0.95
    
    return output

def estimate_noise_psd(noise_signal, frame_size=2048, hop_size=512):
    """
    Estimate noise power spectral density (PSD) from reference noise.
    Uses multiple frames and averages for robust estimation.
    """
    num_frames = min(50, (len(noise_signal) - frame_size) // hop_size + 1)
    noise_psd = np.zeros(frame_size // 2 + 1)
    
    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        
        if end > len(noise_signal):
            frame = np.pad(noise_signal[start:], (0, end - len(noise_signal)), mode='constant')
        else:
            frame = noise_signal[start:end]
        
        window = np.hanning(frame_size)
        windowed_frame = frame * window
        noise_fft = np.fft.rfft(windowed_frame)
        noise_psd += np.abs(noise_fft) ** 2
    
    # Average and return
    noise_psd = noise_psd / num_frames
    return noise_psd

def wiener_filter_enhancement(clean_signal, noise_reference, frame_size=2048, hop_size=512, sample_rate=44100):
    """
    Apply Wiener filter as post-processing with voice preservation.
    """
    min_len = min(len(clean_signal), len(noise_reference))
    clean_signal = clean_signal[:min_len]
    noise_reference = noise_reference[:min_len]
    
    # Estimate noise PSD
    noise_psd = estimate_noise_psd(noise_reference, frame_size, hop_size)
    
    # Create voice frequency mask
    freqs = np.fft.rfftfreq(frame_size, 1.0/sample_rate)
    voice_mask = np.ones(len(freqs))
    voice_freq_range = (freqs >= 85) & (freqs <= 4000)
    voice_mask[voice_freq_range] = 1.2  # 20% boost for voice frequencies
    
    output = np.zeros_like(clean_signal)
    num_frames = (len(clean_signal) - frame_size) // hop_size + 1
    
    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        
        if end > len(clean_signal):
            frame = np.pad(clean_signal[start:], (0, end - len(clean_signal)), mode='constant')
        else:
            frame = clean_signal[start:end]
        
        window = np.hanning(frame_size)
        windowed_frame = frame * window
        signal_fft = np.fft.rfft(windowed_frame)
        signal_magnitude = np.abs(signal_fft)
        signal_phase = np.angle(signal_fft)
        
        # Wiener filter: H(f) = S_signal(f) / (S_signal(f) + S_noise(f))
        signal_psd = signal_magnitude ** 2
        noise_psd_frame = noise_psd[:len(signal_psd)]
        
        # Avoid division by zero
        total_psd = signal_psd + noise_psd_frame + 1e-10
        wiener_gain = signal_psd / total_psd
        
        # Boost voice frequencies in Wiener gain
        wiener_gain = wiener_gain * voice_mask[:len(wiener_gain)]
        wiener_gain = np.minimum(wiener_gain, 1.5)  # Cap gain to prevent distortion
        
        # Apply gain
        enhanced_magnitude = signal_magnitude * wiener_gain
        enhanced_fft = enhanced_magnitude * np.exp(1j * signal_phase)
        enhanced_frame = np.fft.irfft(enhanced_fft, n=frame_size)
        
        enhanced_frame_windowed = enhanced_frame * window
        if end <= len(output):
            output[start:end] += enhanced_frame_windowed
        else:
            output[start:] += enhanced_frame_windowed[:len(output)-start]
    
    # Normalize
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val * 0.95
    
    return output

def enhance_voice_frequencies(signal, sample_rate=44100, boost_db=3.0):
    """
    Apply additional voice frequency enhancement using EQ-like filtering.
    Boosts frequencies in the human speech range (85-4000 Hz).
    """
    # Simple frequency-domain boost for voice range
    frame_size = 2048
    hop_size = 512
    
    output = np.zeros_like(signal)
    num_frames = (len(signal) - frame_size) // hop_size + 1
    
    # Create frequency mask for voice enhancement
    freqs = np.fft.rfftfreq(frame_size, 1.0/sample_rate)
    voice_boost = np.ones(len(freqs))
    
    # Boost voice frequencies (85-4000 Hz) with smooth rolloff
    voice_low = 85
    voice_high = 4000
    
    for i, freq in enumerate(freqs):
        if voice_low <= freq <= voice_high:
            # Maximum boost in the middle of voice range
            if 300 <= freq <= 3000:
                voice_boost[i] = 10.0 ** (boost_db / 20.0)  # Convert dB to linear gain
            else:
                # Gradual rolloff at edges
                if freq < 300:
                    factor = (freq - voice_low) / (300 - voice_low)
                else:
                    factor = (voice_high - freq) / (voice_high - 3000)
                voice_boost[i] = 1.0 + (10.0 ** (boost_db / 20.0) - 1.0) * factor
    
    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        
        if end > len(signal):
            frame = np.pad(signal[start:], (0, end - len(signal)), mode='constant')
        else:
            frame = signal[start:end]
        
        window = np.hanning(frame_size)
        windowed_frame = frame * window
        signal_fft = np.fft.rfft(windowed_frame)
        signal_magnitude = np.abs(signal_fft)
        signal_phase = np.angle(signal_fft)
        
        # Apply voice boost
        enhanced_magnitude = signal_magnitude * voice_boost[:len(signal_magnitude)]
        enhanced_fft = enhanced_magnitude * np.exp(1j * signal_phase)
        enhanced_frame = np.fft.irfft(enhanced_fft, n=frame_size)
        
        enhanced_frame_windowed = enhanced_frame * window
        if end <= len(output):
            output[start:end] += enhanced_frame_windowed
        else:
            output[start:] += enhanced_frame_windowed[:len(output)-start]
    
    # Normalize
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val * 0.95
    
    return output

@app.route("/", methods=["GET"])
def serve_index():
    # Serve index.html from project root
    return send_from_directory(PROJECT_ROOT, "index.html")

@app.route('/process', methods=['POST'])
def process_audio():
    try:
        # Get uploaded files
        if 'speech' not in request.files or 'noise' not in request.files:
            return ("Missing 'speech' or 'noise' file field", 400)
        speech_file = request.files['speech']
        noise_file = request.files['noise']

        # Read audio data
        noisy_input, fs = sf.read(speech_file, always_2d=False)
        noise_ref, fs2 = sf.read(noise_file, always_2d=False)

        # Ensure mono (convert stereo -> mono)
        def to_mono(arr: np.ndarray) -> np.ndarray:
            if arr.ndim == 1:
                return arr.astype(np.float64)
            # shape (N, C) -> average channels
            return np.mean(arr, axis=1).astype(np.float64)

        noisy_input = to_mono(noisy_input)
        noise_ref = to_mono(noise_ref)

        # Ensure minimum length
        min_len = min(len(noisy_input), len(noise_ref))
        if min_len < 1024:  # Need at least some samples
            return ("Audio files too short (minimum 1024 samples required)", 400)
        
        noisy_input = noisy_input[:min_len]
        noise_ref = noise_ref[:min_len]
        
        # Normalize input levels
        noisy_input = noisy_input / (np.max(np.abs(noisy_input)) + 1e-10)
        noise_ref = noise_ref / (np.max(np.abs(noise_ref)) + 1e-10)

        # Step 1: Apply Spectral Subtraction (primary method) with voice preservation
        filtered = spectral_subtraction(
            noisy_input, 
            noise_ref, 
            alpha=1.8,  # Reduced over-subtraction to preserve voice
            beta=0.02,  # Increased spectral floor to preserve voice
            frame_size=2048,
            hop_size=512,
            sample_rate=fs
        )
        
        # Step 2: Apply Wiener filter enhancement with voice boost
        filtered = wiener_filter_enhancement(
            filtered,
            noise_ref,
            frame_size=2048,
            hop_size=512,
            sample_rate=fs
        )
        
        # Step 3: Apply additional voice frequency enhancement
        filtered = enhance_voice_frequencies(
            filtered,
            sample_rate=fs,
            boost_db=3.0  # 3dB boost for voice frequencies
        )
        
        # Ensure output is in valid range
        filtered = np.clip(filtered, -1.0, 1.0)
        
        # Preserve original amplitude scale (don't reduce as much)
        original_max = np.max(np.abs(noisy_input))
        if original_max > 0:
            # Scale to match original level better
            filtered_max = np.max(np.abs(filtered))
            if filtered_max > 0:
                filtered = filtered * (original_max / filtered_max) * 0.95

        # Save to buffer
        buf = io.BytesIO()
        sf.write(buf, filtered, fs, format='WAV')
        buf.seek(0)

        return send_file(buf, mimetype='audio/wav', as_attachment=True, download_name='output_cleaned.wav')
    except Exception as exc:
        import traceback
        return (f"Processing error: {str(exc)}\n{traceback.format_exc()}", 500)

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
