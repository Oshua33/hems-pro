// src/components/payments/PaymentOutstandingList.jsx

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./PaymentOutstandingList.css";

const PaymentOutstandingList = () => {
  const [outstandingData, setOutstandingData] = useState([]);
  const [totalOutstanding, setTotalOutstanding] = useState(0);
  const [totalBalance, setTotalBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOutstanding = async () => {
      try {
        const res = await fetch("http://localhost:8000/payments/outstanding", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        const data = await res.json();

        setOutstandingData(data.outstanding_bookings || []);
        setTotalOutstanding(data.total_outstanding || 0);
        setTotalBalance(data.total_outstanding_balance || 0);
      } catch (error) {
        console.error("Failed to fetch outstanding payments", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOutstanding();
  }, []);

  const handleMakePayment = (booking) => {
    navigate(`/dashboard/payments/create/${booking.booking_id}`);
  };

  return (
    <div className="outstanding-wrapper">
      <h2 className="no-margin">💰 Outstanding Payments</h2>

      <div className="summary-box">
        <span>Total Outstanding: <strong> {totalOutstanding} </strong> </span>
        <span>Total Outstanding Balance:<strong> ₦{totalBalance.toLocaleString()} </strong> </span>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : outstandingData.length === 0 ? (
        <p>No outstanding payments found.</p>
      ) : (
        <table className="outstanding-table">
          <thead>
            <tr>
              <th>ID</th>  
              <th>Guest Name</th>
              <th>Room No</th>
              <th>Booking Date</th>
              <th>Total Due (₦)</th>
              <th>Total Paid (₦)</th>
              <th>Discount (₦)</th>
              <th>Amount Due (₦)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {outstandingData.map((booking) => (
              <tr key={booking.booking_id}>
                <td>{booking.booking_id}</td>
                <td>{booking.guest_name}</td>
                <td>{booking.room_number}</td>
                <td>{new Date(booking.booking_date).toLocaleDateString()}</td>
                <td>{booking.total_due.toLocaleString()}</td>
                <td>{booking.total_paid.toLocaleString()}</td>
                <td>{booking.discount_allowed.toLocaleString()}</td>
                <td><strong>₦{booking.amount_due.toLocaleString()}</strong></td>
                <td>
                  <button
                    className="pay-button"
                    onClick={() => handleMakePayment(booking)}
                  >
                    Make Payment
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PaymentOutstandingList;
