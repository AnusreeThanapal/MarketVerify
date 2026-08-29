import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
  useLocation,
} from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/layout/Header';
import { StatusBar } from './components/layout/StatusBar';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { WelcomeView } from './views/WelcomeView';
import { LoginView } from './views/LoginView';
import { SubmitClaimView } from './views/SubmitClaimView';
import { LiveTraceView } from './views/LiveTraceView';
import { DashboardView } from './views/DashboardView';
import { SourceHistoryView } from './views/SourceHistoryView';
import { DataExplorerView } from './views/DataExplorerView';

/**
 * Public route wrapper for the Welcome Landing Page at "/"
 * If authenticated, redirects to Dashboard/Verify.
 */
const PublicWelcomeRoute: React.FC = () => {
  const { isAuthenticated, isLoading, role } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to={role === 'AUDITOR' ? '/claims' : '/verify'} replace />;
  }

  return (
    <ErrorBoundary>
      <WelcomeView />
    </ErrorBoundary>
  );
};

/**
 * Public route wrapper for Login at "/login"
 * If authenticated, redirects to Dashboard/Verify.
 */
const PublicLoginRoute: React.FC = () => {
  const { isAuthenticated, isLoading, role } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to={role === 'AUDITOR' ? '/claims' : '/verify'} replace />;
  }

  return (
    <ErrorBoundary>
      <LoginView />
    </ErrorBoundary>
  );
};

/**
 * Protected Full-Screen Workstation Layout with ErrorBoundary
 */
const AuthenticatedLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="h-screen w-screen bg-[#F7F8FA] flex items-center justify-center font-mono text-xs text-[#0F2744]">
        <div className="flex items-center gap-2.5 p-4 rounded-portal bg-white border border-[#CBD5E1] shadow-portal-card">
          <span className="w-2.5 h-2.5 rounded-full bg-[#1B3A6B] animate-ping" />
          <span>Verifying Surveillance Session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const isTraceActive = location.pathname.startsWith('/trace/');

  return (
    <div className="h-screen w-screen flex flex-col bg-[#F7F8FA] overflow-hidden text-[#1E293B]">
      {/* Top Workstation Masthead */}
      <Header hasActiveClaim={isTraceActive} />

      {/* Central Full-Screen Surveillance Workspace with ErrorBoundary */}
      <main className="flex-1 overflow-y-auto p-4 sm:p-5">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>

      {/* Fixed Bottom Surveillance Status Bar */}
      <StatusBar />
    </div>
  );
};

/**
 * Guard for Data Explorer
 */
const DataExplorerGuard: React.FC = () => {
  const { role } = useAuth();
  const isAdminOrAuditor = role === 'ADMINISTRATOR' || role === 'AUDITOR';
  if (!isAdminOrAuditor) {
    return <Navigate to="/claims" replace />;
  }
  return <DataExplorerView />;
};

/**
 * Guard for Verify Claim
 */
const VerifyClaimGuard: React.FC = () => {
  const { role } = useAuth();
  if (role === 'AUDITOR') {
    return <Navigate to="/claims" replace />;
  }
  return <SubmitClaimView />;
};

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Welcome Landing Page */}
            <Route path="/" element={<PublicWelcomeRoute />} />

            {/* Public Login Route */}
            <Route path="/login" element={<PublicLoginRoute />} />

            {/* Authenticated Surveillance Desk Routes */}
            <Route element={<AuthenticatedLayout />}>
              <Route path="/verify" element={<VerifyClaimGuard />} />
              <Route path="/claims" element={<DashboardView />} />
              <Route path="/trace" element={<LiveTraceView />} />
              <Route path="/trace/:claimId" element={<LiveTraceView />} />
              <Route path="/sources" element={<SourceHistoryView />} />
              <Route path="/data-explorer" element={<DataExplorerGuard />} />
            </Route>

            {/* Fallback to Root */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
