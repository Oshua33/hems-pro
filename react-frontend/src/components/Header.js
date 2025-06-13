// src/components/Header.jsx
import React from "react";

export default function Header() {
  return (
    <header className="bg-slate-800 text-white px-6 py-4 shadow-md flex justify-between items-center">
      <h1 className="text-2xl font-bold">Destone Hotel & Suite Dashboard</h1>
      <span className="text-sm text-gray-300">Welcome, Admin</span>
    </header>
  );
}
