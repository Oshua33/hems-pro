import React, { useState } from "react";
import "./ListBooking.css";
import ViewForm from "./ViewForm";
import UpdateForm from "./UpdateForm";
import CreatePayment from "../payments/CreatePayment";
import { openViewForm } from "./viewFormUtils";


// Define all columns
const ALL_COLUMNS = [
  { key: "id", label: "ID" },
  { key: "room_number", label: "Room" },
  { key: "guest_name", label: "Guest" },
  { key: "gender", label: "Gender" },
  { key: "arrival_date", label: "Arrival" },
  { key: "departure_date", label: "Departure" },
  { key: "number_of_days", label: "Days" },
  { key: "booking_type", label: "Booking Type" },
  { key: "phone_number", label: "Phone" },
  { key: "booking_date", label: "Booking Date" },
  { key: "status", label: "Status" },
  { key: "payment_status", label: "Payment" },
  { key: "mode_of_identification", label: "Mode of ID" },
  { key: "identification_number", label: "ID Number" },
  { key: "address", label: "Address" },
  { key: "booking_cost", label: "Cost" },
  { key: "created_by", label: "Created By" },
  { key: "vehicle_no", label: "Vehicle No" },
  { key: "attachment", label: "Attachment" },
  { key: "actions", label: "Actions" },
];

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
  const [showColumnMenu, setShowColumnMenu] = useState(false);
  const [paymentBooking, setPaymentBooking] = useState(null); // Booking for payment


  const handlePayment = (booking) => {
    setPaymentBooking(booking); // Open payment form for selected booking
  };




  const getInitialVisibleColumns = () => {
    const saved = localStorage.getItem("visibleColumns");
    if (saved) return JSON.parse(saved);
    return ALL_COLUMNS.reduce((acc, col) => ({ ...acc, [col.key]: true }), {});
  };

  const [visibleColumns, setVisibleColumns] = useState(getInitialVisibleColumns);


  const handleToggleColumn = (key) => {
    setVisibleColumns((prev) => {
      const updated = { ...prev, [key]: !prev[key] };
      localStorage.setItem("visibleColumns", JSON.stringify(updated));
      return updated;
    });
  };

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
    openViewForm(booking);
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
        <div className="booking-header-top">
          <h2>📄 Booking List</h2>
          <div className="column-control-wrapper">
            <button
              className="column-toggle-button"
              onClick={() => setShowColumnMenu(!showColumnMenu)}
            >
              🛠️ Hide Columns
            </button>
            {showColumnMenu && (
              <div className="column-dropdown-menu">
                {ALL_COLUMNS.map((col) => (
                  <label key={col.key}>
                    <input
                      type="checkbox"
                      checked={visibleColumns[col.key]}
                      onChange={() => handleToggleColumn(col.key)}
                    />
                    {col.label}
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>

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
                {ALL_COLUMNS.map(
                  (col) =>
                    visibleColumns[col.key] && <th key={col.key}>{col.label}</th>
                )}
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id}>
                  {visibleColumns.id && <td>{b.id}</td>}
                  {visibleColumns.room_number && <td>{b.room_number}</td>}
                  {visibleColumns.guest_name && <td>{b.guest_name}</td>}
                  {visibleColumns.gender && <td>{b.gender}</td>}
                  {visibleColumns.arrival_date && <td>{b.arrival_date}</td>}
                  {visibleColumns.departure_date && <td>{b.departure_date}</td>}
                  {visibleColumns.number_of_days && <td>{b.number_of_days}</td>}
                  {visibleColumns.booking_type && <td>{b.booking_type}</td>}
                  {visibleColumns.phone_number && <td>{b.phone_number}</td>}
                  {visibleColumns.booking_date && <td>{b.booking_date}</td>}
                  {visibleColumns.status && <td>{b.status}</td>}
                  {visibleColumns.payment_status && <td>{b.payment_status}</td>}
                  {visibleColumns.mode_of_identification && (
                    <td>{b.mode_of_identification}</td>
                  )}
                  {visibleColumns.identification_number && (
                    <td>{b.identification_number}</td>
                  )}
                  {visibleColumns.address && <td>{b.address}</td>}
                  {visibleColumns.booking_cost && (
                    <td>₦{b.booking_cost}</td>
                  )}
                  {visibleColumns.created_by && <td>{b.created_by}</td>}
                  {visibleColumns.vehicle_no && <td>{b.vehicle_no}</td>}
                  {visibleColumns.attachment && (
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
                  )}
                  {visibleColumns.actions && (
                    <td>
                      <button className="view-btn" onClick={() => handleView(b)}>
                        View Form
                      </button>
                      <button className="update-btn" onClick={() => handleUpdate(b)}>
                        Update
                      </button>
                      <button
                      className={`payment-btn ${
                        b.payment_status === "payment excess"
                          ? "excess"
                          : b.payment_status === "payment completed"
                          ? "completed"
                          : b.payment_status === "complimentary"
                          ? "complimentary"
                          : b.payment_status === "void"
                          ? "void"
                          : ["payment incomplete", "pending"].includes(b.payment_status)
                          ? "incomplete"
                          : ""
                      }`}
                      onClick={() => handlePayment(b)}
                    >
                      Payment
                    </button>



                    </td>
                  )}
                </tr>
              ))}
              {bookings.length === 0 && !loading && (
                <tr>
                  <td colSpan={ALL_COLUMNS.length} style={{ textAlign: "center" }}>
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

      {selectedBooking && (
        <ViewForm booking={selectedBooking} onClose={handleCloseView} />
      )}

      {bookingToUpdate && (
        <UpdateForm
          booking={bookingToUpdate}
          onClose={(updatedBooking) => {
            if (updatedBooking) {
              setBookings((prev) =>
                prev.map((b) => (b.id === updatedBooking.id ? updatedBooking : b))
              );
            }
            setBookingToUpdate(null);
          }}
        />
      )}

      {paymentBooking && (
  <CreatePayment
    booking={paymentBooking}
    onClose={() => setPaymentBooking(null)}
    onSuccess={(newPayment) => {
      // Update the bookings list with updated payment status
      setBookings((prev) =>
        prev.map((b) =>
          b.id === paymentBooking.id
            ? { ...b, payment_status: newPayment.status }
            : b
        )
      );
      setPaymentBooking(null); // Close modal after success
    }}
  />
)}

    </div>
  );
};

export default ListBooking;
