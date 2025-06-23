// src/components/payments/ListPayment.jsx
import React, { useEffect, useState } from "react";
import "./ListPayment.css";

const ListPayment = () => {
  const [payments, setPayments] = useState([]);
  const [status, setStatus] = useState("none");
  const [debtorName, setDebtorName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState({});
  const [methodTotals, setMethodTotals] = useState({});

  const fetchPayments = async (endpoint) => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();

      setPayments(data.payments || []);
      setSummary(data.summary || {});
      setMethodTotals(data.payment_method_totals || {});
    } catch (err) {
      setError("Failed to fetch payments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (status === "none") return;
    if (status === "All") {
      fetchPayments("http://localhost:8000/payments/list");
    } else {
      fetchPayments(`http://localhost:8000/payments/status?status=${status}`);
    }
  }, [status]);

  const handleDaily = () => {
    fetchPayments("http://localhost:8000/payments/daily");
  };

  const handleFetchByDate = () => {
    let url = `http://localhost:8000/payments/list`;
    if (startDate || endDate) {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      url += `?${params.toString()}`;
    }
    fetchPayments(url);
  };

  const handleVoid = (paymentId) => {
    alert(`Void payment #${paymentId}`);
  };

  return (
    <div className="list-payment-container">
      <div className="list-payment-header-row">
        <h2 className="compact-title">💳 Payment Records</h2>
      </div>

      <div className="filters-grid">
        <div className="filter-item">
            <label>Payment Status:</label>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="none">None</option>
            <option value="All">All</option>
            <option value="fully paid">fully paid</option>
            <option value="part payment">part payment</option>
            <option value="void payment">void payment</option>
            </select>
        </div>

        <div className="filter-item">
            <label>Debtor Name:</label>
            <input
            type="text"
            placeholder="Enter name..."
            value={debtorName}
            onChange={(e) => setDebtorName(e.target.value)}
            />
        </div>

        <div className="daily-button-wrapper">
            <button className="daily-button" onClick={handleDaily}>📆 Daily Payment</button>
        </div>


        <div className="filter-item date-range-wrapper">
            <label>Date Range:</label>
            <div className="date-range-row">
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
            <button className="fetch-button" onClick={handleFetchByDate}>Fetch</button>
            </div>
        </div>
        </div>


      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {payments.length > 0 && (
        <div className="payment-table-wrapper">
          <table className="payment-table">
            <thead>
              <tr>
                <th>PayID</th>
                <th>BookID</th>
                <th>Guest</th>
                <th>Room</th>
                <th>Booking Cost</th>
                <th>Amount Paid</th>
                <th>Disc</th>
                <th>Due</th>
                <th>Method</th>
                <th>Status</th>
                <th>Payment Date</th>
                <th>Void Date</th>
                <th>Created By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.payment_id}>
                  <td>{p.payment_id}</td>
                  <td>{p.booking_id}</td>
                  <td>{p.guest_name}</td>
                  <td>{p.room_number}</td>
                  <td>₦{(p.booking_cost || 0).toLocaleString()}</td>
                  <td>₦{p.amount_paid.toLocaleString()}</td>
                  <td>₦{p.discount_allowed.toLocaleString()}</td>
                  <td>₦{p.balance_due.toLocaleString()}</td>
                  <td>{p.payment_method}</td>
                  <td>{p.status}</td>
                  <td>{new Date(p.payment_date).toLocaleString()}</td>
                  <td>{p.void_date}</td>
                  <td>{p.created_by}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="view-btn">View</button>
                      <button className="void-btn" onClick={() => handleVoid(p.payment_id)}>Void</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="payment-summary">
            <p><strong>Total Bookings:</strong> {summary.total_bookings}</p>
            <p><strong>Total Booking Cost:</strong> ₦{(summary.total_booking_cost || 0).toLocaleString()}</p>
            <p><strong>Total Paid:</strong> ₦{(summary.total_amount_paid || 0).toLocaleString()}</p>
            <p><strong>Total Discount:</strong> ₦{(summary.total_discount_allowed || 0).toLocaleString()}</p>
            <p><strong>Total Due:</strong> ₦{(summary.total_due || 0).toLocaleString()}</p>
          </div>

          <div className="payment-method-summary">
            <p><strong>Cash:</strong> ₦{(methodTotals.cash || 0).toLocaleString()}</p>
            <p><strong>POS Card:</strong> ₦{(methodTotals.pos_card || 0).toLocaleString()}</p>
            <p><strong>Bank Transfer:</strong> ₦{(methodTotals.bank_transfer || 0).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListPayment;
