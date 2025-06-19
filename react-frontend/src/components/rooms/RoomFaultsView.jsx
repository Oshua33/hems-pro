import React, { useEffect, useState } from "react";
import "./RoomFaultsView.css";

const RoomFaultsView = ({ room, onClose, onRefresh }) => {
  const [faults, setFaults] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("token"); // ⬅️ Get token from localStorage

  /* ───────────────────────── Fetch Faults ───────────────────────── */
  const fetchFaults = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/rooms/${room.room_number}/faults`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setFaults(data || []);

      await checkAndSetRoomStatus(data || []);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error("Error fetching faults:", err);
    } finally {
      setLoading(false);
    }
  };

  /* ─────────── Decide maintenance / available and hit backend ─────────── */
  const checkAndSetRoomStatus = async (faultList) => {
    const hasUnresolved = faultList.some((f) => !f.resolved);
    if (!hasUnresolved) return; // already available

    try {
      await fetch(
        `http://localhost:8000/rooms/${room.room_number}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ status: "maintenance" }),
        }
      );
    } catch (err) {
      console.error("Could not set room to maintenance:", err);
    }
  };

  useEffect(() => {
    fetchFaults();
  }, [room]);

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "Pending");

  /* ─────────────────────── Update Fault Status ─────────────────────── */
  const updateFaultStatus = async (faultId, resolved) => {
    try {
      const response = await fetch("http://localhost:8000/rooms/faults/update", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify([{ id: faultId, resolved }]),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Update failed:", errorText);
        alert("Failed to update fault status.\n" + errorText);
        return;
      }

      // Fetch updated faults
      const faultsResponse = await fetch(`http://localhost:8000/rooms/${room.room_number}/faults`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      const freshFaults = await faultsResponse.json();
      setFaults(freshFaults || []);

      // ✅ Now update room status based on fault resolution states
      const anyUnresolved = (freshFaults || []).some(f => !f.resolved);
      const newStatus = anyUnresolved ? "maintenance" : "available";

      const statusResponse = await fetch(`http://localhost:8000/rooms/${room.room_number}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!statusResponse.ok) {
        const text = await statusResponse.text();
        console.error("Failed to update room status:", text);
      }

      if (onRefresh) onRefresh();

    } catch (error) {
      console.error("Error updating fault or room status:", error);
      alert("Network error occurred.");
    }
  };

  /* ───────────────────────────── UI ───────────────────────────── */
  return (
    <div className="faults-view-modal">
      <div className="modal-overlay">
        <div className="modal-content">
          <button className="close-btn" onClick={onClose}>×</button>
          <h3>Faults for Room {room.room_number}</h3>

          {loading ? (
            <p>Loading...</p>
          ) : faults.length === 0 ? (
            <p>No faults found.</p>
          ) : (
            <table className="faults-table">
              <thead>
                <tr>
                  <th>ID</th><th>Description</th><th>Date Created</th>
                  <th>Date Resolved</th><th>Status</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {faults.map(f => (
                  <tr key={f.id}>
                    <td>{f.id}</td>
                    <td>{f.description}</td>
                    <td>{formatDate(f.created_at)}</td>
                    <td>{formatDate(f.resolved_at)}</td>
                    <td>
                      <input
                        type="checkbox"
                        checked={f.resolved}
                        onChange={(e) => updateFaultStatus(f.id, e.target.checked)}
                      />
                    </td>
                    <td>
                      {f.resolved ? (
                        <button
                          className="action-btn small"
                          onClick={() => updateFaultStatus(f.id, false)}
                        >Unresolve</button>
                      ) : (
                        <span style={{ color: "#888" }}>Not resolved</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="button-group">
            <button onClick={fetchFaults} className="action-btn">Refresh</button>
            <button onClick={onClose} className="action-btn">Close</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomFaultsView;
