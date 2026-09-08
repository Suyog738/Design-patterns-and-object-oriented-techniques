import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "../services/api";

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setError(false);
      })
      .catch(() => {
        setError(true);
      });
  }, []);

  if (error) {
    return (
      <span className="rounded-full border border-red-300 bg-red-50 px-3 py-1 text-sm text-red-700">
        API: unreachable
      </span>
    );
  }

  if (!health) {
    return (
      <span className="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-sm text-amber-700">
        Checking...
      </span>
    );
  }

  const healthy = health.status === "ok" && health.db === "ok";

  return (
    <span
      className={`rounded-full border px-3 py-1 text-sm ${
        healthy
          ? "border-emerald-300 bg-emerald-50 text-emerald-700"
          : "border-red-300 bg-red-50 text-red-700"
      }`}
    >
      API: {health.status} · DB: {health.db}
    </span>
  );
}