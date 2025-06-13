import { useEffect, useState } from 'react';
import axios from 'axios';

export default function ReservationAlertButton() {
  const [blink, setBlink] = useState(false);
  const [count, setCount] = useState(0);

  useEffect(() => {
    const checkAlerts = async () => {
      try {
        const { data } = await axios.get("http://localhost:8000/bookings/reservations/alerts");
        setCount(data.count || 0);
        setBlink(data.active_reservations);
      } catch (e) {
        console.error("Alert check failed", e);
      }
    };

    checkAlerts();
    const interval = setInterval(checkAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`p-2 rounded ${blink ? "bg-red-500 animate-pulse" : "bg-gray-500"}`}
    >
      🔔 Reservation {count > 0 ? `(${count})` : ""}
    </div>
  );
}
