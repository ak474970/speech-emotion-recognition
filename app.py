import os
import logging
import tempfile
import json
import base64
import io
import datetime
import numpy as np
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from audio_processor import preprocess_audio
from feature_extractor import extract_features
from emotion_model import EmotionModel, EMOTIONS
from utils import plot_prediction, plot_confusion_matrix, allowed_file, load_sample_audio, plot_audio_waveform, plot_spectrogram

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Define database models directly here
class EmotionPrediction(db.Model):
    """Model to store emotion prediction history"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=True)
    emotion = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    all_confidences = db.Column(db.Text, nullable=False)  # JSON string of all confidence values
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    is_recorded = db.Column(db.Boolean, default=False)  # Whether it was a recorded sample or uploaded file
    waveform_data = db.Column(db.Text, nullable=True)  # JSON string of waveform data for visualization
    
    def __repr__(self):
        return f'<EmotionPrediction {self.emotion} ({self.confidence:.2f}%)>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'filename': self.filename,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'all_confidences': json.loads(self.all_confidences),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_recorded': self.is_recorded,
            'waveform_data': json.loads(self.waveform_data) if self.waveform_data else None
        }

# Set maximum file size for uploads (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize emotion model
emotion_model = EmotionModel()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Process audio file and make emotion prediction"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file temporarily
            filename = secure_filename(file.filename or "uploaded_audio.wav")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process audio and extract features
            preprocessed_audio = preprocess_audio(filepath)
            audio_data, sr = preprocessed_audio  # Unpack audio data and sample rate
            features = extract_features(preprocessed_audio)
            
            # Make prediction
            prediction, confidence = emotion_model.predict(features)
            
            # Generate visualizations
            prediction_chart = plot_prediction(prediction, confidence)
            waveform_chart, waveform_data = plot_audio_waveform(audio_data, sr)
            spectrogram_chart = plot_spectrogram(audio_data, sr)
            
            # Save prediction to database
            from models import EmotionPrediction
            prediction_record = EmotionPrediction(
                filename=os.path.basename(filepath) if file.filename else None,
                emotion=prediction,
                confidence=confidence[prediction],
                all_confidences=json.dumps(confidence),
                is_recorded=False,
                waveform_data=waveform_data
            )
            db.session.add(prediction_record)
            db.session.commit()
            
            # Clean up the temporary file
            os.remove(filepath)
            
            return render_template(
                'results.html', 
                prediction=prediction,
                confidence=confidence,
                chart=prediction_chart,
                waveform_chart=waveform_chart,
                spectrogram_chart=spectrogram_chart,
                emotions=EMOTIONS,
                record_id=prediction_record.id
            )
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            flash(f'Error processing audio: {str(e)}', 'danger')
            return redirect(url_for('index'))
    else:
        flash('Allowed file types are .wav, .mp3, .ogg', 'warning')
        return redirect(url_for('index'))

@app.route('/record', methods=['POST'])
def process_recording():
    """Process recorded audio and make emotion prediction"""
    try:
        # Get audio data from request
        audio_data = request.json.get('audio')
        if not audio_data:
            return jsonify({'error': 'No audio data received'}), 400
        
        # Decode base64 audio data
        encoded_data = audio_data.split(',')[1]
        binary_data = base64.b64decode(encoded_data)
        
        # Save audio to temporary file
        temp_file = os.path.join(app.config['UPLOAD_FOLDER'], 'recorded_audio.wav')
        with open(temp_file, 'wb') as f:
            f.write(binary_data)
        
        # Process audio and extract features
        preprocessed_audio = preprocess_audio(temp_file)
        audio_data, sr = preprocessed_audio  # Unpack audio data and sample rate
        features = extract_features(preprocessed_audio)
        
        # Make prediction
        prediction, confidence = emotion_model.predict(features)
        
        # Generate visualizations
        prediction_chart = plot_prediction(prediction, confidence)
        waveform_chart, waveform_data = plot_audio_waveform(audio_data, sr)
        spectrogram_chart = plot_spectrogram(audio_data, sr)
        
        # Save prediction to database
        from models import EmotionPrediction
        prediction_record = EmotionPrediction(
            filename='recorded_audio.wav',
            emotion=prediction,
            confidence=confidence[prediction],
            all_confidences=json.dumps(confidence),
            is_recorded=True,
            waveform_data=waveform_data
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        # Clean up the temporary file
        os.remove(temp_file)
        
        return jsonify({
            'success': True,
            'redirect': url_for('results', record_id=prediction_record.id)
        })
        
    except Exception as e:
        logger.error(f"Error processing recorded audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/results/<int:record_id>')
def results(record_id):
    """Show results for a specific prediction"""
    try:
        # Get prediction from database
        prediction_record = db.session.get_or_404(EmotionPrediction, record_id)
        
        if not prediction_record:
            flash('Prediction record not found', 'danger')
            return redirect(url_for('index'))
        
        # Load confidence values from JSON
        confidence = json.loads(prediction_record.all_confidences)
        
        # Generate prediction chart
        prediction_chart = plot_prediction(prediction_record.emotion, confidence)
        
        # If there's waveform data, use it to create a waveform chart
        waveform_chart = None
        spectrogram_chart = None
        if prediction_record.waveform_data:
            try:
                # For demonstration, we'll just show a placeholder chart
                waveform_data = json.loads(prediction_record.waveform_data)
                if 'audio' in waveform_data and 'times' in waveform_data:
                    # Import matplotlib here to avoid global import issues
                    import matplotlib.pyplot as plt
                    import io
                    
                    # Plot from stored data
                    plt.figure(figsize=(10, 3))
                    plt.plot(waveform_data['times'], waveform_data['audio'], color='#3498db')
                    plt.title('Audio Waveform')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
                    plt.ylim(-1.1, 1.1)
                    plt.tight_layout()
                    
                    # Save plot to a bytes buffer
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    
                    # Convert plot to base64 string
                    waveform_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
                    plt.close()
            except Exception as e:
                logger.error(f"Error generating waveform chart: {str(e)}")
        
        return render_template(
            'results.html', 
            prediction=prediction_record.emotion,
            confidence=confidence,
            chart=prediction_chart,
            waveform_chart=waveform_chart,
            spectrogram_chart=spectrogram_chart,
            emotions=EMOTIONS,
            record_id=record_id,
            timestamp=prediction_record.timestamp,
            is_recorded=prediction_record.is_recorded
        )
        
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        flash(f'Error displaying results: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/sample/<sample_name>')
def analyze_sample(sample_name):
    """Analyze a sample audio file"""
    try:
        # Load sample audio
        audio_path = load_sample_audio(sample_name)
        
        # Process audio and extract features
        preprocessed_audio = preprocess_audio(audio_path)
        audio_data, sr = preprocessed_audio  # Unpack audio data and sample rate
        features = extract_features(preprocessed_audio)
        
        # Make prediction
        prediction, confidence = emotion_model.predict(features)
        
        # Generate visualizations
        prediction_chart = plot_prediction(prediction, confidence)
        waveform_chart, waveform_data = plot_audio_waveform(audio_data, sr)
        spectrogram_chart = plot_spectrogram(audio_data, sr)
        
        # Save prediction to database
        from models import EmotionPrediction
        prediction_record = EmotionPrediction(
            filename=f"{sample_name}.wav",
            emotion=prediction,
            confidence=confidence[prediction],
            all_confidences=json.dumps(confidence),
            is_recorded=False,
            waveform_data=waveform_data
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        return render_template(
            'results.html', 
            prediction=prediction,
            confidence=confidence,
            chart=prediction_chart,
            waveform_chart=waveform_chart,
            spectrogram_chart=spectrogram_chart,
            emotions=EMOTIONS,
            record_id=prediction_record.id,
            is_sample=True,
            sample_name=sample_name
        )
        
    except Exception as e:
        logger.error(f"Error processing sample audio: {str(e)}")
        flash(f'Error processing sample audio: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    """Show history of emotion predictions"""
    try:
        # Get predictions from database
        from models import EmotionPrediction
        predictions = EmotionPrediction.query.order_by(EmotionPrediction.timestamp.desc()).limit(10).all()
        
        return render_template(
            'history.html',
            predictions=predictions,
            emotions=EMOTIONS
        )
        
    except Exception as e:
        logger.error(f"Error displaying history: {str(e)}")
        flash(f'Error displaying history: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/train')
def train_page():
    """Training page"""
    # This would be enhanced with proper dataset upload and training in a real application
    return render_template('train.html')

@app.route('/train/start', methods=['POST'])
def start_training():
    """Start the training process"""
    try:
        # In a real application, we'd handle dataset upload and verification
        epochs = int(request.form.get('epochs', 10))
        
        # Train model (simplified for demonstration)
        history, accuracy, confusion_mat = emotion_model.train(epochs=epochs)
        
        # Generate confusion matrix visualization
        cm_chart = plot_confusion_matrix(confusion_mat, EMOTIONS)
        
        flash(f'Model trained successfully with {accuracy:.2f}% accuracy', 'success')
        
        return render_template(
            'train.html', 
            trained=True, 
            accuracy=accuracy,
            cm_chart=cm_chart,
            history=history
        )
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        flash(f'Error during training: {str(e)}', 'danger')
        return redirect(url_for('train_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
