import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",  // no "/api"
  headers: {
    "Content-Type": "application/json",
  },
});

export const verifyLicense = async (licenseKey) => {
  try {
    const response = await apiClient.get(`/license/verify/${encodeURIComponent(licenseKey)}`);
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



