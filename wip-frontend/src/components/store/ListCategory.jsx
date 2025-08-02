import React, { useEffect, useState } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./ListCategory.css";

const ListCategory = ({ onClose }) => {
  const [categories, setCategories] = useState([]);
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const res = await axiosWithAuth().get("/store/categories");
      setCategories(res.data);
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this category?")) return;
    try {
      const axios = axiosWithAuth();
      await axios.delete(`/store/categories/${id}`);
      setCategories(categories.filter((cat) => cat.id !== id));
    } catch (err) {
      alert("Failed to delete category.");
      console.error(err);
    }
  };

  const handleUpdate = async (id) => {
    try {
      const axios = axiosWithAuth();
      await axios.put(`/store/categories/${id}`, { name: editName });
      setCategories(categories.map((cat) => (cat.id === id ? { ...cat, name: editName } : cat)));
      setEditId(null);
      setEditName("");
    } catch (err) {
      alert("Failed to update category.");
      console.error(err);
    }
  };

  return (
    <div className="category-list-container">
      <div className="form-header">
        <h2>📃 List of Categories</h2>
        {onClose && (
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        )}
      </div>

      <table className="category-table">
        <thead>
          <tr>
            <th>Id</th>
            <th>Category Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((cat, index) => (
            <tr key={cat.id} className={index % 2 === 0 ? "even-row" : "odd-row"}>
              <td>{index + 1}</td>
              <td>
                {editId === cat.id ? (
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                  />
                ) : (
                  cat.name
                )}
              </td>
              <td>
                {editId === cat.id ? (
                  <>
                    <button className="action-btn save" onClick={() => handleUpdate(cat.id)}>
                      💾 Save
                    </button>
                    <button className="action-btn cancel" onClick={() => setEditId(null)}>
                      ❌ Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      className="action-btn update"
                      onClick={() => {
                        setEditId(cat.id);
                        setEditName(cat.name);
                      }}
                    >
                      ✏️ Update
                    </button>
                    <button className="action-btn delete" onClick={() => handleDelete(cat.id)}>
                      🗑️ Delete
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {message && <p className="vendor-message">{message}</p>}
    </div>
  );
};

export default ListCategory;
