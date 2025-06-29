import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const checkLicenseStatus = () => {
      const verified = localStorage.getItem("license_verified");
      const validUntil = localStorage.getItem("license_valid_until");

      const now = new Date();
      const expiryDate = validUntil ? new Date(validUntil) : null;

      const isStillValid = verified === "true" && expiryDate && expiryDate > now;

      // Wait 2 seconds then redirect
      setTimeout(() => {
        if (isStillValid) {
          navigate("/login");
        } else {
          navigate("/license");
        }
      }, 3000); // 2-second delay
    };

    checkLicenseStatus();
  }, [navigate]);

  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=Audiowide&display=swap"
        rel="stylesheet"
      />

      <div className="home-container">
        <div className="home-card">
          <div className="hems-text">
            <span className="hems-letter">H</span>
            <span className="hems-letter">E</span>
            <span className="hems-letter">M</span>
            <span className="hems-letter">S</span>
          </div>

          <div className="spinner-container">
            <div className="spinner-ring ring-1" />
            <div className="spinner-ring ring-2" />
            <div className="spinner-ring ring-3" />
          </div>

          <h1 className="heading-line1">Welcome to</h1>
          <h2 className="heading-line2">Hotel & Event Management System</h2>
        </div>

        <footer className="home-footer">
          <div>Produced & Licensed by School of Accounting Package</div>
          <div>© 2025</div>
        </footer>
      </div>
    </>
  );
};

export default HomePage;
