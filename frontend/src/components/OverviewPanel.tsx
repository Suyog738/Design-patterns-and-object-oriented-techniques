
import { useEffect, useState } from "react";
import {
  fetchLocations,
  fetchOverview,
  type LocationDto,
  type LocationOverview,
} from "../services/api";

export default function OverviewPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [overview, setOverview] = useState<LocationOverview | null>(null);
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [loadingOverview, setLoadingOverview] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadLocations() {
      try {
        const data = await fetchLocations();

        if (cancelled) return;

        setLocations(data);
        setLocationId(data[0]?.id ?? "");

        if (data.length === 0) {
          setError("No locations found. Create a location first.");
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load locations.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingLocations(false);
        }
      }
    }

    void loadLocations();

    return () => {
      cancelled = true;
    };
  }, []);

useEffect(() => {
  if (!locationId) {
    return;
  }

  let cancelled = false;

  async function loadOverview() {
    setLoadingOverview(true);
    setError("");

    try {
      const data = await fetchOverview(locationId);
      if (!cancelled) {
        setOverview(data);
      }
    } catch (err) {
      if (!cancelled) {
        setOverview(null);
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load the overview."
        );
      }
    } finally {
      if (!cancelled) {
        setLoadingOverview(false);
      }
    }
  }

  void loadOverview();

  return () => {
    cancelled = true;
  };
}, [locationId, refreshCount]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-emerald-700">
            Location Overview
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            View assigned devices, latest readings, and automation.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <select
            aria-label="Select location"
            value={locationId}
            onChange={(event) => setLocationId(event.target.value)}
            disabled={loadingLocations || locations.length === 0}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={() => setRefreshCount((count) => count + 1)}
            disabled={!locationId || loadingOverview}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {loadingOverview ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      {loadingOverview && (
        <p className="text-sm text-slate-500">
          Loading location overview...
        </p>
      )}

      {overview && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Location</p>
              <p className="mt-1 font-semibold">
                {overview.location.name}
              </p>
            </div>

            <div className="rounded-lg border bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Assigned sensors</p>
              <p className="mt-1 text-2xl font-semibold">
                {overview.device_counts.sensor}
              </p>
            </div>

            <div className="rounded-lg border bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Assigned actuators</p>
              <p className="mt-1 text-2xl font-semibold">
                {overview.device_counts.actuator}
              </p>
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <h4 className="font-semibold">Automation</h4>
            <p className="mt-2 text-sm">
              Strategy: {overview.strategy_key ?? "Not configured"}
            </p>

            {overview.last_recommendation ? (
              <div className="mt-3 text-sm">
                <p>
                  Recommendation:{" "}
                  <span className="font-semibold">
                    {overview.last_recommendation.action}
                  </span>
                </p>
                <p className="mt-1 text-slate-600">
                  {overview.last_recommendation.reason}
                </p>
              </div>
            ) : (
              <p className="mt-2 text-sm text-slate-500">
                No recommendation available.
              </p>
            )}
          </div>

          <div className="space-y-4">
            <h4 className="font-semibold">Zones</h4>

            {overview.zones.length === 0 && (
              <p className="text-sm text-slate-500">
                No zones are configured for this location.
              </p>
            )}

            {overview.zones.map((zone) => (
              <div key={zone.id} className="rounded-lg border p-4">
                <h5 className="font-semibold">{zone.name}</h5>

                <p className="mt-1 text-sm text-slate-500">
                  Moisture thresholds:{" "}
                  {zone.moisture_threshold_low}–{zone.moisture_threshold_high}
                </p>

                {zone.devices.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-500">
                    No assigned devices.
                  </p>
                ) : (
                  <div className="mt-3 space-y-3">
                    {zone.devices.map((device) => {
                      const reading = zone.latest_readings.find(
                        (item) => item.device_id === device.id,
                      );

                      return (
                        <div
                          key={device.id}
                          className="rounded-lg bg-slate-50 p-3"
                        >
                          <p className="font-medium">
                            {device.display_name}
                          </p>
                          <p className="text-sm text-slate-500">
                            {device.device_type} · {device.role}
                          </p>

                          {reading ? (
                            <>
                              <p className="mt-2 text-sm">
                                Latest reading: {reading.value} {reading.unit}
                              </p>
                              <p className="mt-1 text-xs text-slate-500">
                                Recorded:{" "}
                                {new Date(
                                  reading.recorded_at,
                                ).toLocaleString()}
                              </p>
                              <p className="mt-1 text-xs text-slate-500">
                                Tracking:{" "}
                                {reading.tracking_enabled
                                  ? "Enabled"
                                  : "Disabled"}
                                {" · "}
                                Sampling interval:{" "}
                                {reading.sampling_interval_seconds}s
                              </p>
                            </>
                          ) : (
                            <p className="mt-2 text-sm text-slate-500">
                              No readings available.
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
