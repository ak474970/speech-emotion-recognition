# Speech Emotion Recognition System

A Python-based Speech Emotion Recognition system that uses audio processing and deep learning to identify emotions from speech audio files.

## Features

- **Audio File Analysis**: Upload and analyze WAV, MP3, or OGG audio files
- **Live Recording**: Record your voice directly in the browser for analysis
- **Visualization**: View waveform and spectrogram visualizations of audio
- **History Tracking**: Access past emotion predictions
- **Responsive Design**: User-friendly interface that works on desktop and mobile devices

## Emotions Detected

- Angry
- Disgust
- Fear
- Happy
- Neutral
- Sad
- Surprise

## Technical Details

The system uses several audio processing techniques to analyze speech:

1. **Audio Preprocessing**: Normalization, silence removal, and noise reduction
2. **Feature Extraction**: MFCCs, spectral features, zero-crossing rate
3. **Deep Learning**: Neural network for emotion classification
4. **Result Analysis**: Confidence scores and visualization

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/YOUR_USERNAME/speech-emotion-recognition.git
   cd speech-emotion-recognition
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   # Set your PostgreSQL database URL as an environment variable
   export DATABASE_URL=postgresql://username:password@localhost:5432/emotion_recognition
   ```

5. Run the application:
   ```
   python main.py
   ```

6. Open your browser and go to `http://localhost:5000`

## Usage

1. **Upload Audio**: Click the "Upload Audio" tab and select an audio file for analysis
2. **Record Audio**: Click the "Record Audio" tab, click "Start Recording", speak, then click "Stop Recording"
3. **View History**: Click the "History" tab or the "History" link in the navigation bar to view past predictions
4. **Train Model**: Access the model training interface via the "Train Model" link (for demonstration purposes)

## Technologies Used

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Librosa**: Audio processing
- **Matplotlib/Seaborn**: Data visualization
- **Bootstrap**: Frontend styling
- **JavaScript**: Recording and interactive features

## License

This project is licensed under the MIT License - see the LICENSE file for details.