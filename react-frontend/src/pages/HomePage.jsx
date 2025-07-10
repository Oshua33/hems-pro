import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { checkLicenseStatus } from "../api/licenseApi"; // Make sure this exists
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const verifyLicense = async () => {
      try {
        const data = await checkLicenseStatus(); // Expects { valid: true, expires_on: "..." }

        const now = new Date();
        const expiresOn = data.expires_on ? new Date(data.expires_on) : null;

        if (data.valid && expiresOn && expiresOn > now) {
          localStorage.setItem("license_verified", "true");
          localStorage.setItem("license_valid_until", expiresOn.toISOString());
          navigate("/login");
        } else {
          localStorage.removeItem("license_verified");
          localStorage.removeItem("license_valid_until");
          navigate("/license");
        }
      } catch (error) {
        console.error("License check failed", error);
        navigate("/license");
      }
    };

    setTimeout(() => {
      verifyLicense();
    }, 3000); // Keep your animation delay if you like
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
