import React from 'react';

export default function VideoPlayer({ videoUrl }) {
  if (!videoUrl) return null;

  return (
    <div>
      <h2>Visualization Output</h2>
      <video width="640" controls>
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
}
