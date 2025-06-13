import React from "react";
import { useNavigate, Outlet } from "react-router-dom";
import "./DashboardPage.css";

const DashboardPage = () => {
  const navigate = useNavigate();
  const userRole = "admin"; // Replace with actual role logic

  const menu = [
    { name: "🙎 Users", path: "/dashboard/users", adminOnly: true },
    { name: "🏨 Rooms", path: "/dashboard/rooms" },
    { name: "📅 Bookings", path: "/dashboard/bookings" },
    { name: "💳 Payments", path: "/dashboard/payments" },
    { name: "🎉 Events", path: "/dashboard/events" },
  ];

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2 className="sidebar-title">MENU</h2>

        <nav>
          {menu.map(
            (item) =>
              (!item.adminOnly || userRole === "admin") && (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className="sidebar-button"
                >
                  {/* Emoji bigger, text normal */}
                  <span style={{ fontSize: "1.6rem", marginRight: "8px" }}>
                    {item.name.slice(0, 2)}
                  </span>
                  {item.name.slice(2).trim()}
                </button>
              )
          )}

          <button
            onClick={() => navigate("/reservation-alert")}
            className="sidebar-button reservation-button"
          >
            🔔 Reservation Alert
          </button>
        </nav>
      </aside>

      {/* Logout button outside sidebar at top-right */}
      <button onClick={() => navigate("/logout")} className="logout-button">
        🚪 Logout
      </button>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <h1 className="header-title">Hotel Management Dashboard</h1>
        </header>
        <section className="content-area">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
