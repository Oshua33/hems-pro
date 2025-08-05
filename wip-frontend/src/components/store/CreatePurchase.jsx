import React, { useEffect, useState } from "react";
import axiosWithAuth from "../../utils/axiosWithAuth";
import "./CreatePurchase.css";

const CreatePurchase = () => {
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [rows, setRows] = useState([
    { categoryId: "", itemId: "", quantity: "", unitPrice: "", total: 0 },
  ]);
  const [vendorId, setVendorId] = useState("");
  const [purchaseDate, setPurchaseDate] = useState("");
  const [attachment, setAttachment] = useState(null);
  const [message, setMessage] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");


  useEffect(() => {
    fetchVendors();
    fetchCategories();
    fetchItems();
  }, []);

  const fetchVendors = async () => {
    try {
      const axios = axiosWithAuth();
      const response = await axios.get("/vendor/");
      const data = response.data;

      if (Array.isArray(data)) {
        setVendors(data);
      } else if (Array.isArray(data.vendors)) {
        setVendors(data.vendors);
      } else {
        console.error("Expected vendors array but got:", data);
        setVendors([]);
      }
    } catch (error) {
      console.error("Failed to fetch vendors:", error);
      setVendors([]);
    }
  };

  const fetchCategories = async () => {
    try {
      const axios = axiosWithAuth();
      const response = await axios.get("/store/categories");
      const data = response.data;

      if (Array.isArray(data)) {
        setCategories(data);
      } else if (Array.isArray(data.categories)) {
        setCategories(data.categories);
      } else {
        console.error("Expected categories array but got:", data);
        setCategories([]);
      }
    } catch (error) {
      console.error("Failed to fetch categories:", error);
      setCategories([]);
    }
  };

  const fetchItems = async () => {
    try {
      const axios = axiosWithAuth();
      const response = await axios.get("/store/items/simple");
      const data = response.data;

      if (Array.isArray(data)) {
        setItems(data);
      } else if (Array.isArray(data.items)) {
        setItems(data.items);
      } else {
        console.error("Expected items array but got:", data);
        setItems([]);
      }
    } catch (error) {
      console.error("Failed to fetch items:", error);
      setItems([]);
    }
  };

  const handleRowChange = (index, field, value) => {
    const updatedRows = [...rows];
    updatedRows[index][field] = value;

    const quantity = parseFloat(updatedRows[index].quantity) || 0;
    const unitPrice = parseFloat(updatedRows[index].unitPrice) || 0;
    updatedRows[index].total = quantity * unitPrice;

    setRows(updatedRows);
  };

  const addRow = () => {
    setRows([
      ...rows,
      { categoryId: "", itemId: "",  quantity: "", unitPrice: "", total: 0 },
    ]);
  };

  const removeRow = (index) => {
    setRows(rows.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const axios = axiosWithAuth();

      for (const row of rows) {
        const item = items.find((i) => i.id === parseInt(row.itemId));
        if (!item) continue;

        const formData = new FormData();
        formData.append("item_id", String(item.id));
        formData.append("item_name", item.name);
        formData.append("invoice_number", invoiceNumber);
        formData.append("quantity", String(row.quantity));
        formData.append("unit_price", String(row.unitPrice));
        formData.append("vendor_id", String(vendorId));
        formData.append("purchase_date", new Date(purchaseDate).toISOString());


        if (attachment) {
          formData.append("attachment", attachment);
        }

        console.log("FormData being sent:");
        for (let [key, val] of formData.entries()) {
          console.log(`${key}: ${val}`);
        }

        await axios.post("/store/purchases", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }


      setMessage("✅ Purchase saved successfully.");
      setRows([{ categoryId: "", itemId: "", quantity: "", unitPrice: "", total: 0 }]);
      setVendorId("");
      setPurchaseDate("");
      setAttachment(null);
    } catch (err) {
      const detail =
        err.response?.data?.detail || "❌ Failed to save purchase.";
      console.error("Error:", err);
      setMessage(detail);
    }
  };

  return (
    <div className="create-purchase-container">
      <h2>Add New Purchase</h2>
      <form onSubmit={handleSubmit} className="purchase-form">
        <div className="form-group">
          <label>Vendor</label>
          <select
            value={vendorId}
            onChange={(e) => setVendorId(e.target.value)}
            required
          >
            <option value="">Select Vendor</option>
            {vendors.map((vendor) => (
              <option key={vendor.id} value={vendor.id}>
                {vendor.business_name || vendor.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Purchase Date</label>
          <input
            type="date"
            value={purchaseDate}
            onChange={(e) => setPurchaseDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Invoice Number</label>
          <input
            type="text"
            value={invoiceNumber}
            onChange={(e) => setInvoiceNumber(e.target.value)}
            required
          />
        </div>


        


        <div className="form-group">
          <label>Attachment (optional)</label>
          <input
            type="file"
            onChange={(e) => setAttachment(e.target.files[0])}
          />
        </div>

        <div className="rows-container">
          {rows.map((row, index) => (
            <div key={index} className="row-entry">
              <div>
                <label>Category</label>
                <select
                  value={row.categoryId}
                  onChange={(e) =>
                    handleRowChange(index, "categoryId", e.target.value)
                  }
                >
                  <option value="">Select</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Item</label>
                <select
                  value={row.itemId}
                  onChange={(e) => handleRowChange(index, "itemId", e.target.value)}
                >
                  <option value="">Select</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>

              

              <div>
                <label>Quantity</label>
                <input
                  type="number"
                  value={row.quantity}
                  onChange={(e) =>
                    handleRowChange(index, "quantity", e.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label>Unit Price</label>
                <input
                  type="number"
                  value={row.unitPrice}
                  onChange={(e) =>
                    handleRowChange(index, "unitPrice", e.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label>Total</label>
                <input type="number" value={row.total} readOnly />
              </div>

              <div>
                <button type="button" onClick={() => removeRow(index)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>



        <button type="button" onClick={addRow} className="add-row-btn">
          + Add Item
        </button>

        <button type="submit" className="submit-button">
          Add Purchase
        </button>

        {message && <p className="message">{message}</p>}
      </form>
    </div>
  );
};

export default CreatePurchase;