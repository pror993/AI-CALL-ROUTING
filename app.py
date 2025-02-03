import streamlit as st
import sounddevice as sd
import numpy as np
import whisper
import threading
import queue
import tempfile
from scipy.io.wavfile import write

class AudioTranscriber:
    def __init__(self):
        self.model = whisper.load_model("base")  # Use "tiny", "base", "small", "medium", or "large"
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.sample_rate = 16000

    def record_audio(self):
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_queue.put(indata.copy())

        with sd.InputStream(callback=callback, 
                          channels=1,
                          samplerate=self.sample_rate,
                          dtype=np.float32):
            while self.is_recording:
                sd.sleep(100)

    def transcribe_audio(self, audio_data):
        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
            write(temp_audio.name, self.sample_rate, audio_data)
            
            # Transcribe using Whisper
            result = self.model.transcribe(temp_audio.name)
            return result["text"]

def main():
    st.title("Real-time Speech Transcription")
    
    transcriber = AudioTranscriber()
    
    # Initialize session state variables
    if 'text_output' not in st.session_state:
        st.session_state.text_output = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Push-to-Talk button
        if st.button("Push to Talk", key="talk_button", 
                    help="Hold to record audio"):
            transcriber.is_recording = True
            audio_data = []
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(
                target=transcriber.record_audio)
            recording_thread.start()
            
            st.write("Recording... Release button to stop.")
            
            # Wait for button release
            while transcriber.is_recording:
                try:
                    audio_chunk = transcriber.audio_queue.get(timeout=0.1)
                    audio_data.append(audio_chunk)
                except queue.Empty:
                    continue
            
            if audio_data:
                # Combine all audio chunks
                combined_audio = np.concatenate(audio_data)
                
                # Transcribe the audio
                transcription = transcriber.transcribe_audio(combined_audio)
                
                # Update the output text
                st.session_state.text_output += " " + transcription
    
    with col2:
        if st.button("Clear Transcript"):
            st.session_state.text_output = ""
    
    # Display transcribed text
    st.text_area("Transcription", 
                 value=st.session_state.text_output,
                 height=200)

if __name__ == "__main__":
    main()
