// src/api/authService.js
import axios from "axios";

// ✅ Fallback to window.location.hostname if env variable isn't loaded
const BASE_URL =
  process.env.REACT_APP_API_BASE_URL ||
  `http://${window.location.hostname}:8000`;

console.log("🧪 Login API Base URL:", BASE_URL);

const authClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Login user (uses form data for FastAPI OAuth2PasswordRequestForm)
export const loginUser = async (username, password) => {
  try {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await authClient.post("/users/token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return response.data; // { access_token, token_type }
  } catch (error) {
    console.error("❌ Login failed:", error);
    throw error.response?.data || { message: "Login failed" };
  }
};

// ✅ Register user (admin password required)
export const registerUser = async ({
  username,
  password,
  role,
  admin_password,
}) => {
  try {
    const response = await authClient.post("/users/register/", {
      username,
      password,
      role,
      admin_password,
    });

    return response.data; // optional response
  } catch (error) {
    console.error("❌ Registration failed:", error);
    throw error.response?.data || { message: "Registration failed" };
  }
};
