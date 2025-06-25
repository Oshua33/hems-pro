import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ReservationAlert.css";

const ReservationAlert = () => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReservations = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setError("No authentication token found.");
        setLoading(false);
        return;
      }

      try {
        const res = await axios.get("http://localhost:8000/bookings/reservation-alerts", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // ✅ Backend returns a list directly
        if (Array.isArray(res.data)) {
          setReservations(res.data);
        } else {
          setReservations([]);
        }

        setError(null); // clear any previous error
      } catch (err) {
        console.error("Failed to fetch reservation alert status:", err);
        const message =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          "An unknown error occurred";
        setError(`Failed to fetch reservation alert status: ${message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchReservations();

    // Optional: Auto-refresh every 30s
   
  }, []);

  return (
    <div className="reservation-alert-container">
      <h2>🔔 Active Reservations</h2>

      {loading ? (
        <p>Loading reservations...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : reservations.length === 0 ? (
        <p>No active reservations at the moment.</p>
      ) : (
        <table className="reservation-table">
          <thead>
            <tr>
              <th>BookID</th>
              <th>Room</th>
              <th>Guest Name</th>
              <th>Address</th>
              <th>Phone</th>
              <th>Arrival Date</th>
              <th>Departure Date</th>
              <th>Booking Type</th>
              <th>Status</th>
              <th>Payment</th>
              <th>Days</th>
              <th>Cost</th>
              <th>Created By</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((res) => (
              <tr key={res.id}>
                <td>{res.id}</td>
                <td>{res.room_number}</td>
                <td>{res.guest_name}</td>
                <td>{res.address}</td>
                <td>{res.phone_number}</td>
                <td>{res.arrival_date}</td>
                <td>{res.departure_date}</td>
                <td>{res.booking_type}</td>
                <td>{res.status}</td>
                <td>{res.payment_status}</td>
                <td>{res.number_of_days}</td>
                <td>{res.booking_cost}</td>
                <td>{res.created_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ReservationAlert;
