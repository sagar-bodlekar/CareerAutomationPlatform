import { Outlet } from "react-router-dom";
import { Sidebar, Navbar } from "./Navbar";
import OfflineBanner from "./OfflineBanner";

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col lg:pl-64">
        <OfflineBanner />
        <Navbar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
