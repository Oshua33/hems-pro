import React, { useState } from "react";
import "./ListBooking.css";
import ViewForm from "./ViewForm";
import UpdateForm from "./UpdateForm";
import { openViewForm } from "./viewFormUtils";




const ListBooking = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [hasFiltered, setHasFiltered] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [totalBookings, setTotalBookings] = useState(0);
  const [totalBookingCost, setTotalBookingCost] = useState(0);
  const [bookingToUpdate, setBookingToUpdate] = useState(null);



  const fetchBookings = async () => {
    setLoading(true);
    setHasFiltered(true);
    setError(null);

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
      setTotalBookings(data.total_bookings || 0);
      setTotalBookingCost(data.total_booking_cost || 0);
    } catch (err) {
      setError("Failed to fetch bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleView = (booking) => {
    openViewForm(booking); // ✅ Use utility directly
  };

  const handleUpdate = (booking) => {
    setBookingToUpdate(booking);
  };


  const handleCloseView = () => {
    setSelectedBooking(null);
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

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {hasFiltered && (
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
                <th>Days</th>
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
                      <a
                        className="attachment-link"
                        href={`http://localhost:8000/files/attachments/${b.attachment.split("/").pop()}`}
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
                    <button className="view-btn" onClick={() => handleView(b)}>
                      View Form
                    </button>
                    <button className="update-btn" onClick={() => handleUpdate(b)}>
                      Update
                    </button>
                  </td>
                </tr>
              ))}
              {bookings.length === 0 && !loading && (
                <tr>
                  <td colSpan="20" style={{ textAlign: "center" }}>
                    No bookings found for the selected date range.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {bookings.length > 0 && (
            <div className="booking-summary">
              <p>
                <strong>Total Entries:</strong> {totalBookings}
              </p>
              <p>
                <strong>Total Booking Cost:</strong> ₦
                {totalBookingCost.toLocaleString()}
              </p>
            </div>
          )}
        </div>
      )}

      {/* 🚀 Auto Guest Form Print */}
      {selectedBooking && (
        <ViewForm booking={selectedBooking} onClose={handleCloseView} />
      )}

      {bookingToUpdate && (
  <UpdateForm
    booking={bookingToUpdate}
    onClose={(updatedBooking) => {
      if (updatedBooking) {
        setBookings((prev) =>
          prev.map((b) =>
            b.id === updatedBooking.id ? updatedBooking : b
          )
        );
      }
      setBookingToUpdate(null);
    }}
  />
)}

    </div>
  );
};

export default ListBooking;
