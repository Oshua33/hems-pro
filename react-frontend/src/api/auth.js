import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL;

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
