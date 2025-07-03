import React, { useState } from "react";
import "./VoidPayment.css";

const VoidPayment = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [hasFetched, setHasFetched] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [showDialog, setShowDialog] = useState(false);
  const [voiding, setVoiding] = useState(false);

  const fetchVoidedEligiblePayments = async () => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append("start_date", startDate);
      params.append("end_date", endDate);

      const url = `http://localhost:8000/payments/list?${params.toString()}`;

      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      const data = await res.json();
      setPayments(data.payments || []);
      setHasFetched(true);
    } catch (err) {
      setError("Failed to fetch payments.");
    } finally {
      setLoading(false);
    }
  };

  const openVoidDialog = (payment) => {
    setSelectedPayment(payment);
    setShowDialog(true);
  };

  const handleConfirmVoid = async () => {
    setVoiding(true);
    try {
      const res = await fetch(`http://localhost:8000/payments/void/${selectedPayment.payment_id}/`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || "Failed to void payment.");
        return;
      }

      alert(data.message);
      setPayments((prev) =>
        prev.map((p) =>
          p.payment_id === selectedPayment.payment_id ? { ...p, status: "voided" } : p
        )
      );
      setShowDialog(false);
      setSelectedPayment(null);
    } catch (error) {
      console.error("Void error:", error);
      alert("An error occurred while trying to void the payment.");
    } finally {
      setVoiding(false);
    }
  };

  return (
    <div className="void-payment-container">
      <h2 className="void-title">❌Void Payment</h2>

      <div className="filter-row">
        <label htmlFor="start-date">Start Date:</label>
        <input
          type="date"
          id="start-date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <label htmlFor="end-date">End Date:</label>
        <input
          type="date"
          id="end-date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        <button className="fetch-button" onClick={fetchVoidedEligiblePayments}>
          Fetch
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {hasFetched && (
        <div className="payment-table-wrapper">
          <table className="payment-table">
            <thead>
              <tr>
                <th>PayID</th>
                <th>BookID</th>
                <th>Guest</th>
                <th>Room</th>
                <th>Amount Paid</th>
                <th>Method</th>
                <th>Payment Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {payments.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: "center" }}>
                    No payments found.
                  </td>
                </tr>
              ) : (
                payments.map((p) => (
                  <tr
                    key={p.payment_id}
                    className={p.status === "voided" ? "voided-payment" : ""}
                  >
                    <td>{p.payment_id}</td>
                    <td>{p.booking_id}</td>
                    <td>{p.guest_name}</td>
                    <td>{p.room_number}</td>
                    <td>₦{p.amount_paid?.toLocaleString()}</td>
                    <td>{p.payment_method}</td>
                    <td>{new Date(p.payment_date).toLocaleString()}</td>
                    <td>
                      {p.status !== "voided" && (
                        <button className="void-btn" onClick={() => openVoidDialog(p)}>
                          ❌Void
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showDialog && selectedPayment && (
        <div className="modal-overlay">
          <div className="modal-box">
            <p>
              Are you sure you want to void payment <strong>#{selectedPayment.payment_id}</strong> for{" "}
              <strong>{selectedPayment.guest_name}</strong> (₦{selectedPayment.amount_paid?.toLocaleString()})?
            </p>
            <div className="modal-buttons">
              <button onClick={handleConfirmVoid} disabled={voiding}>
                {voiding ? "Voiding..." : "Yes, Void"}
              </button>
              <button onClick={() => setShowDialog(false)} disabled={voiding}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoidPayment;
