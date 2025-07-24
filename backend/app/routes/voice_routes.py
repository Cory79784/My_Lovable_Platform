import os
import tempfile
import whisper
import logging
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import aiofiles

router = APIRouter()

# Initialize Whisper model globally
model = None

def get_whisper_model():
    """Get or initialize local Whisper model"""
    global model
    if model is None:
        try:
            # Load base model for better accuracy
            # You can change to "tiny", "small", "medium", "large" based on your needs
            model = whisper.load_model("base")
            logging.info("Local Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            # Fallback to smaller model if base fails
            try:
                model = whisper.load_model("tiny")
                logging.info("Fallback to tiny Whisper model")
            except Exception as e2:
                logging.error(f"Error loading tiny Whisper model: {e2}")
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to load local speech recognition model"
                )
    return model

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio to text using local Whisper model
    Supports: wav, mp3, m4a, flac, ogg, webm
    """
    try:
        # Validate file type
        allowed_types = [
            "audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", 
            "audio/flac", "audio/ogg", "audio/webm"
        ]
        
        if file.content_type not in allowed_types:
            # Check file extension as fallback
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm']:
                raise HTTPException(
                    status_code=400, 
                    detail="Unsupported audio format. Supported formats: wav, mp3, m4a, flac, ogg, webm"
                )
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Save uploaded audio file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Get local Whisper model
            whisper_model = get_whisper_model()
            
            # Transcribe audio using local model
            logging.info(f"Transcribing audio file: {file.filename}")
            result = whisper_model.transcribe(
                temp_file_path,
                language=None,  # Auto-detect language
                task="transcribe"  # or "translate" for translation
            )
            
            # Extract transcribed text
            transcribed_text = result["text"].strip()
            
            logging.info(f"Transcription successful: {len(transcribed_text)} characters")
            
            return JSONResponse(content={
                "success": True,
                "text": transcribed_text,
                "language": result.get("language", "unknown"),
                "confidence": result.get("confidence", 0.0)
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logging.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Local transcription failed: {str(e)}")

@router.get("/health")
async def voice_health_check():
    """Health check for local voice recognition service"""
    try:
        model = get_whisper_model()
        return JSONResponse(content={
            "status": "healthy",
            "model_loaded": model is not None,
            "model_type": "local_whisper",
            "message": "Local voice recognition service is ready"
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e)
        }, status_code=500) 