import axios from "axios";

// Create an instance of axios with a base URL
const instance = axios.create({
  baseURL: "http://127.0.0.1:5000", // Change this if backend URL changes
});

export default instance;
