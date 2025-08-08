import React, { useState } from "react";
import { useNavigate, Outlet } from "react-router-dom";
import { FaFileExcel, FaPrint } from "react-icons/fa";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import ExcelJS from "exceljs";
import "./BarDashboardPage.css"; // ✅ reuse Store CSS for consistent look

const BarDashboardPage = () => {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState("");

  const exportToExcel = async () => {
    const table = document.querySelector(".content-area table");
    if (!table) return alert("No table found to export.");

    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet("Bar Data");

    const headers = Array.from(table.querySelectorAll("thead th")).map((th) =>
      th.innerText.trim()
    );
    const colCount = headers.length;

    sheet.mergeCells(1, 1, 1, colCount);
    const titleCell = sheet.getCell("A1");
    titleCell.value = "Bar Report";
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
    saveAs(blob, `bar_report.xlsx`);
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

  const barMenu = [
    {
        name: "🍾 Bar Outlet",
        path: "/dashboard/bar/list"

    },
    {
        name: "📥 Receive Stock",
        submenu: [
        { label: "➕ Enter Stock", path: "/dashboard/bar/stock/create" },
        { label: "📃 List Stock", path: "/dashboard/bar/stock/list" },
        ],
    },
    {
        name: "🛍️ Bar Sales",
        submenu: [
        { label: "➕ Create Sales", path: "/dashboard/bar/sales/create" },
        { label: "📃 List Sales", path: "/dashboard/bar/sales/list" },
        ],
    },
    {
        name: "💳 Bar Payment",
        submenu: [
        { label: "➕ Create Payment", path: "/dashboard/bar/payment/create" },
        { label: "📃 List Payment", path: "/dashboard/bar/payment/list" },
        { label: "❌ Void Payment", path: "/dashboard/bar/payment/void" },
        ],
    },
    {
        name: "📊 Stock Balance",
        path: "/dashboard/bar/stock-balance",
    },
    {
        name: "🛠️ Stock Adjustment",
        submenu: [
        { label: "🔧 Adjust Stock", path: "/dashboard/bar/adjustment/create" },
        { label: "📃 List Adjustment", path: "/dashboard/bar/adjustment/list" },
        ],
    },
    {
        name: "💲 Set Price",
        path: "/dashboard/bar/price",
    },
    {
        name: "🏪 Store Issues Control",
        path: "/dashboard/bar/store-issues",
    },
];

  return (
    <div className="dashboard-container">
      <aside className="sidebars1">
        <h2 className="sidebar-title">BAR MENU</h2>
        <nav>
          {barMenu.map((item) => (
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
            🍷 Bar Management Dashboard
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

export default BarDashboardPage;
