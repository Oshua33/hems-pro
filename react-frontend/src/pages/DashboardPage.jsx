import React, { useState } from "react";
import { useNavigate, Outlet, useLocation } from "react-router-dom";
import "./DashboardPage.css";
import { FaHotel } from "react-icons/fa"; // Add at the top

const DashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const userRole = "admin";

  const [isBookingsHovered, setBookingsHovered] = useState(false);

  const menu = [
    { name: "🙎 Users", path: "/dashboard/users", adminOnly: true },
    { name: "🏨 Rooms", path: "/dashboard/rooms" },
    { name: "📅 Bookings", path: "/dashboard/bookings" },
    { name: "💳 Payments", path: "/dashboard/payments" },
    { name: "🎉 Events", path: "/dashboard/events" },
  ];

  const bookingSubmenu = [
    { label: "➕ Create Booking", path: "/dashboard/bookings/create" },
    { label: "📋 List Booking", path: "/dashboard/bookings/list" },
    { label: "🔖 Sort by Status", path: "/dashboard/bookings/sort-status" },
    { label: "🙍 Sort Guest by Name", path: "/dashboard/bookings/sort-name" },
    { label: "🚪 Sort Guest by Room", path: "/dashboard/bookings/sort-room" },
    { label: "✅ Checkout Guest", path: "/dashboard/bookings/checkout" },
    { label: "❌ Cancel Booking", path: "/dashboard/bookings/cancel" },
  ];

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2 className="sidebar-title">MENU</h2>

        <nav>
          {menu.map((item) => {
            const isBookings = item.name.includes("Bookings");
            const isSubRoute =
              location.pathname.startsWith("/dashboard/bookings");

            return (!item.adminOnly || userRole === "admin") ? (
              <div
                key={item.path}
                className="sidebar-item-wrapper"
                onMouseEnter={() => isBookings && setBookingsHovered(true)}
                onMouseLeave={() => isBookings && setBookingsHovered(false)}
                style={{ position: "relative" }}
              >
                <button
                  onClick={() => {
                    if (!isBookings) navigate(item.path);
                  }}
                  className={`sidebar-button ${
                    isBookings && isBookingsHovered

                      ? "sidebar-button-active"
                      : ""
                  }`}
                >
                  <span style={{ fontSize: "1.6rem", marginRight: "8px" }}>
                    {item.name.slice(0, 2)}
                  </span>
                  {item.name.slice(2).trim()}
                </button>

                {/* Bookings Submenu */}
                {isBookings && isBookingsHovered && (
            <div className="submenu">
              {bookingSubmenu.map((sub) => (
                <button
                  key={sub.path}
                  onClick={() => {
                    navigate(sub.path);
                    setBookingsHovered(false); // 👈 immediately close submenu on click
                  }}
                  className="submenu-item"
                >
                  {sub.label}
                </button>
              ))}
            </div>
          )}

              </div>
            ) : null;
          })}

          <button
            onClick={() => navigate("/reservation-alert")}
            className="sidebar-button reservation-button"
          >
            🔔 Reservation Alert
          </button>
        </nav>
      </aside>

      {/* Logout button */}
      <button onClick={() => navigate("/logout")} className="logout-button">
        🚪 Logout
      </button>

      {/* Main content */}
      <main className="main-content">
        <header className="header">
          <h1 className="header-title">🏠 Hotel Management Dashboard</h1>

        </header>
        <section className="content-area">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
