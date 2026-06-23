import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import AppErrorBoundary from "./components/common/AppErrorBoundary";
import SavingIndicator from "./components/common/SavingIndicator";
import Layout from "./components/common/Layout";
import ProtectedRoute from "./components/common/ProtectedRoute";

// Route-based code splitting — each page is a separate chunk
const LoginPage = lazy(() => import("./pages/LoginPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const ProfileEditPage = lazy(() => import("./pages/ProfileEditPage"));
const SkillsPage = lazy(() => import("./pages/SkillsPage"));
const ProfileManagePage = lazy(() => import("./pages/ProfileManagePage"));
const JobsPage = lazy(() => import("./pages/JobsPage"));
const JobDetailPage = lazy(() => import("./pages/JobDetailPage"));
const ResumesPage = lazy(() => import("./pages/ResumesPage"));
const ResumeDetailPage = lazy(() => import("./pages/ResumeDetailPage"));
const ResumeGeneratePage = lazy(() => import("./pages/ResumeGeneratePage"));
const ApplicationsPage = lazy(() => import("./pages/ApplicationsPage"));
const ApplicationDetailPage = lazy(() => import("./pages/ApplicationDetailPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const TrackingPage = lazy(() => import("./pages/TrackingPage"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));
const NotificationsPage = lazy(() => import("./pages/NotificationsPage"));

/** Minimal page-level loading fallback shown during chunk load */
function PageFallback() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
        <p className="text-sm text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AppErrorBoundary>
      <Suspense fallback={<PageFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/profile/edit" element={<ProfileEditPage />} />
            <Route path="/profile/skills" element={<SkillsPage />} />
            <Route path="/profile/manage" element={<ProfileManagePage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:id" element={<JobDetailPage />} />
            <Route path="/resumes" element={<ResumesPage />} />
            <Route path="/resumes/:id" element={<ResumeDetailPage />} />
            <Route path="/resumes/generate" element={<ResumeGeneratePage />} />
            <Route path="/applications" element={<ApplicationsPage />} />
            <Route path="/applications/:id" element={<ApplicationDetailPage />} />
            <Route path="/tracking" element={<TrackingPage />} />
            <Route path="/tracking/analytics" element={<AnalyticsPage />} />
            <Route path="/tracking/notifications" element={<NotificationsPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
      <SavingIndicator />
    </AppErrorBoundary>
  );
}
