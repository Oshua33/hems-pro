// modules/auth/authService.js

const API_BASE_URL = "http://127.0.0.1:8000";

export const loginUser = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/users/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Login failed");
  }

  return response.json(); // { access_token: ..., token_type: ... }
};

export const registerUser = async ({ username, password, role, admin_password }) => {
  const response = await fetch(`${API_BASE_URL}/users/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role, admin_password }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Registration failed");
  }

  return response.json(); // optional response
};
