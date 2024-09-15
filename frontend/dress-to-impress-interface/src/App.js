import React, { useState, useEffect } from "react";

function App() {
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");
  const theme = "kids show";
  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/synthesize", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            image_url:
              "https://i.kinja-img.com/image/upload/c_fit,q_60,w_645/c23152596efe8dd4c94cdf7afb233e67.jpg",
            theme: theme,
          }),
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const result = await response.json();
        // Process the feedback and update state
        setFeedback(result.feedback);
      } catch (err) {
        setError(err.message);
      }
    };

    // Call fetchFeedback function when component mounts
    fetchFeedback();
  }, []);

  return (
    <div className="App">
      <h1>Dress to Impress - Overall Feedback</h1>
      <div className="judge-container">{feedback}</div>
    </div>
  );
}

export default App;
