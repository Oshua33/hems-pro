import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export const loginUser = async (username, password) => {
  const res = await axios.post(`${BASE_URL}/users/token`, {
    username,
    password,
  }, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  return res.data.access_token;
};

export const registerUser = async (data) => {
  const res = await axios.post(`${BASE_URL}/users/register/`, data);
  return res.data;
};
