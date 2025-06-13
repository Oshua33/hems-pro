// LicenseGenerator.jsx
import React, { useState } from "react";
import { generateLicense } from "../api/licenseApi";

const LicenseGenerator = () => {
  const [adminPassword, setAdminPassword] = useState("");
  const [licenseKey, setLicenseKey] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    try {
      setError("");
      const response = await generateLicense(adminPassword, licenseKey);
      setResult(response);
    } catch (err) {
      setResult(null);
      setError(err?.message || "Something went wrong");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Generate License Key</h2>

      <div>
        <label>Admin Password:</label>
        <input
          type="password"
          value={adminPassword}
          onChange={(e) => setAdminPassword(e.target.value)}
        />
      </div>

      <div>
        <label>License Key:</label>
        <input
          type="text"
          value={licenseKey}
          onChange={(e) => setLicenseKey(e.target.value)}
        />
      </div>

      <button onClick={handleGenerate}>Generate</button>

      {result && (
        <div style={{ marginTop: 10, color: "green" }}>
          ✅ License generated: {result.key}
        </div>
      )}
      {error && (
        <div style={{ marginTop: 10, color: "red" }}>
          ❌ {error}
        </div>
      )}
    </div>
  );
};

export default LicenseGenerator;
