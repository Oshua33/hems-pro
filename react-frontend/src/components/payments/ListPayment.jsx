import React, { useState } from "react";
import "./ListPayment.css";

const ListPayment = () => {
  const [payments, setPayments] = useState([]);
  const [status, setStatus] = useState("none");
  const [debtorName, setDebtorName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [noDataMessage, setNoDataMessage] = useState(""); // ✅ new
  const [totalPayments, setTotalPayments] = useState(0);
  const [totalAmount, setTotalAmount] = useState(0);
  const [methodTotals, setMethodTotals] = useState({});
  const [viewMode, setViewMode] = useState("");

  const fetchWithToken = async (url) => {
    return fetch(url, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }).then((res) => res.json());
  };

  const fetchByStatus = async () => {
    if (status === "none") return;
    setLoading(true);
    setViewMode("status");
    setError(null);
    setNoDataMessage(""); // reset
    try {
      const params = new URLSearchParams();
      if (status !== "All") params.append("status", status);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      const url = `http://localhost:8000/payments/by-status?${params}`;
      const data = await fetchWithToken(url);
      setPayments(data.payments || []);
      setTotalPayments(data.total_payments || 0);
      setTotalAmount(data.total_amount || 0); // ✅ add this line
      setMethodTotals({});
      if (!data.payments || data.payments.length === 0) {
        setNoDataMessage("No payment records found for the selected status.");
      }
    } catch {
      setError("Failed to fetch by status.");
    } finally {
      setLoading(false);
    }
  };


  const fetchDaily = async () => {
    setLoading(true);
    setViewMode("daily");
    setError(null);
    setNoDataMessage("");
    try {
      const data = await fetchWithToken("http://localhost:8000/payments/total_daily_payment");
      setPayments(data.payments || []);
      setTotalPayments(data.total_payments || 0);
      setTotalAmount(data.total_amount || 0);
      setMethodTotals(data.total_by_method || {});
      if (!data.payments || data.payments.length === 0) {
        setNoDataMessage("No daily payments found for today.");
      }
    } catch {
      setError("Failed to fetch daily payments.");
    } finally {
      setLoading(false);
    }
  };

  const fetchDebtors = async () => {
    setLoading(true);
    setViewMode("debtor");
    setError(null);
    setNoDataMessage("");
    try {
      const params = new URLSearchParams();
      if (debtorName) params.append("debtor_name", debtorName);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      const url = `http://localhost:8000/payments/debtor_list?${params}`;
      const data = await fetchWithToken(url);

      setPayments(data.debtors || []);
      setTotalPayments(data.total_debtors || 0);
      setTotalAmount(data.total_current_debt || 0);
      setMethodTotals({});
      if (!data.debtors || data.debtors.length === 0) {
        setNoDataMessage("No debtors found for the selected filters.");
      }
    } catch {
      setError("Failed to fetch debtor list.");
    } finally {
      setLoading(false);
    }
  };

  const handleView = (paymentId) => {
    alert(`View payment #${paymentId}`);
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
            <option value="none">Select</option>
            <option value="All">All</option>
            <option value="fully paid">Fully Paid</option>
            <option value="part payment">Part Payment</option>
            <option value="voided">Voided</option>
          </select>
          <button className="fetch-button" onClick={fetchByStatus}>Fetch</button>
        </div>

        <div className="filter-item">
          <label>Debtor Name:</label>
          <input
            type="text"
            placeholder="Enter name..."
            value={debtorName}
            onChange={(e) => setDebtorName(e.target.value)}
          />
          <button className="fetch-button" onClick={fetchDebtors}>Fetch Debtors</button>
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
          </div>
        </div>

        <div className="daily-button-wrapper">
          <button className="daily-button" onClick={fetchDaily}>📊 Daily Summary</button>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {noDataMessage && <p className="no-data">{noDataMessage}</p>}

      {payments.length > 0 && (
        <div className="payment-table-wrapper">
          <table className="payment-table">
            <thead>
              <tr>
                {viewMode === "debtor" ? (
                  <>
                    <th>Guest</th>
                    <th>Room</th>
                    <th>BookID</th>
                    <th>Room Price</th>
                    <th>Days</th>
                    <th>Total Due</th>
                    <th>Paid</th>
                    <th>Discount</th>
                    <th>Amount Due</th>
                    <th>Booking Date</th>
                    <th>Last Payment</th>
                  </>
                ) : (
                  <>
                    <th>PayID</th>
                    <th>BookID</th>
                    <th>Guest</th>
                    <th>Room</th>
                    <th>Amount Paid</th>
                    <th>Disc</th>
                    <th>Due</th>
                    <th>Method</th>
                    <th>Status</th>
                    <th>Payment Date</th>
                    <th>Void Date</th>
                    <th>Created By</th>
                    <th>Actions</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {payments.map((p, i) => (
                <tr key={i}>
                  {viewMode === "debtor" ? (
                    <>
                      <td>{p.guest_name}</td>
                      <td>{p.room_number}</td>
                      <td>{p.booking_id}</td>
                      <td>₦{p.room_price?.toLocaleString()}</td>
                      <td>{p.number_of_days}</td>
                      <td>₦{p.total_due?.toLocaleString()}</td>
                      <td>₦{p.total_paid?.toLocaleString()}</td>
                      <td>₦{p.discount_allowed?.toLocaleString()}</td>
                      <td>₦{p.amount_due?.toLocaleString()}</td>
                      <td>{new Date(p.booking_date).toLocaleDateString()}</td>
                      <td>{p.last_payment_date ? new Date(p.last_payment_date).toLocaleDateString() : "-"}</td>
                    </>
                  ) : (
                    <>
                      <td>{p.payment_id}</td>
                      <td>{p.booking_id}</td>
                      <td>{p.guest_name}</td>
                      <td>{p.room_number}</td>
                      <td>₦{p.amount_paid?.toLocaleString()}</td>
                      <td>₦{p.discount_allowed?.toLocaleString()}</td>
                      <td>₦{p.balance_due?.toLocaleString()}</td>
                      <td>{p.payment_method}</td>
                      <td>{p.status}</td>
                      <td>{new Date(p.payment_date).toLocaleString()}</td>
                      <td>{p.void_date || "-"}</td>
                      <td>{p.created_by}</td>
                      <td><button className="view-btn" onClick={() => handleView(p.payment_id)}>View</button></td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>

          <div className="payment-summary">
            <p><strong>Total Records:</strong> {totalPayments}</p>
            <p><strong>Total Amount:</strong> ₦{totalAmount.toLocaleString()}</p>
          </div>

          {viewMode === "daily" && (
            <div className="payment-method-summary">
              <h4>Breakdown by Payment Method</h4>
              <ul>
                <li><strong>Cash:</strong> ₦{(methodTotals?.cash || 0).toLocaleString()}</li>
                <li><strong>POS:</strong> ₦{(methodTotals?.pos_card || 0).toLocaleString()}</li>
                <li><strong>Bank Transfer:</strong> ₦{(methodTotals?.bank_transfer || 0).toLocaleString()}</li>
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ListPayment;
