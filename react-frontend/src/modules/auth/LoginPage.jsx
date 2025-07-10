import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../api/auth";
import "./../../styles/AuthForm.css";
import { Link } from "react-router-dom";
import { getLicenseExpiryWarning } from "../../utils/licenseUtils"; // ✅ NEW

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const warning = getLicenseExpiryWarning(); // ✅ Check for license expiry

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const token = await loginUser(username.trim().toLowerCase(), password);

      localStorage.setItem("token", token);
      localStorage.setItem("username", username);
      navigate("/dashboard/rooms/status");

    } catch (err) {
      setError("Invalid username or password.");
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-container">
        {warning && (
          <div style={{
            backgroundColor: "#fff3cd",
            padding: "12px",
            marginBottom: "15px",
            border: "1px solid #ffeeba",
            borderRadius: "6px",
            color: "#856404",
            textAlign: "center",
            fontWeight: "bold"
          }}>
            {warning}
          </div>
        )}

        <div className="auth-logo-text">
          H <span>E</span> M <span>S</span>
        </div>

        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <div className="error">{error}</div>}
          <button type="submit">Login</button>
          <p>
            Don't have an account? <Link to="/register">Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
