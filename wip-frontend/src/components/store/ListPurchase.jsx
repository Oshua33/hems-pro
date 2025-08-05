import React, { useEffect, useState } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./ListPurchase.css";

const ListPurchase = () => {
  const [purchases, setPurchases] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalEntries, setTotalEntries] = useState(0);
  const [totalPurchase, setTotalPurchase] = useState(0);

  const [editingPurchase, setEditingPurchase] = useState(null); // For Edit form
  const [attachmentFile, setAttachmentFile] = useState(null); // File upload

  // Don't fetch anything on initial load
// User must click "Search" to load data


  const fetchPurchases = async () => {
    setLoading(true);
    setError("");
    try {
      const axios = axiosWithAuth();
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (invoiceNumber) params.invoice_number = invoiceNumber;

      const response = await axios.get("/store/purchases", { params });
      const { purchases, total_entries, total_purchase } = response.data;

      setPurchases(purchases || []);
      setTotalEntries(total_entries || 0);
      setTotalPurchase(total_purchase || 0);
    } catch (err) {
      setError("Failed to fetch purchases");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this purchase?")) return;
    try {
      const axios = axiosWithAuth();
      await axios.delete(`/store/purchases/${id}`);
      fetchPurchases();
    } catch (err) {
      alert("Failed to delete purchase");
    }
  };

  const handleEditClick = (purchase) => {
    setEditingPurchase({ ...purchase });
    setAttachmentFile(null);
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditingPurchase((prev) => ({ ...prev, [name]: value }));
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!editingPurchase) return;

    try {
        const axios = axiosWithAuth();
        const formData = new FormData();

        formData.append("item_id", parseInt(editingPurchase.item_id));
        formData.append("item_name", editingPurchase.item_name);
        formData.append("invoice_number", editingPurchase.invoice_number);
        formData.append("quantity", parseFloat(editingPurchase.quantity));
        formData.append("unit_price", parseFloat(editingPurchase.unit_price));
        formData.append("vendor_id", editingPurchase.vendor_id ? parseInt(editingPurchase.vendor_id) : "");
        
        // Important: Format to valid ISO string for datetime-local input
        const formattedDate = new Date(editingPurchase.purchase_date).toISOString();
        formData.append("purchase_date", formattedDate);

        if (attachmentFile) {
        formData.append("attachment", attachmentFile);
        }

        await axios.put(`/store/purchases/${editingPurchase.id}`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
        });

        setEditingPurchase(null);
        fetchPurchases();
    } catch (err) {
        alert("Failed to update purchase");
        console.error(err.response?.data || err.message);
    }
    };



  return (
    <div className="list-purchase-container">
      <h2>List Purchases</h2>

      <div className="filters">
        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        <input type="text" value={invoiceNumber} onChange={(e) => setInvoiceNumber(e.target.value)} placeholder="Invoice number" />
        <button onClick={fetchPurchases}>Search</button>
      </div>

      <div className="summary">
        <p><strong>Total Entries:</strong> {totalEntries}</p>
        <p><strong>Total Purchase:</strong> ₦{totalPurchase.toLocaleString()}</p>
      </div>


    {/* ✅ Edit Form - Now in the DOM tree */}
    {editingPurchase && (
      <form className="edit-form" onSubmit={handleEditSubmit}>
        <h3>Edit Purchase</h3>
        <input name="item_name" value={editingPurchase.item_name} onChange={handleEditChange} placeholder="Item Name" />
        <input name="item_id" value={editingPurchase.item_id} onChange={handleEditChange} placeholder="Item ID" />
        <input name="invoice_number" value={editingPurchase.invoice_number} onChange={handleEditChange} placeholder="Invoice #" />
        <input name="quantity" type="number" value={editingPurchase.quantity} onChange={handleEditChange} placeholder="Quantity" />
        <input name="unit_price" type="number" value={editingPurchase.unit_price} onChange={handleEditChange} placeholder="Unit Price" />
        <input name="vendor_id" value={editingPurchase.vendor_id || ""} onChange={handleEditChange} placeholder="Vendor ID" />
        <input
          name="purchase_date"
          type="datetime-local"
          value={editingPurchase.purchase_date}
          onChange={handleEditChange}
        />
        <input type="file" onChange={(e) => setAttachmentFile(e.target.files[0])} />

        <button type="submit">Update Purchase</button>
        <button type="button" className="cancel-btn" onClick={() => setEditingPurchase(null)}>Cancel</button>
      </form>
    )}


      {loading ? (
        <p>Loading purchases...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : (
        <table className="purchase-table">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Item</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
              <th>Vendor</th>
              <th>Purchase Date</th>
              <th>Created By</th>
              <th>Attachment</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {purchases.length === 0 ? (
              <tr>
                <td colSpan="10">No purchases found.</td>
              </tr>
            ) : (
              purchases.map((purchase) => (
                <tr key={purchase.id}> 
                  <td>{purchase.invoice_number}</td>
                  <td>{purchase.item_name}</td>
                  <td>{purchase.quantity}</td>
                  <td>{purchase.unit_price}</td>
                  <td>{purchase.total_amount}</td>
                  <td>{purchase.vendor_name}</td>
                  <td>{new Date(purchase.purchase_date).toLocaleDateString()}</td>
                  <td>{purchase.created_by}</td>
                  <td>
                    {purchase.attachment_url ? (
                      <a href={purchase.attachment_url} target="_blank" rel="noopener noreferrer">View Invoice</a>
                    ) : "-"}
                  </td>
                  <td>
                    <button className="edit-btn" onClick={() => handleEditClick(purchase)}>Edit</button>
                    <button className="delete-btn" onClick={() => handleDelete(purchase.id)}>Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}

      
    </div>
  );
};

export default ListPurchase;
