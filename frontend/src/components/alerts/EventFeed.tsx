import { useEffect, useState } from "react";
import {
  fetchAlerts,
  fetchLocationConfig,
  fetchLocations,
  type AlertDto,
  type LocationDto,
  type ZoneDto,
} from "../../services/api";

const POLL_MS = 5000;

const SEVERITY_STYLES: Record<string, string> = {
  info: "bg-slate-100 text-slate-700",
  warning: "bg-amber-100 text-amber-800",
  critical: "bg-red-100 text-red-700",
};

export default function EventFeed() {
  const [alerts, setAlerts] = useState<AlertDto[]>([]);
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [zones, setZones] = useState<ZoneDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [zoneId, setZoneId] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");

  // Load locations once.
  useEffect(() => {
    let cancelled = false;

    fetchLocations()
      .then((data) => {
        if (!cancelled) setLocations(data);
      })
      .catch(() => {
        // Filters are optional; the feed still works without them.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load zones whenever a location is chosen.
  useEffect(() => {
    if (!locationId) return;

    let cancelled = false;

    fetchLocationConfig(locationId)
      .then((config) => {
        if (!cancelled) setZones(config.zones);
      })
      .catch(() => {
        if (!cancelled) setZones([]);
      });

    return () => {
      cancelled = true;
    };
  }, [locationId]);

  // Poll alerts every 5 seconds (Phase 12 replaces this with WebSocket).
  useEffect(() => {
    let cancelled = false;

    const poll = () => {
      fetchAlerts({
        status: "active",
        locationId: locationId || undefined,
        zoneId: zoneId || undefined,
        limit: 50,
      })
        .then((rows) => {
          if (cancelled) return;
          setAlerts(rows);
          setError("");
          setLoaded(true);
        })
        .catch((err) => {
          if (cancelled) return;
          setError(
            err instanceof Error ? err.message : "Failed to load alerts.",
          );
          setLoaded(true);
        });
    };

    poll();
    const intervalId = window.setInterval(poll, POLL_MS);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [locationId, zoneId]);

  function handleLocationChange(value: string) {
    setLocationId(value);
    setZoneId("");
    setZones([]);
  }

  function zoneName(id: string | null): string {
    if (!id) return "—";
    return zones.find((z) => z.id === id)?.name ?? `${id.slice(0, 8)}…`;
  }

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-emerald-700">Events</h3>
          <p className="mt-1 text-sm text-slate-500">
            Active alerts from the event bus. Refreshes every 5 seconds.
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label
            htmlFor="events-location"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Location
          </label>
          <select
            id="events-location"
            value={locationId}
            onChange={(e) => handleLocationChange(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          >
            <option value="">All locations</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="events-zone"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Zone
          </label>
          <select
            id="events-zone"
            value={zoneId}
            onChange={(e) => setZoneId(e.target.value)}
            disabled={!locationId}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
          >
            <option value="">All zones</option>
            {zones.map((zone) => (
              <option key={zone.id} value={zone.id}>
                {zone.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-4 text-sm text-red-600">
          {error}
        </p>
      )}

      {!loaded ? (
        <p className="mt-6 text-sm text-slate-500">Loading alerts...</p>
      ) : alerts.length === 0 ? (
        <p className="mt-6 rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
          No active alerts. Everything looks fine.
        </p>
      ) : (
        <ul className="mt-6 divide-y rounded-lg border">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className="flex flex-wrap items-start justify-between gap-3 p-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      SEVERITY_STYLES[alert.severity] ?? SEVERITY_STYLES.info
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <span className="font-mono text-xs text-slate-500">
                    {alert.event_type}
                  </span>
                </div>
                <p className="mt-1 text-sm font-medium text-slate-900">
                  {alert.message}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Zone: {zoneName(alert.zone_id)}
                  {" · "}
                  Device:{" "}
                  {alert.device_id ? `${alert.device_id.slice(0, 8)}…` : "—"}
                </p>
              </div>

              <time className="whitespace-nowrap text-xs text-slate-500">
                {new Date(alert.created_at).toLocaleString()}
              </time>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
