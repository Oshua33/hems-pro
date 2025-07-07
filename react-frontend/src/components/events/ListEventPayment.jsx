// src/components/events/ListEventPayment.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ListEventPayment.css";


const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${window.location.hostname}:8000`;

const ListEventPayment = () => {
  const navigate = useNavigate();
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState(null);

  const fetchPayments = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      let url = `${API_BASE_URL}/eventpayment/`;
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
      setPayments(data.payments || []);
      setSummary(data.summary || {});
    } catch (err) {
      setError("Failed to fetch event payments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  const handleView = (payment) => {
    navigate(`/dashboard/events/view/${payment.id}`);
  };

  return (
    <div className="list-event-payment-containers">
      <h2>📄 Event Payment List</h2>

      <div className="filterss">
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
        <button onClick={fetchPayments}>↻ Refresh</button>
      </div>

      {loading && <p>Loading payments...</p>}
      {error && <p className="errors">{error}</p>}

      <div className="payment-table-wrappers">
        <table className="event-payment-tables">
          <thead>
            <tr>
              <th>ID</th>
              <th>Organiser</th>
              <th>Event Amount</th>
              <th>Amount Paid</th>
              <th>Discount</th>
              <th>Balance Due</th>
              <th>Method</th>
              <th>Status</th>
              <th>Payment Date</th>
              <th>Created By</th>
              <th>Actions</th> {/* New Actions column */}
            </tr>
          </thead>
          <tbody>
            {payments.length === 0 ? (
              <tr>
                <td colSpan="11" style={{ textAlign: "center" }}>
                  No event payments found
                </td>
              </tr>
            ) : (
              payments.map((pay) => (
                <tr key={pay.id}>
                  <td>{pay.id}</td>
                  <td>{pay.organiser}</td>
                  <td>₦{pay.event_amount?.toLocaleString()}</td>
                  <td>₦{pay.amount_paid?.toLocaleString()}</td>
                  <td>₦{pay.discount_allowed?.toLocaleString()}</td>
                  <td>₦{pay.balance_due?.toLocaleString()}</td>
                  <td>{pay.payment_method}</td>
                  <td>{pay.payment_status}</td>
                  <td>{new Date(pay.payment_date).toLocaleString()}</td>
                  <td>{pay.created_by}</td>
                  <td>
                    <button onClick={() => handleView(pay)}>View</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="all-summary-wrappers">
        <div className="summary-rows">
          <div className="summary-lefts">💵 Cash Total:</div>
          <div className="summary-rights">₦{summary.total_cash?.toLocaleString()}</div>
        </div>
        <div className="summary-rows">
          <div className="summary-lefts">💳 POS Total:</div>
          <div className="summary-rights">₦{summary.total_pos?.toLocaleString()}</div>
        </div>
        <div className="summary-rows">
          <div className="summary-lefts">🏦 Transfer Total:</div>
          <div className="summary-rights">₦{summary.total_transfer?.toLocaleString()}</div>
        </div>
        <div className="summary-rows">
          <div className="summary-lefts">
            <strong>Total Payment:</strong>
          </div>
          <div className="summary-rights">
            <strong>₦{summary.total_payment?.toLocaleString()}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListEventPayment;
