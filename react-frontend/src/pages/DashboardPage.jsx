import React, { useState, useEffect } from "react";
import { useNavigate, Outlet, useLocation } from "react-router-dom";
import axios from "axios";
import "./DashboardPage.css";
import { FaHotel } from "react-icons/fa";

const DashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const userRole = "admin";

  const [hasReservationAlert, setHasReservationAlert] = useState(false);
  const [isBookingsHovered, setBookingsHovered] = useState(false);
  const [isPaymentsHovered, setPaymentsHovered] = useState(false);


  const [reservationCount, setReservationCount] = useState(0);

    useEffect(() => {
      const checkReservationAlerts = async () => {
        const token = localStorage.getItem("token");
        if (!token) return;

        try {
          const res = await axios.get("http://localhost:8000/bookings/reservations/alerts", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          const count = res.data.count || 0;
          setReservationCount(count);
        } catch (err) {
          console.error("Failed to check reservation alert status:", err.message);
        }
      };

      checkReservationAlerts();
      const interval = setInterval(checkReservationAlerts, 5000); // every 30s
      return () => clearInterval(interval);
    }, []);

  const menu = [
    { name: "🙎 Users", path: "/dashboard/users", adminOnly: true },
    { name: "🏨 Rooms", path: "/dashboard/rooms" },
    { name: "📅 Bookings", path: "/dashboard/bookings" },
    { name: "💳 Payments", path: "/dashboard/payments" },
    { name: "🎉 Events", path: "/dashboard/events" },
  ];

  const bookingSubmenu = [
    { label: "➕ Create Booking", path: "/dashboard/bookings/create" },
    { label: "📝 List Booking", path: "/dashboard/bookings/list" },
    { label: "✅ Checkout Guest", path: "/dashboard/bookings/checkout" },
    { label: "❌ Cancel Booking", path: "/dashboard/bookings/cancel" },
  ];

  const paymentSubmenu = [
    { label: "➕ Create Payment", path: "/dashboard/payments/create" },
    { label: "📝 List Payment", path: "/dashboard/payments/list" },
    { label: "❌ Void payment", path: "/dashboard/payments/void" },
  ];

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2 className="sidebar-title">MENU</h2>

        <nav>
          {menu.map((item) => {
            const isBookings = item.name.includes("Bookings");
            const isPayments = item.name.includes("Payments");

            return (!item.adminOnly || userRole === "admin") ? (
              <div
                key={item.path}
                className="sidebar-item-wrapper"
                onMouseEnter={() => {
                  if (isBookings) setBookingsHovered(true);
                  if (isPayments) setPaymentsHovered(true);
                }}
                onMouseLeave={() => {
                  if (isBookings) setBookingsHovered(false);
                  if (isPayments) setPaymentsHovered(false);
                }}
                style={{ position: "relative" }}
              >
                <button
                  onClick={() => {
                    if (!isBookings && !isPayments) navigate(item.path);
                  }}
                  className={`sidebar-button ${
                    (isBookings && isBookingsHovered) ||
                    (isPayments && isPaymentsHovered)
                      ? "sidebar-button-active"
                      : ""
                  }`}
                >
                  <span style={{ fontSize: "1.6rem", marginRight: "8px" }}>
                    {item.name.slice(0, 2)}
                  </span>
                  {item.name.slice(2).trim()}
                </button>

                {isBookings && isBookingsHovered && (
                  <div className="submenu">
                    {bookingSubmenu.map((sub) => (
                      <button
                        key={sub.path}
                        onClick={() => {
                          navigate(sub.path);
                          setBookingsHovered(false);
                        }}
                        className="submenu-item"
                      >
                        {sub.label}
                      </button>
                    ))}
                  </div>
                )}

                {isPayments && isPaymentsHovered && (
                  <div className="submenu">
                    {paymentSubmenu.map((sub) => (
                      <button
                        key={sub.path}
                        onClick={() => {
                          navigate(sub.path);
                          setPaymentsHovered(false);
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
            onClick={() => navigate("/dashboard/reservation-alert")}
            className={`sidebar-button reservation-button ${
              reservationCount > 0 ? "alert-active" : "alert-inactive"
            }`}
          >
            🔔 Reservation Alert{reservationCount > 0 ? ` (${reservationCount})` : ""}
          </button>


        </nav>
      </aside>

      <button onClick={() => navigate("/logout")} className="logout-button">
        🚪 Logout
      </button>

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
