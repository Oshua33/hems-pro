import React, { useEffect, useState } from "react";
import "./ListBooking.css";

const ListBooking = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      let url = "http://localhost:8000/bookings/list";
      const params = [];
      if (startDate) params.push(`start_date=${startDate}`);
      if (endDate) params.push(`end_date=${endDate}`);
      if (params.length > 0) url += "?" + params.join("&");

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      const data = await response.json();
      setBookings(data.bookings || []);
    } catch (err) {
      setError("Failed to fetch bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleView = (booking) => {
    alert(`View Booking: ID ${booking.id}`);
  };

  const handleUpdate = (booking) => {
    alert(`Update Booking: ID ${booking.id}`);
  };

  return (
    <div className="list-booking-container">
      <div className="list-booking-header">
        <h2>📄 Booking List</h2>
        <div className="date-range-filters">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <button onClick={fetchBookings}>Filter</button>
        </div>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : (
        <div className="booking-table-wrapper">
          <table className="booking-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Room</th>
                <th>Guest</th>
                <th>Gender</th>
                <th>Arrival</th>
                <th>Departure</th>
                <th>No. of Days</th>
                <th>Booking Type</th>
                <th>Phone</th>
                <th>Booking Date</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Mode of ID</th>
                <th>ID Number</th>
                <th>Address</th>
                <th>Cost</th>
                <th>Created By</th>
                <th>Vehicle No</th>
                <th>Attachment</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{b.room_number}</td>
                  <td>{b.guest_name}</td>
                  <td>{b.gender}</td>
                  <td>{b.arrival_date}</td>
                  <td>{b.departure_date}</td>
                  <td>{b.number_of_days}</td>
                  <td>{b.booking_type}</td>
                  <td>{b.phone_number}</td>
                  <td>{b.booking_date}</td>
                  <td>{b.status}</td>
                  <td>{b.payment_status}</td>
                  <td>{b.mode_of_identification}</td>
                  <td>{b.identification_number}</td>
                  <td>{b.address}</td>
                  <td>₦{b.booking_cost}</td>
                  <td>{b.created_by}</td>
                  <td>{b.vehicle_no}</td>
                  <td>
                    {b.attachment ? (
                      <a href={b.attachment} target="_blank" rel="noopener noreferrer">
                        View
                      </a>
                    ) : (
                      "None"
                    )}
                  </td>
                  <td>
                    <button onClick={() => handleView(b)}>View</button>
                    <button onClick={() => handleUpdate(b)}>Update</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ListBooking;
