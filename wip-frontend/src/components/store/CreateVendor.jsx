import React, { useState } from "react";
import "./CreateVendor.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${window.location.hostname}:8000`;

const CreateVendor = ({ onClose }) => {
  const [formData, setFormData] = useState({
    business_name: "",
    address: "",
    phone_number: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${API_BASE_URL}/vendor/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`✅ Vendor "${data.business_name}" created successfully.`);
        setFormData({ business_name: "", address: "", phone_number: "" });

        setTimeout(() => setMessage(""), 3000);
      } else {
        const errorData = await response.json();
        if (
          response.status === 400 &&
          typeof errorData.detail === "string" &&
          errorData.detail.includes("Vendor name already exists")
        ) {
          setMessage("❌ Vendor name already exists.");
        } else {
          setMessage("❌ Failed to create vendor.");
        }
        setTimeout(() => setMessage(""), 3000);
      }
    } catch (error) {
      console.error(error);
      setMessage("❌ An error occurred while creating vendor.");
      setTimeout(() => setMessage(""), 3000);
    }
  };

  return (
    <div className="create-vendor-container">
      <div className="form-header">
        <h2>Create New Vendor</h2>
        <button className="close-button" onClick={onClose}>✖</button>
      </div>

      <form onSubmit={handleSubmit} className="vendor-form">
        <label>Business Name</label>
        <input
          type="text"
          name="business_name"
          value={formData.business_name}
          onChange={handleChange}
          required
        />

        <label>Address</label>
        <input
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
          required
        />

        <label>Phone Number</label>
        <input
          type="text"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          required
        />

        <button type="submit">Save Vendor</button>
      </form>

      {message && <p className="vendor-message">{message}</p>}
    </div>
  );
};

export default CreateVendor;
