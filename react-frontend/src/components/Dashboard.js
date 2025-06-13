import React, { useState } from "react";
import UserManagement from "./UserManagement";

const Dashboard = ({ token }) => {
  const [showUserManagement, setShowUserManagement] = useState(false);

  return (
    <div>
      <button onClick={() => setShowUserManagement(true)}>Open User Management</button>

      {showUserManagement && (
        <UserManagement
          token={token}
          onClose={() => setShowUserManagement(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
