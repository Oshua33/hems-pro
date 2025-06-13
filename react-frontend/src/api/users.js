// src/api/users.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const getUsers = (token) =>
  axios.get(`${API_BASE_URL}/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const addUser = (data, token) =>
  axios.post(`${API_BASE_URL}/users/register/`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const updateUser = (username, data, token) =>
  axios.put(`${API_BASE_URL}/users/${username}`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const deleteUser = (username, token) =>
  axios.delete(`${API_BASE_URL}/users/${username}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
