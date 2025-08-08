// src/api/licenseApi.js

import axios from "axios";

// ✅ Use environment variable from .env
const BASE_URL = process.env.REACT_APP_API_BASE_URL;

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const verifyLicense = async (licenseKey) => {
  try {
    const response = await apiClient.get(
      `/license/verify/${encodeURIComponent(licenseKey)}`
    );
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: "API request failed" };
  }
};

export const generateLicense = async (adminPassword, licenseKey) => {
  if (!adminPassword || !licenseKey) {
    throw new Error("Admin password and license key are required.");
  }

  try {
    const response = await apiClient.post(
      `/license/generate?license_password=${encodeURIComponent(adminPassword)}&key=${encodeURIComponent(licenseKey)}`
    );
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: "API request failed" };
  }
};

// ✅ NEW: Check current license status (used in HomePage)
export const checkLicenseStatus = async () => {
  try {
    const response = await apiClient.get(`/license/check`);
    return response.data; // Expected { valid: true/false, expires_on: "..." }
  } catch (error) {
    throw error.response?.data || { message: "License check failed" };
  }
};
