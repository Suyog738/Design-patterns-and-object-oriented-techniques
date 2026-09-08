import { Link, Outlet } from "react-router-dom";
import HealthStatus from "./HealthStatus";

export default function AppLayout() {
  return (
    <div className="min-h-screen">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold text-emerald-700">
              Smart Greenhouse
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <nav className="flex gap-4">
              <Link
                to="/"
                className="text-slate-600 hover:text-emerald-600"
              >
                Home
              </Link>

              <Link
                to="/dashboard"
                className="text-slate-600 hover:text-emerald-600"
              >
                Dashboard
              </Link>
            </nav>

            <HealthStatus />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}