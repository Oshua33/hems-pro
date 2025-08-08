import React, { useState, useEffect } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./ListIssues.css";

const ListIssues = () => {
  const [issues, setIssues] = useState([]);
  const [bars, setBars] = useState([]);
  const [items, setItems] = useState([]);
  const [message, setMessage] = useState("");
  const [barName, setBarName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [editingIssue, setEditingIssue] = useState(null);
  const [formData, setFormData] = useState({
    issue_to: "bar",
    issued_to_id: "",
    issue_date: "",
    issue_items: [],
  });

  // Helper to show messages for 3 seconds
  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(""), 3000);
  };

  // Fetch bars
  useEffect(() => {
    (async () => {
      try {
        const res = await axiosWithAuth().get("/bar/bars/simple");
        setBars(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error("❌ Error fetching bars", err);
      }
    })();
  }, []);

  // Fetch items for dropdown
  useEffect(() => {
    (async () => {
      try {
        const res = await axiosWithAuth().get("/store/items/simple");
        setItems(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error("❌ Error fetching items", err);
      }
    })();
  }, []);

  const fetchIssues = async () => {
    if (!startDate || !endDate) {
      showMessage("⚠️ Please select a start and end date.");
      return;
    }
    try {
      const params = {};
      if (barName) params.bar_name = barName;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const res = await axiosWithAuth().get("/store/issues", { params });
      setIssues(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("❌ Error fetching issues", err);
    }
  };

  const handleEditClick = (issue) => {
    setEditingIssue(issue.id);
    setFormData({
      issue_to: "bar",
      issued_to_id: issue.issued_to_id || "",
      issue_date: issue.issue_date ? issue.issue_date.split("T")[0] : "",
      issue_items: issue.issue_items.map((item) => ({
        item_id: item.item?.id || "",
        quantity: item.quantity || 0,
      })),
    });
  };

  const handleFormChange = (index, field, value) => {
    const newItems = [...formData.issue_items];
    newItems[index][field] = value;
    setFormData({ ...formData, issue_items: newItems });
  };

  const handleSubmitEdit = async (id) => {
    try {
      const payload = {
        ...formData,
        issued_to_id: parseInt(formData.issued_to_id, 10),
        issue_items: formData.issue_items.map((item) => ({
          item_id: parseInt(item.item_id, 10),
          quantity: parseInt(item.quantity, 10),
        })),
      };

      await axiosWithAuth().put(`/store/issues/${id}`, payload);
      showMessage("✅ Issue updated successfully.");
      setEditingIssue(null);
      fetchIssues();
    } catch (err) {
      console.error("❌ Update failed", err.response?.data || err.message);
      showMessage("❌ Failed to update issue.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this issue?")) return;
    try {
      await axiosWithAuth().delete(`/store/issues/${id}`);
      showMessage("✅ Issue deleted successfully.");
      fetchIssues();
    } catch (err) {
      console.error("❌ Delete failed", err);
      showMessage("❌ Failed to delete issue.");
    }
  };

  // Summary stats
  const totalIssued = issues.length;
  const totalQuantity = issues.reduce(
    (acc, issue) =>
      acc +
      (issue.issue_items?.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0),
    0
  );

  return (
    <div className="list-issues-container">
      <h2>📦 List of Issued Items</h2>

      <div className="filters">
        <select value={barName} onChange={(e) => setBarName(e.target.value)}>
          <option value="">-- Filter by Bar --</option>
          {bars.map((bar) => (
            <option key={bar.id} value={bar.name}>
              {bar.name}
            </option>
          ))}
        </select>

        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        <button onClick={fetchIssues}>🔍 Filter</button>
        <button
          onClick={() => {
            setBarName("");
            setStartDate("");
            setEndDate("");
            setIssues([]);
          }}
        >
          ♻️ Reset
        </button>
      </div>

      {message && <p className="issue-message">{message}</p>}

      <div className="summary">
        <p>Total Entries: {totalIssued}</p>
        <p>Total Quantity Issued: {totalQuantity}</p>
      </div>

      <table className="list-issues-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Issue To</th>
            <th>Issue Date</th>
            <th>Items Issued</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {issues.length === 0 ? (
            <tr>
              <td colSpan="5">No issues found.</td>
            </tr>
          ) : (
            issues.map((issue) => (
              <tr key={issue.id}>
                <td>{issue.id}</td>
                <td>{issue.issued_to?.name || "Unnamed Bar"}</td>
                <td>{new Date(issue.issue_date).toLocaleDateString()}</td>
                <td>
                  <ul style={{ paddingLeft: "1rem", margin: 0 }}>
                    {issue.issue_items.map((item) => (
                      <li key={item.id}>
                        {item.item?.name || "Unnamed Item"} — Qty: {item.quantity}
                      </li>
                    ))}
                  </ul>
                </td>
                <td>
                  <button onClick={() => handleEditClick(issue)}>✏️ Edit</button>
                  <button onClick={() => handleDelete(issue.id)}>🗑️ Delete</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {editingIssue && (
        <div className="edit-modal-overlay">
          <div className="edit-form">
            <h3>Edit Issue</h3>

            <label>Bar:</label>
            <select
              value={formData.issued_to_id}
              onChange={(e) =>
                setFormData({ ...formData, issued_to_id: e.target.value })
              }
            >
              <option value="">-- Select a bar --</option>
              {bars.map((bar) => (
                <option key={bar.id} value={bar.id}>
                  {bar.name}
                </option>
              ))}
            </select>

            <label>Issue Date:</label>
            <input
              type="date"
              value={formData.issue_date}
              onChange={(e) =>
                setFormData({ ...formData, issue_date: e.target.value })
              }
            />

            <h4>Items</h4>
            {formData.issue_items.map((item, index) => (
              <div key={index} className="item-row">
                <select
                  value={item.item_id}
                  onChange={(e) =>
                    handleFormChange(index, "item_id", e.target.value)
                  }
                >
                  <option value="">-- Select an item --</option>
                  {items.map((it) => (
                    <option key={it.id} value={it.id}>
                      {it.name}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) =>
                    handleFormChange(index, "quantity", e.target.value)
                  }
                  placeholder="Qty"
                />
              </div>
            ))}

            <button onClick={() => handleSubmitEdit(editingIssue)}>✅ Save</button>
            <button onClick={() => setEditingIssue(null)}>❌ Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListIssues;
