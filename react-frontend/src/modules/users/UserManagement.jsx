import React, { useEffect, useState } from "react";
import "./UserManagement.css";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000";

const UserManagement = ({ token }) => {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [popupMsg, setPopupMsg] = useState("");
  const [editingUser, setEditingUser] = useState(null);
  const [editRole, setEditRole] = useState("");
  const [editPassword, setEditPassword] = useState("");
  const [selectedAction, setSelectedAction] = useState("list");
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("user");
  const [adminPassword, setAdminPassword] = useState(""); // 🆕 Admin Password field

  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setError("You must be logged in");
      return;
    }
    fetchUsers();
  }, [token]);

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/users/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to fetch users");
      setUsers(data);
    } catch (err) {
      setError(err.message || "Network error");
    }
  };

  const showPopup = (msg) => {
    setPopupMsg(msg);
    setTimeout(() => setPopupMsg(""), 3000);
  };

  const handleEditClick = (user) => {
    setEditingUser(user);
    setEditRole(user.role);
    setEditPassword("");
    setSelectedAction("update");
    setError("");
  };

  const cancelEdit = () => {
    setEditingUser(null);
    setEditPassword("");
    setEditRole("");
    setSelectedAction("list");
  };

  const submitUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/users/${editingUser.username}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: editingUser.username,
          password: editPassword || undefined,
          role: editRole,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Update failed");
      }
      showPopup(`User ${editingUser.username} updated`);
      cancelEdit();
      fetchUsers();
    } catch (err) {
      showPopup(err.message || "Update failed");
    }
  };

  const deleteUser = async (username) => {
  console.log("Delete function called for:", username);  // <-- add this
  if (!window.confirm(`Are you sure you want to delete user "${username}"?`)) return;

  try {
    const res = await fetch(`${API_BASE_URL}/users/${username}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Delete failed");
    }

    showPopup(data.message || `User ${username} deleted successfully`);
    fetchUsers();  // Refresh list
  } catch (err) {
    console.error("Delete Error:", err);
    showPopup(err.message || "Delete failed");
  }
};



  const submitAddUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/users/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: newUsername,
          password: newPassword,
          role: newRole,
          admin_password: adminPassword, // 🆕 Send admin password
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to create user");
      }
      showPopup(`User "${newUsername}" created`);
      setNewUsername("");
      setNewPassword("");
      setNewRole("user");
      setAdminPassword(""); // 🆕 Reset admin password
      setSelectedAction("list");
      fetchUsers();
    } catch (err) {
      showPopup(err.message || "Create failed");
    }
  };

  return (
    <div className="user-container small-frame">
      <div className="user-header">
        <h2 className="user-heading">User Management</h2>
        <div className="header-right">
          <select
            value={selectedAction}
            onChange={(e) => {
              setSelectedAction(e.target.value);
              setEditingUser(null);
            }}
          >
            <option value="list">List Users</option>
            <option value="add">Add User</option>
            <option value="update" disabled={!editingUser}>
              Edit User
            </option>
          </select>
          <button className="close-main-button" onClick={() => navigate("/dashboard")}>
            ❌
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {popupMsg && <div className="popup-inside">{popupMsg}</div>}

      {/* User List */}
      {selectedAction === "list" && (
        <div className="user-table compact">
          <div className="table-header">
            <div>ID</div>
            <div>Username</div>
            <div>Role</div>
            <div>Action</div>
          </div>
          {users.map((user) => (
            <div className="table-row" key={user.id}>
              <div>{user.id}</div>
              <div>{user.username}</div>
              <div>{user.role}</div>
              <div className="action-buttons">
                <button className="btn edit" onClick={() => handleEditClick(user)}>
                  Edit
                </button>
                <button
                  className="btn delete"
                  onClick={() => deleteUser(user.username)}
                  disabled={
                    // Disable only if trying to delete self
                    user.username === localStorage.getItem("username")
                  }
                >
                  Delete
                </button>


              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add User Form */}
      {selectedAction === "add" && (
        <form onSubmit={submitAddUser} className="edit-form compact-form">
          <div className="edit-header">
            <h4>Add New User</h4>
            <button type="button" className="close-button" onClick={() => setSelectedAction("list")}>
              ❌
            </button>
          </div>

          <label>
            Username:
            <input
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              required
            />
          </label>
          <label>
            Password:
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </label>
          <label>
            Role:
            <select value={newRole} onChange={(e) => setNewRole(e.target.value)} required>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <label>
            Admin Password:
            <input
              type="password"
              value={adminPassword}
              onChange={(e) => setAdminPassword(e.target.value)}
              required
            />
          </label>
          <div className="form-buttons">
            <button type="submit">Create</button>
            <button type="button" onClick={() => setSelectedAction("list")}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Edit User Form */}
      {selectedAction === "update" && editingUser && (
        <form onSubmit={submitUpdate} className="edit-form compact-form">
          <div className="edit-header">
            <h4>Edit: {editingUser.username}</h4>
            <button type="button" className="close-button" onClick={cancelEdit}>
              ❌
            </button>
          </div>

          <label>
            Role:
            <select value={editRole} onChange={(e) => setEditRole(e.target.value)} required>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <label>
            New Password:
            <input
              type="password"
              value={editPassword}
              onChange={(e) => setEditPassword(e.target.value)}
            />
          </label>
          <div className="form-buttons">
            <button type="submit">Save</button>
            <button type="button" onClick={cancelEdit}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default UserManagement;
