# 🌧️ Rain Noise Reduction Web Application

A web-based application that uses **Spectral Subtraction, Wiener Filtering, and Voice Enhancement** to reduce rain noise from audio recordings while preserving and amplifying human speech. The application provides an intuitive web interface for uploading noisy speech and rain reference files, then processes them using advanced frequency-domain techniques to produce cleaner audio output with enhanced voice clarity.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## ✨ Features

- **Web-based Interface**: Simple, user-friendly web UI for audio processing
- **Spectral Subtraction**: Frequency-domain noise reduction algorithm optimized for stationary noise like rain
- **Wiener Filter Enhancement**: Adaptive filtering for additional noise reduction
- **Voice Preservation & Enhancement**: Advanced voice frequency boosting (85-4000 Hz) to maintain and amplify human speech
- **Three-Stage Processing**: Spectral Subtraction → Wiener Filter → Voice Enhancement for optimal results
- **Adaptive Noise Reduction**: SNR-based adaptation to preserve speech while removing noise
- **Real-time Processing**: Fast audio processing with immediate results
- **Audio Preview**: Listen to both original and filtered audio directly in the browser
- **Automatic Format Handling**: Supports both mono and stereo WAV files
- **Error Handling**: Comprehensive error messages for debugging

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework for API endpoints
- **NumPy**: Numerical computations and FFT operations for signal processing
- **SoundFile**: Audio file I/O operations
- **Flask-CORS**: Cross-origin resource sharing support

### Frontend
- **HTML5**: Structure and audio elements
- **CSS3**: Modern, responsive styling
- **JavaScript (ES6+)**: Client-side logic and API communication

## 📁 Project Structure

```
rain-noise-reduction/
│
├── index.html          # Main HTML page
├── style.css           # Styling for the web interface
├── script.js           # Frontend JavaScript logic
│
├── backend/
│   └── app.py         # Flask backend with Spectral Subtraction + Wiener Filter + Voice Enhancement
│
├── audio/             # Sample audio files (optional)
│   ├── speech_clean.wav
│   ├── rain_noise.wav
│   └── output_cleaned.wav
│
└── README.md          # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd rain-noise-reduction
```

### Step 2: Install Python Dependencies

```bash
pip install flask numpy soundfile flask-cors
```

### Step 3: Verify Installation

Check that all packages are installed:
```bash
python -c "import flask, numpy, soundfile, flask_cors; print('All packages installed successfully!')"
```

## 💻 Usage

### Starting the Server

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

3. The server will start on `http://127.0.0.1:5000`

### Using the Web Interface

1. **Open your browser** and navigate to `http://127.0.0.1:5000`

2. **Upload Files**:
   - **Noisy Speech File**: Upload a WAV file containing speech with rain noise
   - **Rain Noise Reference File**: Upload a WAV file containing only rain noise (no speech)

3. **Process Audio**: Click the "Process Audio" button

4. **Listen to Results**: 
   - The original audio will play in the "Original Speech" section
   - The filtered (cleaned) audio will appear in the "Filtered Output" section

### Important Notes

- **File Format**: Only WAV files are supported (`.wav` extension)
- **Rain Reference Quality**: For best results, the rain reference file should:
  - Contain only rain noise (no speech or other sounds)
  - Match the type/intensity of rain in your noisy speech file
  - Be recorded in similar conditions if possible (not strictly required with spectral methods)
- **File Length**: The filter automatically aligns file lengths to the shorter file
- **Minimum Length**: Files must be at least 1024 samples long for processing

## 🔬 How It Works

### Three-Stage Noise Reduction Architecture with Voice Preservation

The application uses a **hybrid three-stage approach** combining Spectral Subtraction, Wiener Filtering, and Voice Enhancement for effective rain noise reduction while preserving and amplifying human speech:

#### Stage 1: Adaptive Spectral Subtraction with Voice Preservation

Spectral Subtraction works in the **frequency domain** with intelligent voice preservation:

1. **Noise PSD Estimation**: Estimates the noise Power Spectral Density (PSD) from the rain reference file by analyzing multiple frames
2. **Frame-Based Processing**: Processes the noisy signal in overlapping frames using FFT
3. **SNR-Based Adaptation**: Calculates Signal-to-Noise Ratio (SNR) per frequency bin
4. **Adaptive Over-Subtraction**: Uses adaptive over-subtraction factor (α=1.8, reduced from 2.5) that becomes less aggressive in high-SNR regions (likely speech)
5. **Voice Frequency Masking**: Applies 30% boost to voice frequencies (85-4000 Hz) during processing
6. **Enhanced Spectral Flooring**: Uses higher spectral floor (β=0.02) with voice frequency emphasis to preserve speech
7. **Signal Reconstruction**: Reconstructs the time-domain signal using overlap-add method

**Key Voice Preservation Features:**
- Adaptive alpha reduces noise removal aggressiveness where speech is detected
- Voice frequency mask (85-4000 Hz) receives 30% boost
- Higher spectral floor prevents voice from being over-filtered

#### Stage 2: Wiener Filter Enhancement with Voice Boost

The Wiener filter provides additional noise reduction while emphasizing voice:

1. **Adaptive Filtering**: Applies frequency-dependent gain based on estimated Signal-to-Noise Ratio (SNR)
2. **Per-Frequency Processing**: Each frequency bin is filtered independently
3. **Optimal Gain**: Uses Wiener filter gain: `H(f) = S_signal(f) / (S_signal(f) + S_noise(f))`
4. **Voice Frequency Boost**: Applies 20% additional gain to voice frequencies (85-4000 Hz)
5. **Gain Capping**: Limits maximum gain to 1.5x to prevent distortion
6. **Smooth Output**: Produces cleaner output with reduced artifacts

#### Stage 3: Voice Frequency Enhancement

A dedicated voice enhancement stage amplifies human speech:

1. **EQ-like Filtering**: Applies frequency-domain equalization to boost voice range
2. **Core Voice Boost**: 3dB boost for primary voice frequencies (300-3000 Hz)
3. **Smooth Rolloff**: Gradual boost at voice range edges (85-300 Hz and 3000-4000 Hz)
4. **Natural Sound**: Preserves natural voice characteristics while enhancing clarity
5. **Amplitude Preservation**: Maintains original voice levels without distortion

### Algorithm Parameters

- **Frame Size**: 2048 samples - provides good frequency resolution
- **Hop Size**: 512 samples - 75% overlap for smooth reconstruction
- **Over-Subtraction Factor (α)**: 1.8 - reduced from 2.5 to preserve voice (adaptive based on SNR)
- **Spectral Floor (β)**: 0.02 - increased from 0.01 to better preserve voice frequencies
- **Voice Frequency Range**: 85-4000 Hz - human speech frequency range
- **Voice Boost (Stage 1)**: 30% gain for voice frequencies during spectral subtraction
- **Voice Boost (Stage 2)**: 20% additional gain for voice frequencies in Wiener filter
- **Voice Boost (Stage 3)**: 3dB (≈41% linear) boost for core voice frequencies (300-3000 Hz)
- **Window Function**: Hann window - reduces spectral leakage

### Why This Architecture?

**Spectral Subtraction** is superior to time-domain adaptive filters (like LMS) for rain noise because:

- ✅ Works in frequency domain where noise characteristics are clearer
- ✅ Doesn't require perfect correlation between reference and noisy signal
- ✅ More effective for stationary noise (rain is relatively stationary)
- ✅ Can handle different noise intensities and characteristics
- ✅ Better at preserving speech while removing noise

**Adaptive Voice Preservation** provides:
- ✅ SNR-based adaptation reduces aggressiveness where speech is detected
- ✅ Voice frequency masking prevents over-filtering of speech
- ✅ Maintains natural voice characteristics

**Wiener Filter** enhancement provides:
- ✅ Additional noise reduction in frequency bins with low SNR
- ✅ Adaptive gain control per frequency
- ✅ Voice frequency boost for enhanced clarity
- ✅ Smoother output with fewer artifacts

**Voice Enhancement** provides:
- ✅ Dedicated EQ-like filtering for voice frequencies
- ✅ Amplifies speech while maintaining natural sound
- ✅ Compensates for any voice loss during noise reduction
- ✅ Improves overall voice clarity and intelligibility

### Mathematical Overview

#### Adaptive Spectral Subtraction with Voice Preservation

For each frequency bin `k`:

1. **SNR Calculation**:
   ```
   SNR(k) = |X_noisy(k)| / (|N(k)| + ε)
   ```

2. **Adaptive Over-Subtraction Factor**:
   ```
   α_adaptive(k) = α * (1.0 - 0.3 * min(SNR(k) / 3.0, 1.0))
   ```
   This reduces aggressiveness in high-SNR regions (likely speech).

3. **Spectral Subtraction with Voice Mask**:
   ```
   |X_clean(k)| = max(|X_noisy(k)| - α_adaptive(k) * |N(k)|, β * |X_noisy(k)| * V_mask(k))
   ```
   
   Where:
   - `|X_noisy(k)|` = magnitude of noisy signal at frequency k
   - `|N(k)|` = estimated noise magnitude from reference
   - `α` = base over-subtraction factor (1.8)
   - `α_adaptive(k)` = adaptive over-subtraction factor based on SNR
   - `β` = spectral floor factor (0.02)
   - `V_mask(k)` = voice frequency mask (1.3 for 85-4000 Hz, 1.0 otherwise)

4. **Voice Frequency Boost**:
   ```
   |X_clean(k)| = |X_clean(k)| * V_mask(k)
   ```

The phase is preserved from the original signal:
```
X_clean(k) = |X_clean(k)| * exp(j * phase(X_noisy(k)))
```

#### Wiener Filter with Voice Boost

The Wiener filter gain for each frequency bin:

```
H(k) = P_signal(k) / (P_signal(k) + P_noise(k)) * V_boost(k)
```

Where:
- `P_signal(k)` = power spectral density of signal at frequency k
- `P_noise(k)` = power spectral density of noise at frequency k
- `V_boost(k)` = voice boost factor (1.2 for 85-4000 Hz, 1.0 otherwise)

The gain is capped to prevent distortion:
```
H(k) = min(H(k), 1.5)
```

The enhanced signal:
```
X_enhanced(k) = X_clean(k) * H(k)
```

#### Voice Frequency Enhancement

The voice enhancement applies an EQ-like boost:

```
G_voice(k) = {
    10^(boost_db/20)     if 300 ≤ f(k) ≤ 3000 Hz  (core voice)
    1 + (10^(boost_db/20) - 1) * factor  if 85 ≤ f(k) < 300 or 3000 < f(k) ≤ 4000 Hz
    1.0                  otherwise
}
```

Where:
- `f(k)` = frequency at bin k
- `boost_db` = boost in decibels (3 dB)
- `factor` = smooth rolloff factor at edges

The final enhanced signal:
```
X_final(k) = X_enhanced(k) * G_voice(k)
```

## 📡 API Documentation

### Endpoints

#### `GET /`
Serves the main HTML page.

**Response**: HTML content of `index.html`

---

#### `POST /process`
Processes audio files to reduce rain noise using three-stage processing: Spectral Subtraction + Wiener Filter + Voice Enhancement.

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `speech` (file): Noisy speech WAV file
  - `noise` (file): Rain noise reference WAV file

**Response**:
- Success (200): Audio WAV file (binary)
  - Content-Type: `audio/wav`
  - Filename: `output_cleaned.wav`
- Error (400/500): Error message (text)

**Example using curl**:
```bash
curl -X POST http://127.0.0.1:5000/process \
  -F "speech=@noisy_speech.wav" \
  -F "noise=@rain_reference.wav" \
  --output cleaned_output.wav
```

---

#### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

## 📦 Requirements

### Python Packages

```
flask>=3.0.0
numpy>=1.20.0
soundfile>=0.10.0
flask-cors>=3.0.0
```

### System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **RAM**: Minimum 512MB (more recommended for large audio files)
- **Disk Space**: Sufficient space for temporary audio processing

## 🔧 Troubleshooting

### Common Issues

#### "Failed to fetch" Error
- **Cause**: Backend server not running or CORS issues
- **Solution**: 
  1. Ensure the Flask server is running (`python backend/app.py`)
  2. Check that you're accessing `http://127.0.0.1:5000` (not file://)
  3. Verify firewall isn't blocking port 5000

#### "No space left on device" Error
- **Cause**: Insufficient disk space for temporary file processing
- **Solution**: Free up disk space on your system drive

#### "Audio files too short" Error
- **Cause**: Files are shorter than 1024 samples
- **Solution**: Use longer audio files (at least a few seconds)

#### Poor Noise Reduction Results
- **Possible Causes**:
  - Rain reference doesn't match the noise characteristics in speech file
  - Reference file contains speech or other sounds
  - Files are too short (< 1024 samples)
  - Very low signal-to-noise ratio
- **Solutions**:
  - Use a clean rain-only reference recording
  - Ensure reference captures similar rain characteristics (intensity, type)
  - Use longer audio files for better noise estimation
  - Try different rain reference files if available

#### Port Already in Use
- **Cause**: Another process is using port 5000
- **Solution**: 
  ```bash
  # Find and kill the process (Windows)
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # Or change the port in app.py:
  app.run(debug=True, port=5001)
  ```

## 🚀 Future Improvements

Potential enhancements for the project:

- [ ] **Parameter Tuning UI**: Allow users to adjust over-subtraction factor, spectral floor, and frame size
- [ ] **Real-time Processing**: WebSocket support for live audio streaming
- [ ] **Multiple Algorithm Options**: Add support for RLS, Kalman filters, or deep learning approaches
- [ ] **Audio Visualization**: Waveform and spectrogram displays showing before/after
- [ ] **Batch Processing**: Process multiple files at once
- [ ] **Format Support**: Add support for MP3, FLAC, and other audio formats
- [ ] **Quality Metrics**: SNR (Signal-to-Noise Ratio) calculation and display
- [ ] **Machine Learning**: Deep learning-based noise reduction as an alternative
- [ ] **Cloud Deployment**: Docker containerization and cloud hosting options
- [ ] **Noise Profile Learning**: Automatically learn noise characteristics from reference

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📧 Contact

For questions or issues, please open an issue in the project repository.

---

**Note**: This application uses advanced frequency-domain techniques (Adaptive Spectral Subtraction + Wiener Filter + Voice Enhancement) which are highly effective for stationary noise like rain. The three-stage approach with voice preservation provides superior noise reduction while maintaining and enhancing human speech clarity, outperforming time-domain adaptive filters for this use case.
