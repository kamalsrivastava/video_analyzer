import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "../utils/api";
import video from "../assets/uploadvideo.png";
import audio from "../assets/uploadaudio.png";
import checkmark from "../assets/checkmark.png"; // Add a checkmark image in your assets folder

function FileUploader({ setAnalysisResult }) {
  const [file, setFile] = useState(null);
  const [uploaded, setUploaded] = useState({ audio: false, video: false }); // Track successful uploads
  const [error, setError] = useState({ audio: "", video: "" });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (event, type) => {
    const selectedFile = event.target.files[0];
    setError({ audio: "", video: "" }); // Clear any previous errors
    setUploaded({ audio: false, video: false }); // Reset checkmarks

    if (type === "video" && selectedFile && selectedFile.type !== "video/mp4") {
      setError((prev) => ({
        ...prev,
        video: "Please upload a valid MP4 file.",
      }));
      return;
    }

    setFile(selectedFile);
    setUploaded((prev) => ({ ...prev, [type]: true })); // Show the checkmark for the correct button
  };

  const handleUpload = async (type) => {
    if (!file) {
      setError((prev) => ({
        ...prev,
        [type]: `Please upload a ${type} file.`,
      }));
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setIsLoading(true);

    try {
      const response = await axios.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAnalysisResult(response.data);
      navigate("/result");
    } catch (err) {
      console.error("Error uploading file:", err);
      setError((prev) => ({
        ...prev,
        [type]: "Failed to upload the file. Please try again.",
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Video Analyzer</h1>
      <div style={styles.buttonContainer}>
        {/* Video Upload Button */}
        <div style={styles.buttonWrapper}>
          <label htmlFor="video-upload" style={styles.imageButton}>
            <img src={video} alt="Upload Video" style={styles.image} />
          </label>
          <input
            type="file"
            id="video-upload"
            style={styles.hiddenInput}
            onChange={(e) => handleFileChange(e, "video")}
          />
          {uploaded.video && (
            <img src={checkmark} alt="Uploaded" style={styles.checkmark} />
          )}
          <button
            style={styles.uploadButton}
            onClick={(e) => {
              e.preventDefault();
              handleUpload("video");
            }}
          >
            Upload Video
          </button>
          {error.video && <p style={styles.errorText}>{error.video}</p>}
        </div>

        {/* Audio Upload Button */}
        <div style={styles.buttonWrapper}>
          <label htmlFor="audio-upload" style={styles.imageButton}>
            <img src={audio} alt="Upload Audio" style={styles.image} />
          </label>
          <input
            type="file"
            id="audio-upload"
            style={styles.hiddenInput}
            onChange={(e) => handleFileChange(e, "audio")}
          />
          {uploaded.audio && (
            <img src={checkmark} alt="Uploaded" style={styles.checkmark} />
          )}
          <button
            style={styles.uploadButton}
            onClick={(e) => {
              e.preventDefault();
              handleUpload("audio");
            }}
          >
            Upload Audio
          </button>
          {error.audio && <p style={styles.errorText}>{error.audio}</p>}
        </div>
      </div>

      {/* Loader Overlay */}
      {isLoading && (
        <div style={styles.overlay}>
          <div style={styles.loader}></div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "#1c1c1c",
    color: "white",
    padding: "10px",
  },
  title: {
    fontSize: "2rem",
    marginBottom: "40px",
    textAlign: "center",
    color: "white",
  },
  buttonContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "30px", // Space between the buttons
  },
  buttonWrapper: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    position: "relative", // For positioning the checkmark
  },
  imageButton: {
    display: "inline-block",
    cursor: "pointer",
  },
  image: {
    width: "150px",
    height: "150px",
    borderRadius: "8px",
  },
  checkmark: {
    width: "30px",
    height: "30px",
    position: "absolute",
    top: "10px",
    right: "-10px",
  },
  uploadButton: {
    marginTop: "10px",
    padding: "10px 20px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  hiddenInput: {
    display: "none",
  },
  errorText: {
    color: "red",
    marginTop: "10px",
    fontSize: "0.9rem",
  },
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.7)", // Semi-transparent background
    display: "flex",
    justifyContent: "center",
    alignItems: "center", // Center the loader vertically and horizontally
    zIndex: 1000, // Ensure it's above everything
  },
  loader: {
    border: "8px solid #f3f3f3", // Light gray
    borderTop: "8px solid #007bff", // Blue
    borderRadius: "50%",
    width: "50px",
    height: "50px",
    animation: "spin 1s linear infinite",
  },
};

// Add CSS animation for the loader
const styleSheet = document.styleSheets[0];
styleSheet.insertRule(
  `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`,
  styleSheet.cssRules.length
);

export default FileUploader;
