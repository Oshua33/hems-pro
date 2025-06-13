import { useNavigate } from 'react-router-dom';

export default function Sidebar({ userRole }) {
  const navigate = useNavigate();

  const menu = [
    { name: "👤 Users", path: "/users", adminOnly: true },
    { name: "🏨 Rooms", path: "/rooms" },
    { name: "📅 Bookings", path: "/bookings" },
    { name: "💳 Payments", path: "/payments" },
    { name: "🎉 Events", path: "/events" },
  ];

  return (
    <div className="bg-slate-700 text-white w-60 p-4">
      <h2 className="text-lg font-bold mb-4">MENU</h2>
      {menu.map(item =>
        (!item.adminOnly || userRole === "admin") && (
          <button key={item.path}
            onClick={() => navigate(item.path)}
            className="w-full text-left p-2 rounded hover:bg-teal-500"
          >
            {item.name}
          </button>
        )
      )}
      <button
        onClick={() => navigate('/reservation-alert')}
        className="w-full mt-4 bg-red-600 hover:bg-red-700 p-2 rounded"
      >
        🔔 Reservation
      </button>
      <button
        onClick={() => navigate('/logout')}
        className="w-full mt-2 bg-red-900 p-2 rounded"
      >
        🚪 Logout
      </button>
    </div>
  );
}
