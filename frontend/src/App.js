import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FileUploader from "./components/FileUploader";
import ResultPage from "./components/ResultPage";

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  // Check if the application is opened on a mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768); // Adjust width as per your mobile breakpoint
    };

    checkMobile(); // Initial check
    window.addEventListener("resize", checkMobile); // Re-check on window resize

    return () => window.removeEventListener("resize", checkMobile); // Cleanup
  }, []);

  return (
    <>
      {isMobile ? (
        // Render the app content for mobile devices
        <Router>
          <Routes>
            <Route
              path="/"
              element={<FileUploader setAnalysisResult={setAnalysisResult} />}
            />
            <Route
              path="/result"
              element={<ResultPage analysisResult={analysisResult} />}
            />
          </Routes>
        </Router>
      ) : (
        // Render a message for non-mobile devices
        <div style={styles.desktopMessage}>
          <h1>This application is available only on mobile devices.</h1>
        </div>
      )}
    </>
  );
}

const styles = {
  desktopMessage: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#1c1c1c",
    color: "white",
    textAlign: "center",
    padding: "20px",
  },
};

export default App;
