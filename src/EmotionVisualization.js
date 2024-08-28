import React from 'react';
import { useLocation } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

function EmotionVisualization() {
  const location = useLocation();
  const emotions = location.state?.emotions || []; 

  console.log("Emotions Data in Visualization:", emotions); 

  // Ensure emotions is an array
  const data = Array.isArray(emotions) ? emotions : [];

  return (
    <div className="emotion-visualization">
      <h2>Emotion Analysis</h2>
      {data.length > 0 ? (
        <BarChart width={600} height={300} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="percentage" fill="#8884d8" />
        </BarChart>
      ) : (
        <p>No emotions detected</p>
      )}
    </div>
  );
}

export default EmotionVisualization;
