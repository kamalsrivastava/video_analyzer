import React from "react";
import { useNavigate } from "react-router-dom";

function ResultPage({ analysisResult }) {
  const navigate = useNavigate();

  if (!analysisResult) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <div style={styles.backArrow} onClick={() => navigate("/")}></div>
          <h1 style={styles.title}>Video Summary & Issues</h1>
        </div>
        <p style={styles.noAnalysisText}>
          No analysis available. Please upload a file first.
        </p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.backArrow} onClick={() => navigate("/")}></div>
        <h1 style={styles.title}>Video Summary & Issues</h1>
      </div>
      <div style={styles.scrollableContent}>
        {/* Issues Section */}
        <div style={styles.sectionWrapper}>
          <h3 style={styles.sectionTitle}>Issues</h3>
          <div style={styles.card}>
            <p style={styles.cardText}>{analysisResult.issues}</p>
          </div>
        </div>
        {/* Summary Section */}
        <div style={styles.sectionWrapper}>
          <h3 style={styles.sectionTitle}>Summary</h3>
          <div style={styles.card}>
            <p style={styles.cardText}>{analysisResult.summary}</p>
          </div>
        </div>
        {/* Sentiment Section */}
        <div style={styles.sectionWrapper}>
          <h3 style={styles.sectionTitle}>Sentiment</h3>
          <div style={styles.card}>
            <p style={styles.cardText}>{analysisResult.sentiment}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    height: "100vh",
    backgroundColor: "#1c1c1c",
    color: "white",
    padding: "20px",
    overflow: "hidden",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-start", // Align content horizontally to the left
    width: "90%",
    maxWidth: "400px",
    marginBottom: "20px",
  },
  backArrow: {
    width: "16px",
    height: "16px",
    borderLeft: "2px solid white",
    borderBottom: "2px solid white",
    transform: "rotate(45deg)",
    cursor: "pointer",
    marginRight: "10px", // Space between arrow and title
  },
  title: {
    fontSize: "1.5rem",
    color: "white",
    margin: 0,
  },
  scrollableContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    overflowY: "auto",
    width: "100%",
    maxWidth: "400px",
    maxHeight: "calc(100vh - 100px)",
    padding: "10px",
    scrollbarWidth: "none",
  },
  sectionWrapper: {
    width: "100%",
    marginBottom: "20px",
  },
  sectionTitle: {
    marginBottom: "10px",
    fontSize: "1.2rem",
    fontWeight: "bold",
    color: "white",
    textAlign: "left",
  },
  card: {
    backgroundColor: "rgba(27, 79, 113, 0.49)",
    padding: "20px",
    borderRadius: "30px",
    boxShadow: "0 8px 20px rgba(0, 0, 0, 0.3)",
    color: "white",
    textAlign: "left",
  },
  cardText: {
    fontSize: "1rem",
    lineHeight: "1.5",
  },
  noAnalysisText: {
    fontSize: "1.2rem",
    marginBottom: "20px",
    textAlign: "center",
  },
};

export default ResultPage;
