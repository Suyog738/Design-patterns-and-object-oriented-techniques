import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import DashboardPage from "./Pages/DashboardPage";

function HomePage() {
  return (
    <div>
      <h2 className="text-3xl font-bold text-emerald-600">
        Smart Greenhouse
      </h2>

      <p className="mt-3 text-slate-600">
        Welcome to the Smart Greenhouse system.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}