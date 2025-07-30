import React, { useState } from "react";
import { useNavigate, Outlet } from "react-router-dom";
import { FaFileExcel, FaPrint } from "react-icons/fa";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import ExcelJS from "exceljs";
import "./StoreDashboardPage.css";



const StoreDashboardPage = () => {
  const navigate = useNavigate();

  const exportToExcel = async () => {
    const table = document.querySelector(".content-area table");
    if (!table) return alert("No table found to export.");

    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet("Store Data");

    const headers = Array.from(table.querySelectorAll("thead th")).map((th) =>
      th.innerText.trim()
    );
    const colCount = headers.length;

    // Title
    sheet.mergeCells(1, 1, 1, colCount);
    const titleCell = sheet.getCell("A1");
    titleCell.value = "Store Report";
    titleCell.font = { size: 14, bold: true };
    titleCell.alignment = { vertical: "middle", horizontal: "center" };

    sheet.addRow(headers).font = { bold: true };

    const rows = Array.from(table.querySelectorAll("tbody tr")).map((tr) =>
      Array.from(tr.querySelectorAll("td")).map((td) => td.innerText.trim())
    );
    rows.forEach((row) => sheet.addRow(row));
    sheet.eachRow((row) => {
      row.eachCell((cell) => {
        cell.border = {
          top: { style: "thin" },
          left: { style: "thin" },
          bottom: { style: "thin" },
          right: { style: "thin" },
        };
        cell.alignment = { vertical: "middle", horizontal: "left" };
      });
    });

    sheet.columns.forEach((col) => {
      let maxLength = 10;
      col.eachCell({ includeEmpty: true }, (cell) => {
        const val = cell.value ? cell.value.toString() : "";
        maxLength = Math.max(maxLength, val.length);
      });
      col.width = maxLength + 2;
    });

    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    saveAs(blob, `store_report.xlsx`);
  };

  const printContent = () => {
    const content = document.querySelector(".content-area");
    if (!content) return;
    const printWindow = window.open("", "_blank");
    printWindow.document.write("<html><head><title>Print</title></head><body>");
    printWindow.document.write(content.innerHTML);
    printWindow.document.write("</body></html>");
    printWindow.document.close();
    printWindow.print();
  };

  const storeMenu = [
    { name: "📂 Drinks Category", submenu: [
      { label: "➕ New Category", path: "/dashboard/store/category/create" },
      { label: "📃 List Category", path: "/dashboard/store/category/list" },
      
    ]},
    { name: "📦 Items", submenu: [
      { label: "➕ Add Item", path: "/dashboard/store/items/create" },
      { label: "📃 Item List", path: "/dashboard/store/items/list" },
      
    ]},
    { name: "🛒 Purchase", submenu: [
      { label: "➕ New Purchase", path: "/dashboard/store/purchase/create" },
      { label: "📃 List Purchase", path: "/dashboard/store/purchase/list" },
      
    ]},
    { name: "🍶 Issue to Bar", submenu: [
      { label: "📤 Issue Items", path: "/dashboard/store/issue/create" },
      { label: "📃 Issued List", path: "/dashboard/store/issue/list" },
      
    ]},
    { name: "⚖️ Stock Adjustment", submenu: [
      { label: "🔧 Adjust Stock", path: "/dashboard/store/adjustment/create" },
      
    ]},
    { name: "📊 Stock Balance", path: "/dashboard/store/stock-balance" },
    
    { name: "🏭 Vendor", submenu: [
      { label: "➕ Add Vendor", path: "/dashboard/store/vendor/create" },
      { label: "📃 Vendor List", path: "/dashboard/store/vendor/list" },
      
    ]},
  ];

  const [hovered, setHovered] = useState("");

  return (
    <div className="dashboard-container">
      <aside className="sidebars1">
        <h2 className="sidebar-title">STORE MENU</h2>
        <nav>
          {storeMenu.map((item) => (
            <div
              key={item.name}
              className="sidebar-item-wrapper"
              onMouseEnter={() => setHovered(item.name)}
              onMouseLeave={() => setHovered("")}
            >
              <button
                className={`sidebars1-button ${hovered === item.name ? "active" : ""}`}
                onClick={() => {
                  if (!item.submenu) navigate(item.path);
                }}
              >
                {item.name}
              </button>
              {item.submenu && hovered === item.name && (
                <div className="submenu">
                  {item.submenu.map((sub) => (
                    <button
                      key={sub.path}
                      className="submenu-item"
                      onClick={() => {
                        navigate(sub.path);
                        setHovered("");
                      }}
                    >
                      {sub.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </aside>


      <main className="main-content">
        <header className="header" style={{ gap: "20px" }}>
          <h1 className="header-title" style={{ flexGrow: 1 }}>
            🏪 Store Management Dashboard
          </h1>
          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={exportToExcel} className="action-button1">
              <FaFileExcel style={{ marginRight: "5px" }} />
              Export to Excel
            </button>
            <button onClick={printContent} className="action-button1">
              <FaPrint style={{ marginRight: "5px" }} />
              Print
            </button>
            <button onClick={() => navigate("/logout")} className="logout-button1">
              🚪 Logout
            </button>
          </div>
        </header>


        <section className="content-area">
          <Outlet />
        </section>
      </main>
    </div>
  );
};

export default StoreDashboardPage;
