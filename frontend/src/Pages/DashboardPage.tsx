import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensors,
  type Sensor,
} from "../services/api";

const sections = [
  {
    id: "config",
    title: "Configuration",
  },
  {
    id: "automation",
    title: "Automation",
  },
  {
    id: "overview",
    title: "Overview",
  },
  {
    id: "controls",
    title: "Controls",
  },
  {
    id: "events",
    title: "Events",
  },
];

export default function DashboardPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadSensors() {
      try {
        const data = await fetchSensors();

        if (!cancelled) {
          setSensors(data);
          setError("");
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load sensors.");
          setLoading(false);
        }
      }
    }

    loadSensors();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleCreateSensor(
    type: "moisture" | "light",
    displayName: string
  ) {
    try {
      setCreating(true);
      setError("");

      await createSensor(type, displayName);

      const data = await fetchSensors();
      setSensors(data);
    } catch {
      setError("Failed to create sensor.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="mt-2 text-slate-600">
          Smart Greenhouse monitoring and control dashboard.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Sensors */}
        <section
          id="sensors"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Sensors
          </h3>

          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="button"
              disabled={creating}
              onClick={() =>
                handleCreateSensor(
                  "moisture",
                  "Greenhouse Moisture Sensor"
                )
              }
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Add Moisture Sensor
            </button>

            <button
              type="button"
              disabled={creating}
              onClick={() =>
                handleCreateSensor(
                  "light",
                  "Greenhouse Light Sensor"
                )
              }
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Add Light Sensor
            </button>
          </div>

          {loading && (
            <p className="mt-4 text-sm text-slate-500">
              Loading sensors...
            </p>
          )}

          {error && (
            <p className="mt-4 text-sm text-red-500">
              {error}
            </p>
          )}

          {!loading && !error && sensors.length === 0 && (
            <p className="mt-4 text-sm text-slate-500">
              No sensors found.
            </p>
          )}

          {!loading && !error && sensors.length > 0 && (
            <div className="mt-5 space-y-3">
              {sensors.map((sensor) => (
                <div
                  key={sensor.id}
                  className="rounded-lg border bg-slate-50 p-4"
                >
                  <p className="font-medium text-slate-900">
                    {sensor.display_name || "Unnamed sensor"}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Type: {sensor.device_type}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    ID: {sensor.id}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Other sections */}
        {sections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-emerald-700">
              {section.title}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Placeholder for the {section.title.toLowerCase()} section.
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}