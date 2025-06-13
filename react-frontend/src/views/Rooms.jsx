import React from "react";
import RoomTable from "../modules/rooms/RoomTable";

export default function Rooms() {
  const token = localStorage.getItem("token"); // Or use context

  return (
    <div>
      <h2>Room Management</h2>
      <RoomTable token={token} />
    </div>
  );
}
