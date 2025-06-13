// src/components/MainContent.jsx
import React from "react";

export default function MainContent() {
  return (
    <main className="flex-1 bg-gray-100 p-6 overflow-y-auto">
      <div className="text-gray-700 text-lg">
        📊 Dashboard Overview
      </div>

      {/* You can add cards, charts, etc., here */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold">Total Rooms</h2>
          <p className="text-3xl mt-2">25</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold">Active Bookings</h2>
          <p className="text-3xl mt-2">12</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold">Pending Payments</h2>
          <p className="text-3xl mt-2">₦52,000</p>
        </div>
      </div>
    </main>
  );
}
