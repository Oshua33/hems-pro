// CreateCategory.jsx
import React, { useState } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./CreateCategory.css";

const CreateCategory = ({ onClose }) => {
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const axios = axiosWithAuth();
      await axios.post("/store/categories", { name });

      setMessage("✅ Category created successfully!");
      setName("");
    } catch (error) {
      setMessage(error.response?.data?.detail || "❌ Error creating category.");
    }
  };

  return (
    <div className="create-category-container">
      <div className="form-header">
        <h2>Create Category</h2>
        <button className="close-button" onClick={onClose}>✖</button>
      </div>

      <form className="category-form" onSubmit={handleSubmit}>
        <label htmlFor="categoryName">Category Name</label>
        <input
          id="categoryName"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Soft Drinks, Wines, Whisky & Spirit"
          required
        />
        <button type="submit">➕ Create Category</button>
      </form>

      {message && <p className="category-message">{message}</p>}
    </div>
  );
};

export default CreateCategory;
