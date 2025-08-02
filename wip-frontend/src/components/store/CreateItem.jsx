// src/components/store/CreateItem.jsx
import React, { useState, useEffect } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./CreateItem.css";

const CreateItem = ({ onClose }) => {
  const [name, setName] = useState("");
  const [unit, setUnit] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [categories, setCategories] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const axios = axiosWithAuth();
        const response = await axios.get("/store/categories");
        setCategories(response.data);
      } catch (error) {
        console.error("Error fetching categories:", error);
        setMessage("❌ Failed to load categories.");
      }
    };

    fetchCategories();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const axios = axiosWithAuth();
      await axios.post("/store/items", {
        name,
        unit,
        category_id: parseInt(categoryId),
      });

      setMessage("✅ Item created successfully!");
      setName("");
      setUnit("");
      setCategoryId("");
    } catch (error) {
      console.error("Error creating item:", error);
      setMessage(error.response?.data?.detail || "❌ Error creating item.");
    }
  };

  return (
    <div className="create-item-container">
      <div className="form-header">
        <h2>Create Store Item</h2>
        <button className="close-button" onClick={onClose}>✖</button>
      </div>

      <form className="item-form" onSubmit={handleSubmit}>
        <label>Item Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Coke, Four Cousin, Whisky"
          required
        />

        <label>Unit</label>
        <input
          type="text"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          placeholder="e.g. Cartons, Packs, Pieces"
          required
        />

        <label>Category</label>
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} required>
          <option value="">Select Category</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        <button type="submit">➕ Create Item</button>
      </form>

      {message && <p className="item-message">{message}</p>}
    </div>
  );
};

export default CreateItem;
