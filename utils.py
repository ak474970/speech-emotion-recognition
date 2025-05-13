"""
Utility functions for Speech Emotion Recognition
"""
import os
import base64
import logging
import io
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import librosa
import librosa.display
from sklearn.metrics import confusion_matrix

logger = logging.getLogger(__name__)

# Define allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

def allowed_file(filename):
    """
    Check if a file has an allowed extension
    
    Args:
        filename: Name of the file to check
        
    Returns:
        allowed: Whether the file has an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def plot_prediction(emotion, confidences):
    """
    Create a bar chart of emotion prediction confidences
    
    Args:
        emotion: Predicted emotion
        confidences: Dictionary of confidence values for each emotion
        
    Returns:
        image_base64: Base64-encoded image
    """
    try:
        plt.figure(figsize=(10, 6))
        
        # Sort emotions by confidence
        emotions = list(confidences.keys())
        values = [confidences[e] for e in emotions]
        
        # Create bar chart
        colors = ['#3498db'] * len(emotions)
        
        # Highlight the predicted emotion
        pred_idx = emotions.index(emotion)
        colors[pred_idx] = '#e74c3c'
        
        # Create the bar chart
        ax = sns.barplot(x=emotions, y=values, palette=colors)
        
        # Customize the chart
        plt.title('Emotion Prediction Confidence', fontsize=16)
        plt.xlabel('Emotion', fontsize=14)
        plt.ylabel('Confidence (%)', fontsize=14)
        plt.ylim(0, 100)
        
        # Add value labels on top of each bar
        for i, v in enumerate(values):
            ax.text(i, v + 2, f"{v:.1f}%", ha='center', fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Make plot look better
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert plot to base64 string
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating prediction plot: {str(e)}")
        return ""

def plot_confusion_matrix(cm, class_names):
    """
    Create a confusion matrix visualization
    
    Args:
        cm: Confusion matrix
        class_names: List of class names
        
    Returns:
        image_base64: Base64-encoded image
    """
    try:
        plt.figure(figsize=(10, 8))
        
        # Normalize confusion matrix
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Create heatmap
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt='.2f',
            cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names
        )
        
        # Add labels and title
        plt.ylabel('True Emotion')
        plt.xlabel('Predicted Emotion')
        plt.title('Confusion Matrix')
        
        # Make plot look better
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert plot to base64 string
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating confusion matrix plot: {str(e)}")
        return ""

def plot_audio_waveform(audio, sr):
    """
    Create a waveform visualization of the audio
    
    Args:
        audio: Audio time series
        sr: Sampling rate
        
    Returns:
        image_base64: Base64-encoded image
        waveform_data: Downsampled waveform data for storing in database
    """
    try:
        plt.figure(figsize=(10, 3))
        
        # Plot waveform
        plt.plot(np.linspace(0, len(audio) / sr, len(audio)), audio, color='#3498db')
        
        # Add labels and title
        plt.title('Audio Waveform')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        
        # Add a horizontal line at y=0
        plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        
        # Set y-axis limits
        plt.ylim(-1.1, 1.1)
        
        # Make plot look better
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert plot to base64 string
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        # Downsample audio for storage in database
        # We'll keep ~1000 points for visualization
        samples_to_keep = 1000
        if len(audio) > samples_to_keep:
            downsample_factor = len(audio) // samples_to_keep
            downsampled_audio = audio[::downsample_factor][:samples_to_keep].tolist()
        else:
            downsampled_audio = audio.tolist()
        
        # Create waveform data object
        waveform_data = {
            'audio': downsampled_audio,
            'times': np.linspace(0, len(audio) / sr, len(downsampled_audio)).tolist()
        }
        
        return image_base64, json.dumps(waveform_data)
        
    except Exception as e:
        logger.error(f"Error creating waveform plot: {str(e)}")
        return "", json.dumps({})

def plot_spectrogram(audio, sr):
    """
    Create a spectrogram visualization of the audio
    
    Args:
        audio: Audio time series
        sr: Sampling rate
        
    Returns:
        image_base64: Base64-encoded image
    """
    try:
        plt.figure(figsize=(10, 5))
        
        # Compute spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
        
        # Plot spectrogram
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        
        # Add title
        plt.title('Spectrogram')
        
        # Make plot look better
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert plot to base64 string
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating spectrogram plot: {str(e)}")
        return ""

def load_sample_audio(sample_name):
    """
    Load a sample audio file
    
    This function returns the path to a sample audio file for demonstration purposes.
    
    Args:
        sample_name: Name of the sample audio file
        
    Returns:
        audio_path: Path to the sample audio file
    """
    # Get the samples directory
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    
    # Define the sample path
    sample_path = os.path.join(sample_dir, f"{sample_name}.wav")
    
    # Create a placeholder sample file if it doesn't exist
    if not os.path.exists(sample_path):
        logger.warning(f"Sample file {sample_path} not found. Creating a placeholder.")
        # For demonstration purposes, we'll create an empty file
        # In a real app, we would have pre-recorded sample files
        with open(sample_path, 'wb') as f:
            # Write a minimal WAV file header
            f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
    
    return sample_path
