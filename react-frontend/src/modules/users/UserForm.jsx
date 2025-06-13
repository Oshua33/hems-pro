// src/modules/users/UserForm.jsx
import React, { useState, useEffect } from 'react';

const UserForm = ({ initialData = {}, onSubmit, onClose, mode }) => {
  const [username, setUsername] = useState(initialData.username || '');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState(initialData.role || 'user');
  const [adminPassword, setAdminPassword] = useState('');

  const handleSubmit = () => {
    if (!username || !password) {
      alert('Username and password are required.');
      return;
    }
    const data = { username, password, role };
    if (role === 'admin') {
      data.admin_password = adminPassword;
    }
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">{mode === 'edit' ? 'Update User' : 'Add User'}</h2>

        <input
          type="text"
          placeholder="Username"
          className="w-full border rounded px-3 py-2 mb-3"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border rounded px-3 py-2 mb-3"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <select
          className="w-full border rounded px-3 py-2 mb-3"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>

        {role === 'admin' && (
          <input
            type="password"
            placeholder="Admin Password"
            className="w-full border rounded px-3 py-2 mb-3"
            value={adminPassword}
            onChange={(e) => setAdminPassword(e.target.value)}
          />
        )}

        <div className="flex justify-end gap-3">
          <button
            className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserForm;
