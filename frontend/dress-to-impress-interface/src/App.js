import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [judgesResponses, setJudgesResponses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch the data from the Flask API
  useEffect(() => {
    fetch("http://localhost:3000/api/judges_responses")
      .then((response) => response.json())
      .then((data) => {
        setJudgesResponses(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching judges' responses:", error);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="App">
      <h1>Dress to Impress - Judges' Feedback</h1>
      <div className="judge-container">
        {judgesResponses.map((response, index) => (
          <div key={index} className="judge-response">
            <h2>{response.judge}</h2>
            <p>{response.feedback}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
