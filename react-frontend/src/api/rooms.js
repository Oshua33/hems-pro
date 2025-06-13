import axios from "./axiosInstance";

export const fetchRoomDetails = (roomNumber, token) =>
  axios.get(`/rooms/${roomNumber}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const updateRoom = (roomNumber, data, token) =>
  axios.put(`/rooms/${roomNumber}`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const deleteRoom = (roomNumber, token) =>
  axios.delete(`/rooms/${roomNumber}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const fetchAllRooms = (token) =>
  axios.get(`/rooms`, {
    headers: { Authorization: `Bearer ${token}` },
  });
