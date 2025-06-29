import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Cell, CartesianGrid } from "recharts";
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
      case "available": return "#cabebef8";
      case "reserved": return "#FFD700";
      case "checked-in": return "#4CAF50";
      case "checked-out": return "#90A4AE";
      case "maintenance": return "#e60606";
      default: return "#BDBDBD";
    }
  };

  const statusCounts = rooms.reduce((acc, room) => {
    const status = room.status.toLowerCase();
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  const chartData = [
    { name: "Available", value: statusCounts["available"] || 0, color: "#cabebef8" },
    { name: "Checked-in", value: statusCounts["checked-in"] || 0, color: "#4CAF50" },
    { name: "Reserved", value: statusCounts["reserved"] || 0, color: "#FFD700" },
    { name: "Maintenance", value: statusCounts["maintenance"] || 0, color: "#e60606" },
  ];

  return (
    <div style={{ maxHeight: "100vh", overflow: "hidden" }}>
      <div className="room-grid" style={{ maxHeight: "35vh", overflowY: "auto" }}>
        {rooms.map((room) => {
          const isClickable = !["maintenance", "checked-in", "reserved"].includes(
            room.status.toLowerCase()
          );

          return (
            <div
              key={room.id}
              className={`room-card ${isClickable ? "clickable" : "disabled"}`}
              style={{ backgroundColor: getStatusColor(room.status), fontSize: "0.7rem", padding: "4px" }}
              onClick={() => handleRoomClick(room)}
            >
              <h3 style={{ margin: "2px 0" }}>{room.room_number}</h3>
              <p style={{ margin: "1px 0" }}>{room.room_type}</p>
              <p style={{ margin: "1px 0" }}>{formatNaira(room.amount)}</p>
            </div>
          );
        })}
      </div>

      <div className="room-summary-footer" style={{ fontSize: "0.8rem", padding: "6px" }}>
        <span>🔘 Available: {statusCounts["available"] || 0}</span>
        <span>🟢 Checked-in🧍‍♂️: {statusCounts["checked-in"] || 0}</span>
        <span>🟡 Reserved🕒: {statusCounts["reserved"] || 0}</span>
        <span>🔴 Maintenance🛠️: {statusCounts["maintenance"] || 0}</span>
      </div>

      <hr className="room-divider" style={{ margin: "8px 0" }} />

      <div className="chart-container" style={{ height: "35vh" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" isAnimationActive>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RoomStatusBoard;
