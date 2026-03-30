import './App.css'
import { BrowserRouter, Routes, Route, Outlet, Navigate, useLocation, useNavigate } from 'react-router-dom';
import LoginPage from './components/login_page';
import RegisterPage from './components/register_page';
import DashboardPage from './components/dashboard_page';

function isAuthenticated() {
  return !!localStorage.getItem('token');
}

function ProtectedRoute() {
  return isAuthenticated() ? <Outlet /> : <Navigate to="/login" replace />;
}

function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  const headerAction = location.pathname === '/login' ? (
    <button onClick={() => navigate('/register')}>Register</button>
  ) : location.pathname === '/register' ? (
    <button onClick={() => navigate('/login')}>Login</button>
  ) : location.pathname === '/dashboard' ? (
    <button onClick={handleLogout}>Log out</button>
  ) : null;

  return (
    <>
      <header className="flex justify-between items-center">
        <h1>My Demo Project</h1>
        {headerAction}
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}