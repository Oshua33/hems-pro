import React, { useEffect, useState } from "react";

import { useNavigate } from "react-router-dom";
import "./ListEvent.css";
import EventUpdate from "./EventUpdate"; // Adjust path as needed
import CancelEvent from "./CancelEvent"; // adjust path if necessary






const ListEvent = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [organizer, setOrganizer] = useState("");
  const [error, setError] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState(null);



  //const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState({ total_entries: 0, total_booking_amount: 0 });

  const fetchEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      let url = "http://localhost:8000/events";
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      // Handle new backend format
      const filtered = organizer
        ? data.events.filter((e) =>
            e.organizer?.toLowerCase().includes(organizer.toLowerCase())
          )
        : data.events;

      setEvents(filtered);
      setSummary(data.summary || {});
    } catch (err) {
      console.error(err);
      setError("Failed to fetch events");
    } finally {
      setLoading(false);
    }
  };



  useEffect(() => {
    fetchEvents();
  }, []);

  const totalAmount = events.reduce((sum, e) => sum + (e.event_amount || 0), 0);
  const navigate = useNavigate();


  return (
    <div className="list-event-container">
      <div className="list-event-header-row">
        <h2 className="compact-title">🎉 Event Management</h2>

        <div className="filters">
          <input
            type="text"
            placeholder="Search organizer"
            value={organizer}
            onChange={(e) => setOrganizer(e.target.value)}
            className="filter-input"
          />
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          <button onClick={fetchEvents} className="fetch-button">↻ Refresh</button>
        </div>
      </div>

      {loading && <p>Loading events...</p>}
      {error && <p className="error">{error}</p>}

      <div className="event-table-wrapper">
        <table className="event-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Organizer</th>
              <th>Title</th>
              <th>Phone</th>
              <th>Start</th>
              <th>End</th>
              <th>Event Amount</th>
              <th>Caution Fee</th>
              <th>Status</th>
              <th>Address</th>
              <th>Created by</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: "center" }}>No events found</td>
              </tr>
            ) : (
              events.map((event) => (
                <tr key={event.id}>
                  <td>{event.id}</td>
                  <td>{event.organizer}</td>
                  <td>{event.title}</td>
                  <td>{event.phone_number}</td>
                  <td>{event.start_datetime}</td>
                  <td>{event.end_datetime}</td>
                  <td>₦{event.event_amount?.toLocaleString()}</td>
                  <td>₦{event.caution_fee?.toLocaleString()}</td>
                  <td>{event.payment_status}</td>
                  <td>{event.address}</td>
                  <td>{event.created_by}</td>
                  <td className="action-buttons">
                    <button
                      className="view-btn"
                      onClick={() => navigate("/dashboard/events/view", { state: { event } })}
                    >
                      View
                    </button>

                    <button
                      className="update-btn"
                      onClick={() => navigate("/dashboard/events/update", { state: { event } })}
                    >
                      Update
                    </button>


                    <button
                      className="cancel-btn"
                      onClick={() => {
                        setSelectedEventId(event.id);
                        setShowCancelModal(true);
                      }}
                    >
                      Cancel
                    </button>

                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {showCancelModal && selectedEventId && (
        <CancelEvent
          eventId={selectedEventId}
          onClose={() => {
            setShowCancelModal(false);
            setSelectedEventId(null);
            fetchEvents(); // refresh event list after cancellation
          }}
        />
      )}

      </div>

      {events.length > 0 && (
      <div className="event-summary-wrapper">
        <div><strong>Total Entries:</strong> {summary.total_entries}</div>
        <div><strong>Total Booking Amount:</strong> ₦{summary.total_booking_amount?.toLocaleString()}</div>
      </div>
    )}


      

    </div>
  );
};

export default ListEvent;
