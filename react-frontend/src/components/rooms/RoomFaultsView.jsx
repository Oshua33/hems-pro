import React, { useEffect, useState } from "react";
import './RoomFaultsView.css';

const RoomFaultsView = ({ room, onClose }) => {
  const [faults, setFaults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFaults = async () => {
      try {
        const response = await fetch(`http://localhost:8000/rooms/${room.room_number}/faults`);
        const data = await response.json();
        setFaults(data || []);
      } catch (error) {
        console.error("Error fetching faults:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchFaults();
  }, [room]);

  const formatDate = (dateString) => {
    if (!dateString) return "Pending";
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const updateFaultStatus = async (faultId, resolved) => {
    try {
      const response = await fetch(`http://localhost:8000/rooms/faults/${faultId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: faultId, resolved }),
      });

      if (response.ok) {
        const updatedFaults = await fetch(`http://localhost:8000/rooms/${room.room_number}/faults`);
        const data = await updatedFaults.json();
        setFaults(data);
      } else {
        const errorText = await response.text();
        console.error("Update failed:", errorText);
        alert("Failed to update fault status.\n" + errorText);
      }
    } catch (error) {
      console.error("Error updating fault status:", error);
      alert("Network error updating fault.");
    }
  };

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
                  <th>ID</th>
                  <th>Description</th>
                  <th>Date Created</th>
                  <th>Date Resolved</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {faults.map((fault) => (
                  <tr key={fault.id}>
                    <td>{fault.id}</td>
                    <td>{fault.description}</td>
                    <td>{formatDate(fault.created_at)}</td>
                    <td>{formatDate(fault.resolved_at)}</td>
                    <td>
                      <input
                        type="checkbox"
                        checked={fault.resolved}
                        onChange={(e) => updateFaultStatus(fault.id, e.target.checked)}
                      />
                    </td>
                    <td>
                      {fault.resolved ? (
                        <button
                          className="action-btn small"
                          onClick={() => updateFaultStatus(fault.id, false)}
                        >
                          Unresolve
                        </button>
                      ) : (
                        <span style={{ color: "#888" }}>Not resolved</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <button onClick={onClose} className="action-btn">Close</button>
        </div>
      </div>
    </div>
  );
};

export default RoomFaultsView;
