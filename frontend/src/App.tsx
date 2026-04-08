import './App.css'
import { BrowserRouter, Routes, Route, Outlet, Navigate, useLocation, useNavigate } from 'react-router-dom';
import LoginPage from './components/login_page';
import RegisterPage from './components/register_page';
import DashboardPage from './components/dashboard_page';
import { AuthProvider, useAuth } from './context/AuthContext';

function ProtectedRoute() {
  const { userId, isLoading } = useAuth();
  if (isLoading) return null;
  return userId ? <Outlet /> : <Navigate to="/login" replace />;
}

function GuestOnlyRoute() {
  const { userId, isLoading } = useAuth();
  if (isLoading) return null;
  return userId ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

function IndexRedirect() {
  const { userId, isLoading } = useAuth();
  if (isLoading) return null;
  return <Navigate to={userId ? '/dashboard' : '/login'} replace />;
}

function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  async function handleLogout() {
    await logout();
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
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<IndexRedirect />} />
            <Route element={<GuestOnlyRoute />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
