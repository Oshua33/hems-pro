// src/App.js

import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import HomePage from "./pages/HomePage";
import LicensePage from "./modules/license/LicensePage";
import LoginPage from "./modules/auth/LoginPage";
import RegisterPage from "./modules/auth/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import UsersPage from "./pages/UsersPage";
import RoomsPage from "./pages/RoomsPage";
import BookingsPage from "./pages/BookingsPage";

import CreateBooking from "./components/bookings/CreateBooking";
import ListBooking from "./components/bookings/ListBooking";
import CheckoutGuest from "./components/bookings/CheckoutGuest";
import CancelBooking from "./components/bookings/CancelBooking";
// import ViewBooking from "./components/bookings/ViewBooking"; // ← only add this if you really need a dynamic route

const App = () => {
  const [isLicenseVerified, setIsLicenseVerified] = useState(false);

  useEffect(() => {
    const licenseVerified = localStorage.getItem("license_verified") === "true";
    setIsLicenseVerified(licenseVerified);
  }, []);

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route
          path="/license"
          element={<LicensePage setIsLicenseVerified={setIsLicenseVerified} />}
        />
        <Route
          path="/login"
          element={
            isLicenseVerified ? <LoginPage /> : <Navigate to="/license" replace />
          }
        />
        <Route
          path="/register"
          element={
            isLicenseVerified ? <RegisterPage /> : <Navigate to="/license" replace />
          }
        />

        {/* Protected dashboard routes */}
        <Route
          path="/dashboard"
          element={
            isLicenseVerified ? <DashboardPage /> : <Navigate to="/license" replace />
          }
        >
          <Route path="users" element={<UsersPage />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route path="bookings" element={<BookingsPage />}>
            <Route index element={<ListBooking />} /> {/* 👈 default subpage */}
            <Route path="create" element={<CreateBooking />} />
            <Route path="list" element={<ListBooking />} />
            <Route path="checkout" element={<CheckoutGuest />} />
            <Route path="cancel" element={<CancelBooking />} />
            {/* <Route path=":booking_id" element={<ViewBooking />} /> ← Add last only if needed */}
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
