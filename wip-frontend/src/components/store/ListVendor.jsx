import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ListVendor.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${window.location.hostname}:8000`;

const ListVendor = () => {
  const [vendors, setVendors] = useState([]);

  useEffect(() => {
    fetchVendors();
  }, []);

  const fetchVendors = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/vendor/`);
      setVendors(response.data);
    } catch (error) {
      console.error("Error fetching vendors:", error);
    }
  };

  const handleDelete = async (vendorId) => {
    if (!window.confirm("Are you sure you want to delete this vendor?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/vendor/${vendorId}`);
      fetchVendors();
    } catch (error) {
      console.error("Error deleting vendor:", error);
    }
  };

  const handleUpdate = async (vendor) => {
    const newName = prompt("Enter new business name", vendor.business_name);
    const newPhone = prompt("Enter new phone number", vendor.phone_number);
    const newAddress = prompt("Enter new address", vendor.address);

    if (!newName || !newPhone || !newAddress) {
        alert("All fields are required.");
        return;
    }

    try {
        await axios.put(`${API_BASE_URL}/vendor/${vendor.id}`, {
        business_name: newName,
        phone_number: newPhone,
        address: newAddress
        });
        fetchVendors();
    } catch (error) {
        console.error("Error updating vendor:", error);
        alert("Failed to update vendor. Check console for details.");
    }
    };


  return (
    <div className="vendor-container">
      <h2 className="vendor-heading">Vendor List</h2>
      <div className="vendor-table">
        <div className="table-header">
          <div>ID</div>
          <div>Business Name</div>
          <div>Phone</div>
          <div>Address</div>
          <div>Actions</div>
        </div>

        {vendors.length === 0 ? (
          <div className="table-row">
            <div colSpan="5">No vendors found.</div>
          </div>
        ) : (
          vendors.map((vendor, idx) => (
            <div className="table-row" key={vendor.id}>
              <div>{idx + 1}</div>
              <div>{vendor.business_name}</div>
              <div>{vendor.phone_number}</div>
              <div>{vendor.address}</div>
              <div className="action-buttons">
                <button className="btn update" onClick={() => handleUpdate(vendor)}>Update</button>
                <button className="btn delete" onClick={() => handleDelete(vendor.id)}>Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ListVendor;
