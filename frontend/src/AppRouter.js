import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import App from './App';
import EmotionVisualization from './EmotionVisualization';

function AppRouter() {
  const [emotions, setEmotions] = useState([]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<App setEmotions={setEmotions} />} />
        <Route path="/emotions" element={<EmotionVisualization emotions={emotions} />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
