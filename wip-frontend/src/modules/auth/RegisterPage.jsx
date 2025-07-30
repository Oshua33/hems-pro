import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "./authService";
import { Link } from "react-router-dom";
import "./../../styles/AuthForm.css";



const RegisterPage = () => {
  const [form, setForm] = useState({
    username: "",
    password: "",
    role: "user",
    admin_password: "",
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (form.role === "admin" && !form.admin_password) {
      setError("Admin password is required.");
      return;
    }

    try {
      await registerUser(form);
      alert("Registration successful!");
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
   <div className="auth-page-wrapper"> 
    <div className="auth-container">
      <div className="auth-logo-text">H <span>E</span> M <span>S</span></div> 
      <h2>Register</h2>
      {error && <p className="error-msg">{error}</p>}
      <form onSubmit={handleRegister}>
        <input name="username" placeholder="Username" value={form.username} onChange={handleChange} required />
        <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} required />
        <select name="role" value={form.role} onChange={handleChange}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
        {form.role === "admin" && (
          <input name="admin_password" type="password" placeholder="Admin Password" value={form.admin_password} onChange={handleChange} />
        )}
        <button type="submit">Register</button>
      </form>
      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
 </div>
  );
};

export default RegisterPage;
