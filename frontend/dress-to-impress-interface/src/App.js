import React, { useState, useEffect } from "react";

function App() {
  const [judgesResponses, setJudgesResponses] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJudgesResponses = async () => {
      try {
        // Make the API request to the Flask server
        const response = await fetch("http://localhost:5000/evaluate", {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        // Parse the JSON response
        const data = await response.json();

        // Update the state with the received data
        setJudgesResponses(data);
      } catch (error) {
        console.error("Error fetching judges' responses:", error);
        setError(error.message);
      }
    };

    // Call the fetch function when the component mounts
    fetchJudgesResponses();
  }, []);

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
