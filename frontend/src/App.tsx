import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Scans from './pages/Scans';
import ScanDetails from './pages/ScanDetails';
import GraphExplorer from './pages/GraphExplorer';
import IOCViewer from './pages/IOCViewer';
import EntityViewer from './pages/EntityViewer';
import AIChat from './pages/AIChat';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="scans" element={<Scans />} />
        <Route path="scans/:scanId" element={<ScanDetails />} />
        <Route path="graph" element={<GraphExplorer />} />
        <Route path="iocs" element={<IOCViewer />} />
        <Route path="entities" element={<EntityViewer />} />
        <Route path="chat" element={<AIChat />} />
      </Route>
    </Routes>
  );
}

export default App;
