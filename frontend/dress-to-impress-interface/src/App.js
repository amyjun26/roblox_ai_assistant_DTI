import React, { useEffect, useState } from "react";
import "./index.css";

function App() {
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [actualResult, setActualResult] = useState("");
  const [waitingForGame, setIsWaitingForGame] = useState(true);
  const [actualImageURL, setActualImageURL] = useState("");
  const [theme, setTheme] = useState("");

  const socket = new WebSocket("ws://localhost:8080/ws");
  socket.addEventListener("message", (event) => {
    let payload = JSON.parse(event.data);
    if (payload.complete) {
      console.log(payload);
      const rating = payload.num_stars / payload.num_players;
      setActualResult(rating * 2 + "/10");
      setActualImageURL(payload.outfit);
      setTheme(payload.theme);
    }
  });

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
            image_url: actualImageURL,
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
  }, []);

  const getRandomImage = (folder, numImages) => {
    const randomIndex = Math.floor(Math.random() * numImages) + 1; // +1 because images are 1-indexed
    return `${folder}/item${randomIndex}.jpg`;
  };

  // Number of images in each folder
  const numHairImages = 85;
  const numMakeupImages = 23;
  const numTopsImages = 98;
  const numPantsImages = 30;

  // Generate image paths
  const selectedImages = {
    hair: getRandomImage("images/hair", numHairImages),
    makeup: getRandomImage("images/makeup", numMakeupImages),
    tops: getRandomImage("images/items/free_tops", numTopsImages),
    pants: getRandomImage("images/items/free_skirts", numPantsImages),
  };

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
                AI Score: {score}/10
              </h3>
              <h3 className="text-xl font-bold text-pink-600 mb-4">
                Game Score: {actualResult}/10
              </h3>
              <p className="text-pink-700">{feedback}</p>
              <br></br>
              <br></br>
              <h3 className="text-xl font-bold text-pink-600 mb-4">
                You can also consider using these items next time:
              </h3>
              <div className="flex justify-center space-x-4 p-4">
                <img
                  src={`/${selectedImages.hair}`}
                  alt="Random Hair"
                  className="w-32 h-32 object-cover"
                />
                <img
                  src={`/${selectedImages.makeup}`}
                  alt="Random Makeup"
                  className="w-32 h-32 object-cover"
                />
                <img
                  src={`/${selectedImages.tops}`}
                  alt="Random Top"
                  className="w-32 h-32 object-cover"
                />
                <img
                  src={`/${selectedImages.pants}`}
                  alt="Random Pants"
                  className="w-32 h-32 object-cover"
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
