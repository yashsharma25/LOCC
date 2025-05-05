import React, { useState } from 'react';
import QuantumStateForm from './components/QuantumStateForm';
import LOCCProtocolForm from './components/LOCCProtocolForm';
import ExecutionTypeSelector from './components/ExecutionTypeSelector';
import RunProtocolButton from './components/RunProtocolButton';
import VideoPlayer from './components/VideoPlayer';

export default function App() {
  const [videoUrl, setVideoUrl] = useState('');

  return (
    <div>
      <h1>Quantum LOCC Visualizer</h1>
      <QuantumStateForm />
      <LOCCProtocolForm />
      <ExecutionTypeSelector />
      <RunProtocolButton setVideoUrl={setVideoUrl} />
      <VideoPlayer videoUrl={videoUrl} />
    </div>
  );
}
