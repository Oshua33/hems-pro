// src/components/payments/CreatePayment.jsx

import React, { useState } from "react";
import "./CreatePayment.css";

const CreatePayment = ({ booking, onClose, onSuccess }) => {
  const [amountPaid, setAmountPaid] = useState("");
  const [discountAllowed, setDiscountAllowed] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 16));
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`http://localhost:8000/payments/${booking.id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          amount_paid: parseFloat(amountPaid),
          discount_allowed: parseFloat(discountAllowed) || 0,
          payment_method: paymentMethod,
          payment_date: new Date(paymentDate).toISOString(),
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Payment failed");
      }

      setMessage("✅ " + data.message);

      // Pass status info to parent via onSuccess
      if (onSuccess) {
        const status = data.updated_booking?.payment_status || "pending";
        onSuccess({ status });
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-form-overlay">
      <div className="payment-form-container">
        <h2>💳 Create Payment for Booking #{booking.id}</h2>
        <form onSubmit={handleSubmit}>
          <label>Amount Paid (₦)</label>
          <input
            type="number"
            value={amountPaid}
            onChange={(e) => setAmountPaid(e.target.value)}
            required
          />

          <label>Discount Allowed (₦)</label>
          <input
            type="number"
            value={discountAllowed}
            onChange={(e) => setDiscountAllowed(e.target.value)}
          />

          <label>Payment Method</label>
          <select
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            required
          >
            <option value="cash">Cash</option>
            <option value="bank transfer">Bank Transfer</option>
            <option value="POS">POS</option>
          </select>

          <label>Payment Date</label>
          <input
            type="datetime-local"
            value={paymentDate}
            onChange={(e) => setPaymentDate(e.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}

          <div className="payment-buttons">
            <button type="submit" disabled={loading}>
              {loading ? "Processing..." : "Submit Payment"}
            </button>
            <button type="button" onClick={onClose} className="cancel-btn">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePayment;
