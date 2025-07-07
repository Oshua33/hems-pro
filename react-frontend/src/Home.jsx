import React from "react";
import "./Home.css";

function Home() {
  return (
    <div className="home-container">
      <div className="home-card">
        <h1>Welcome to Destone Hotel & Suite</h1>
        <p>Manage your bookings, events, and licenses seamlessly.</p>
        <div className="home-buttons">
          <button className="primary-button">Go to Dashboard</button>
          <button className="secondary-button">Manage License</button>
        </div>
      </div>
    </div>
  );
}


export default Home;
