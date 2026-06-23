import { Outlet } from "react-router-dom";
import { Sidebar, Navbar } from "./Navbar";
import OfflineBanner from "./OfflineBanner";
import ApiVersionBanner from "./ApiVersionBanner";
import ToastContainer from "./Toast";

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col lg:pl-64">
        <OfflineBanner />
        <ApiVersionBanner />
        <Navbar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  );
}
