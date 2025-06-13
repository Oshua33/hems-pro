import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css"; // Import the external CSS

const HomePage = () => {
  const navigate = useNavigate();
  const [hover, setHover] = React.useState(false);

  const handleGoToLicense = () => {
    navigate("/license");
  };

  return (
    <>
      {/* Google Font */}
      <link
        href="https://fonts.googleapis.com/css2?family=Audiowide&display=swap"
        rel="stylesheet"
      />

      <div className="home-container">
        <div className="home-card">
          {/* Stylish animated HEMS text */}
          <div className="hems-text">
            <span className="hems-letter">H</span>
            <span className="hems-letter">E</span>
            <span className="hems-letter">M</span>
            <span className="hems-letter">S</span>
          </div>

          {/* Spinner with multiple rings */}
          <div className="spinner-container">
            <div className="spinner-ring ring-1" />
            <div className="spinner-ring ring-2" />
            <div className="spinner-ring ring-3" />
          </div>

          <h1 className="heading-line1">Welcome to</h1>
          <h2 className="heading-line2">Hotel & Event Management System</h2>

          <button
            className={`home-button ${hover ? "hover" : ""}`}
            onClick={handleGoToLicense}
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
          >
            Go to License Management
          </button>
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
