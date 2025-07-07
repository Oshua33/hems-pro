import axios from "axios";

// 🔁 This uses the current browser IP address and port
const API_BASE_URL = `http://${window.location.hostname}:8000`;

const API = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});


export default API;
