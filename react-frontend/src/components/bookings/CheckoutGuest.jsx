import React, { useEffect, useState } from "react";
import "./CheckoutGuest.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${window.location.hostname}:8000`;

const CheckoutGuest = ({ token }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [bookings, setBookings] = useState([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [totalBookingCost, setTotalBookingCost] = useState(0);

  useEffect(() => {
    fetchUnavailableRooms();
  }, []);

  const fetchUnavailableRooms = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/rooms/unavailable`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to fetch");

      setBookings(data.unavailable_rooms || []);
      setTotalEntries(data.total_unavailable || 0);
      setTotalBookingCost(data.total_booking_cost || 0);
    } catch (err) {
      setError(err.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (roomNumber) => {
  try {
    const res = await fetch(`${API_BASE_URL}/bookings/${roomNumber}/`, {

      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Checkout failed");

    alert(data.message);

    // Optimistically remove the checked-out booking from state
    setBookings((prev) => prev.filter((b) => b.room_number !== roomNumber));

    // Refresh from backend to stay accurate
    fetchUnavailableRooms();
  } catch (err) {
    alert(err.message);
  }
};


  return (
    <div className="checkout-guest-container">
      <div className="checkout-frame">
        <h2 className="checkout-title">Check Out Guests</h2>

        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : bookings.length === 0 ? (
          <p>No guests currently in rooms.</p>
        ) : (
          <>
            <div className="checkout-summary">
              <span>Total Entries: {totalEntries}</span>
              <span>Total Booking Cost: ₦{totalBookingCost.toLocaleString()}</span>
            </div>

            <div className="table-scroll-wrapper">
              <table className="checkout-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Room</th>
                    <th>Guest</th>
                    <th>Arrival</th>
                    <th>Departure</th>
                    <th>Days</th>
                    <th>Booking Date</th>
                    <th>Status</th>
                    <th>Payment</th>
                    <th>Cost</th>
                    <th>Created By</th>
                    <th>Attachment</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map((b) => (
                    <tr key={b.booking_id}>
                      <td>{b.booking_id}</td>
                      <td>{b.room_number}</td>
                      <td>{b.guest_name}</td>
                      <td>{b.arrival_date}</td>
                      <td>{b.departure_date}</td>
                      <td>{b.number_of_days}</td>
                      <td>{b.booking_date}</td>
                      <td>{b.status}</td>
                      <td>{b.payment_status}</td>
                      <td>₦{b.booking_cost?.toLocaleString()}</td>
                      <td>{b.created_by}</td>
                      <td>
                        {b.attachment ? (
                          <a
                            className="attachment-link"
                            href={`${API_BASE_URL}/files/attachments/${b.attachment.split("/").pop()}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            View
                          </a>
                        ) : (
                          "None"
                        )}
                      </td>
                      <td>
                        <div className="checkout-action-buttons">
                          <button
                            className="checkout-btn"
                            onClick={() => handleCheckout(b.room_number)}
                          >
                            Checkout
                          </button>
                          
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CheckoutGuest;
