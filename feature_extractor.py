"""
Feature extraction module for Speech Emotion Recognition
Extracts acoustic features from audio files
"""
import logging
import numpy as np
import librosa

logger = logging.getLogger(__name__)

def extract_mfcc(audio, sr, n_mfcc=13, n_fft=2048, hop_length=512):
    """
    Extract Mel-Frequency Cepstral Coefficients (MFCCs)
    
    Args:
        audio: Audio time series
        sr: Sampling rate
        n_mfcc: Number of MFCCs to extract
        n_fft: FFT window size
        hop_length: Number of samples between successive frames
        
    Returns:
        mfccs: MFCCs features
    """
    try:
        mfccs = librosa.feature.mfcc(
            y=audio, 
            sr=sr, 
            n_mfcc=n_mfcc,
            n_fft=n_fft,
            hop_length=hop_length
        )
        # Normalize MFCCs
        mfccs = (mfccs - np.mean(mfccs, axis=1, keepdims=True)) / (np.std(mfccs, axis=1, keepdims=True) + 1e-8)
        return mfccs
    except Exception as e:
        logger.error(f"Error extracting MFCCs: {str(e)}")
        raise

def extract_spectral_features(audio, sr, n_fft=2048, hop_length=512):
    """
    Extract spectral features (spectral centroid, bandwidth, roll-off)
    
    Args:
        audio: Audio time series
        sr: Sampling rate
        n_fft: FFT window size
        hop_length: Number of samples between successive frames
        
    Returns:
        spectral_features: Dictionary of spectral features
    """
    try:
        spectral_features = {}
        
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio, 
            sr=sr, 
            n_fft=n_fft, 
            hop_length=hop_length
        )[0]
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio, 
            sr=sr, 
            n_fft=n_fft, 
            hop_length=hop_length
        )[0]
        
        # Spectral roll-off
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, 
            sr=sr, 
            n_fft=n_fft, 
            hop_length=hop_length
        )[0]
        
        # Normalize features
        spectral_features['centroid'] = (spectral_centroids - np.mean(spectral_centroids)) / (np.std(spectral_centroids) + 1e-8)
        spectral_features['bandwidth'] = (spectral_bandwidth - np.mean(spectral_bandwidth)) / (np.std(spectral_bandwidth) + 1e-8)
        spectral_features['rolloff'] = (spectral_rolloff - np.mean(spectral_rolloff)) / (np.std(spectral_rolloff) + 1e-8)
        
        return spectral_features
    
    except Exception as e:
        logger.error(f"Error extracting spectral features: {str(e)}")
        raise

def extract_zero_crossing_rate(audio, hop_length=512):
    """
    Extract zero crossing rate
    
    Args:
        audio: Audio time series
        hop_length: Number of samples between successive frames
        
    Returns:
        zcr: Zero crossing rate
    """
    try:
        zcr = librosa.feature.zero_crossing_rate(
            y=audio,
            hop_length=hop_length
        )[0]
        return zcr
    except Exception as e:
        logger.error(f"Error extracting zero crossing rate: {str(e)}")
        raise

def extract_chroma_features(audio, sr, n_fft=2048, hop_length=512, n_chroma=12):
    """
    Extract chroma features
    
    Args:
        audio: Audio time series
        sr: Sampling rate
        n_fft: FFT window size
        hop_length: Number of samples between successive frames
        n_chroma: Number of chroma bins
        
    Returns:
        chroma: Chroma features
    """
    try:
        chroma = librosa.feature.chroma_stft(
            y=audio, 
            sr=sr, 
            n_fft=n_fft, 
            hop_length=hop_length, 
            n_chroma=n_chroma
        )
        return chroma
    except Exception as e:
        logger.error(f"Error extracting chroma features: {str(e)}")
        raise

def extract_features(audio_data, sr=22050, n_mfcc=13, n_fft=2048, hop_length=512):
    """
    Extract combined features from audio data
    
    Args:
        audio_data: Tuple of (audio, sr) or just audio time series
        sr: Sampling rate (used if audio_data is just the time series)
        n_mfcc: Number of MFCCs to extract
        n_fft: FFT window size
        hop_length: Number of samples between successive frames
        
    Returns:
        features: Dictionary of features or padded features ready for model
    """
    try:
        # Handle both (audio, sr) tuple or just audio input
        if isinstance(audio_data, tuple):
            audio, sr = audio_data
        else:
            audio = audio_data
        
        # Extract features
        mfccs = extract_mfcc(audio, sr, n_mfcc, n_fft, hop_length)
        spectral = extract_spectral_features(audio, sr, n_fft, hop_length)
        zcr = extract_zero_crossing_rate(audio, hop_length)
        chroma = extract_chroma_features(audio, sr, n_fft, hop_length)
        
        # Transpose to get time as first dimension
        mfccs = mfccs.T  # Shape: (time_steps, n_mfcc)
        
        # Ensure all features have the same length by padding or truncating
        target_length = mfccs.shape[0]
        
        # Reshape spectral features to match MFCC time steps
        spectral_features = np.vstack([
            np.pad(spectral['centroid'], (0, max(0, target_length - len(spectral['centroid']))), 'constant')[:target_length],
            np.pad(spectral['bandwidth'], (0, max(0, target_length - len(spectral['bandwidth']))), 'constant')[:target_length],
            np.pad(spectral['rolloff'], (0, max(0, target_length - len(spectral['rolloff']))), 'constant')[:target_length],
        ]).T
        
        # Reshape ZCR to match MFCC time steps
        zcr_reshaped = np.pad(zcr, (0, max(0, target_length - len(zcr))), 'constant')[:target_length].reshape(-1, 1)
        
        # Reshape chroma to match MFCC time steps
        chroma_reshaped = chroma.T
        if chroma_reshaped.shape[0] < target_length:
            pad_width = ((0, target_length - chroma_reshaped.shape[0]), (0, 0))
            chroma_reshaped = np.pad(chroma_reshaped, pad_width, 'constant')
        else:
            chroma_reshaped = chroma_reshaped[:target_length, :]
        
        # Combine all features
        combined_features = np.hstack([mfccs, spectral_features, zcr_reshaped, chroma_reshaped])
        
        # Add batch dimension for model input
        model_input = np.expand_dims(combined_features, axis=0)
        
        return model_input
    
    except Exception as e:
        logger.error(f"Error extracting combined features: {str(e)}")
        raise
