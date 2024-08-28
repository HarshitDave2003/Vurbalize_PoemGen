import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import { useSpring, animated } from '@react-spring/web';
import { useNavigate } from 'react-router-dom';
import './App.css';

const socket = io('http://localhost:5000');

function App() {
  const [poemWords, setPoemWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emotions, setEmotions] = useState([]);

  const navigate = useNavigate();

  const typewriterEffect = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    config: { duration: 50 },
    reset: true,
  });

  useEffect(() => {
    socket.on('text_stream', (data) => {
      console.log("Received text stream:", data);
      const words = data.text.split(' ').filter(word => word !== '');
      setPoemWords((prev) => [...prev, ...words]);
    });

    socket.on('emotion_analysis', (data) => {
      console.log("Received emotion analysis:", data);
      setEmotions(data.emotions);
      setLoading(false);
    });

    socket.on('error', (data) => {
      console.log("Received error:", data);
      setError(data.error);
      setLoading(false);
    });

    return () => {
      socket.off('text_stream');
      socket.off('emotion_analysis');
      socket.off('error');
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setPoemWords([]);
    setError('');

    const prompt = e.target.prompt.value;
    console.log("Submitting prompt:", prompt);
    socket.emit('stream_text', { prompt });
  };

  const handleAnalyzeEmotions = () => {
    console.log("Navigating to emotion visualization with data:", emotions);
    navigate('/emotions', { state: { emotions } });
  };

  return (
    <div className="App">
      <h1>Poem Generator</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" name="prompt" placeholder="Enter your poem prompt" required />
        <button type="submit">Generate Poem</button>
      </form>
      {loading && <p className="loading">Generating...</p>}
      {error && <p className="error">Error: {error}</p>}
      {poemWords.length > 0 && (
        <div className="poem-container">
          <h2 className="poem-heading">Generated Poem</h2>
          <div className="poem">
            {poemWords.join(' ')}
          </div>
        </div>
      )}
      {poemWords.length > 0 && (
        <button onClick={handleAnalyzeEmotions} className="analyze-emotions">Analyze Emotions</button>
      )}
    </div>
  );
}

export default App;
