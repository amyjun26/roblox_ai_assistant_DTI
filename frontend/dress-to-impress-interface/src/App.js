import React, { useEffect, useState } from "react";
import "./index.css";
function App() {
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [waitingForGame, setIsWaitingForGame] = useState(true);
  const theme = "kids show";
  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        setIsLoading(true);
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
        setScore(result.avg_score);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    // Call fetchFeedback function when component mounts
    fetchFeedback();

    const socket = new WebSocket("ws://localhost:8080/ws");
    socket.addEventListener("message", (event) => {
      let payload = JSON.parse(event.data);

      if (payload.complete) {
        console.log(payload);
      }
    });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-pink-100">
      <div className="flex flex-col items-center">
        <img src="/dti.webp" alt="logo" className="mb-4 w-100" />
        <div className="bg-pink-200 p-8 rounded-lg shadow-lg w-full max-w-md text-center">
          <h2 className="text-2xl font-bold text-pink-600 mb-6">
            Dress to Impress AI Coach
          </h2>
          {isLoading ? (
            <p className="text-pink-500 animate-pulse">Fetching feedback...</p>
          ) : error ? (
            <p className="text-red-600">Error: {error}</p>
          ) : (
            <>
              <h3 className="text-xl font-bold text-pink-600 mb-4">
                Score: {score}/10
              </h3>
              <p className="text-pink-700">{feedback}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
