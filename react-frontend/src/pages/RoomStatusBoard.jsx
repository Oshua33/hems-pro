import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./RoomStatusBoard.css";

const RoomStatusBoard = () => {
  const [rooms, setRooms] = useState([]);
  const navigate = useNavigate();

const formatNaira = (amount) => {
  return amount.toLocaleString("en-NG", {
    style: "currency",
    currency: "NGN",
    minimumFractionDigits: 0,
  });
};


  useEffect(() => {
    const fetchRooms = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const res = await axios.get("http://localhost:8000/rooms/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setRooms(res.data.rooms);
      } catch (error) {
        console.error("Error fetching rooms:", error.message);
      }
    };

    fetchRooms();
  }, []);

  const handleRoomClick = (room) => {
    const nonClickableStatuses = ["maintenance", "checked-in", "reserved"];
    if (nonClickableStatuses.includes(room.status.toLowerCase())) return;

    navigate(`/dashboard/bookings/create?room_number=${room.room_number}`);
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case "available": return "#cabebef8";     // Green
      case "reserved": return "#FFD700";      // Yellow
      case "checked-in": return "#4CAF50";    // Red
      case "checked-out": return "#90A4AE";   // Gray Blue
      case "maintenance": return "#e60606";   // red ✅
      default: return "#BDBDBD";              // Default gray
    }
  };

  const statusCounts = rooms.reduce((acc, room) => {
  const status = room.status.toLowerCase();
  acc[status] = (acc[status] || 0) + 1;
  return acc;
}, {});


  return (
    <div>
        <div className="room-grid">
        {rooms.map((room) => {
            const isClickable = !["maintenance", "checked-in", "reserved"].includes(
            room.status.toLowerCase()
            );

            return (
            <div
                key={room.id}
                className={`room-card ${isClickable ? "clickable" : "disabled"}`}
                style={{ backgroundColor: getStatusColor(room.status) }}
                onClick={() => handleRoomClick(room)}
                >
                <h3>{room.room_number}</h3>
                <p>{room.room_type}</p>
                <p>{formatNaira(room.amount)}</p> {/* ✅ Formatted ₦ amount */}
                </div>

            );
        })}
        </div>

        {/* ✅ Horizontal summary footer */}
        <div className="room-summary-footer">
            <span>🔘 Available: {statusCounts["available"] || 0}</span>
            <span>✅ Checked-in: {statusCounts["checked-in"] || 0}</span>
            <span>🟡 Reserved: {statusCounts["reserved"] || 0}</span>
            <span>🔴 Maintenance: {statusCounts["maintenance"] || 0}</span>
            </div>

    </div>
    );
};

export default RoomStatusBoard;
