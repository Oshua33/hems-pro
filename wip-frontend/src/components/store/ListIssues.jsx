import React, { useState, useEffect } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./ListIssues.css";
import { useNavigate } from "react-router-dom";

const ListIssues = () => {
  const [issues, setIssues] = useState([]);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchIssues();
  }, []);

  const fetchIssues = async () => {
    try {
      const res = await axiosWithAuth().get("/store/issues");
      setIssues(res.data);
    } catch (err) {
      console.error("❌ Error fetching issues", err);
    }
  };

  const handleEdit = (id) => {
    navigate(`/store/update-issue/${id}`);
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this issue?")) {
      try {
        await axiosWithAuth().delete(`/store/issues/${id}`);
        setMessage("✅ Issue deleted successfully.");
        fetchIssues();
      } catch (err) {
        console.error("❌ Delete failed", err);
        setMessage("❌ Failed to delete issue.");
      }
    }
  };

  return (
    <div className="list-issues-container">
      <h2>📦 List of Issued Items</h2>

      {message && <p className="issue-message">{message}</p>}

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
                  <button className="edit-btn" onClick={() => handleEdit(issue.id)}>✏️ Edit</button>
                  <button className="delete-btn" onClick={() => handleDelete(issue.id)}>🗑️ Delete</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ListIssues;
