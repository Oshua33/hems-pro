// --- src/components/Auth/AuthPage.jsx ---
import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

export default function AuthPage() {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <div className="flex min-h-screen justify-center items-center bg-muted">
      {showRegister ? (
        <RegisterForm switchToLogin={() => setShowRegister(false)} />
      ) : (
        <LoginForm switchToRegister={() => setShowRegister(true)} />
      )}
    </div>
  );
}
