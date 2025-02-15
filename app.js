import React, { useState, useRef } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import AudioPlayer from './components/AudioPlayer';
import SubtitleOverlay from './components/SubtitleOverlay';

function App() {
  const [pdf, setPdf] = useState(null);
  const [voiceId, setVoiceId] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [subtitles, setSubtitles] = useState([]);
  const [audioDuration, setAudioDuration] = useState(0);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);

  const handleFileChange = (e) => setPdf(e.target.files[0]);
  const handleVoiceChange = (e) => setVoiceId(e.target.value);

  const handleSubmit = async () => {
    if (!pdf || !voiceId) {
      alert('Please select a PDF file and voice ID');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('pdf', pdf);
    formData.append('voice_id', voiceId);

    try {
      const response = await axios.post('http://localhost:8000/process_pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setAudioUrl(response.data.audio_url);
      setSubtitles(response.data.subtitles);
      setAudioDuration(response.data.audio_duration);

      // Adjust video loop based on the audio duration
      if (videoRef.current && response.data.audio_duration > videoRef.current.duration) {
        videoRef.current.loop = true;
      }
    } catch (error) {
      console.error('Error uploading PDF:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>PDF to Audio with Voice Selection</h1>

      <FileUpload onFileChange={handleFileChange} />
      
      <div>
        <select value={voiceId} onChange={handleVoiceChange}>
          <option value="">Select Voice</option>
          <option value="voice1">Voice 1</option>
          <option value="voice2">Voice 2</option>
          <option value="voice3">Voice 3</option>
        </select>
      </div>

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Convert PDF to Audio'}
      </button>

      {audioUrl && (
        <div>
          <video ref={videoRef} width="600" controls poster="path_to_video_poster.jpg">
            <source src="path_to_fixed_video.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          {/* Audio Player */}
          <AudioPlayer audioUrl={audioUrl} />
          
          {/* Subtitles */}
          <SubtitleOverlay subtitles={subtitles} audioDuration={audioDuration} />
        </div>
      )}
    </div>
  );
}

export default App;
