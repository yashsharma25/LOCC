import React from 'react';
import API from '../api';

export default function RunProtocolButton({ setVideoUrl }) {
  const runProtocol = async () => {
    try {
      const res = await API.post('/generate_video');
      const videoUrl = res.data.video_url;
      setVideoUrl(`http://localhost:8000${videoUrl}`);
    } catch (err) {
      alert('Failed to generate video: ' + err.message);
    }
  };

  return (
    <div>
      <h2>Execute Protocol</h2>
      <button onClick={runProtocol}>Run and Generate Video</button>
    </div>
  );
}
