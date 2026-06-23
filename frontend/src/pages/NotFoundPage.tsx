import { Link } from "react-router-dom";
import { Home, ArrowLeft, FileQuestion } from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export default function NotFoundPage() {
  useDocumentTitle("Page Not Found");
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-amber-100">
            <FileQuestion className="h-10 w-10 text-amber-600" />
          </div>
        </div>

        <h1 className="text-6xl font-bold text-gray-900">404</h1>
        <p className="mt-2 text-xl font-semibold text-gray-700">Page not found</p>
        <p className="mt-2 text-sm text-gray-500">
          The page you're looking for doesn't exist or has been moved.
        </p>

        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            to="/"
            className="flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 transition-colors"
          >
            <Home className="h-4 w-4" />
            Go to Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </button>
        </div>

        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-400">
            Try these pages
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            <Link to="/profile" className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 transition-colors">
              Profile
            </Link>
            <Link to="/jobs" className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 transition-colors">
              Browse Jobs
            </Link>
            <Link to="/resumes" className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 transition-colors">
              Resumes
            </Link>
            <Link to="/applications" className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 transition-colors">
              Applications
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
