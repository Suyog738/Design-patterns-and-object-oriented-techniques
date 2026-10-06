import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensors,
  fetchSensorReadings,
  fetchDevices,
  provisionDeviceFamily,
  readSensor,
  updateDeviceSampling,
  type Sensor,
  type Reading,
  type DeviceDto,
  type DeviceFamily,
} from "../services/api";

import LocationConfigWizard from "../components/LocationConfigWizard";

export default function DashboardPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const [readings, setReadings] = useState<
    Record<string, Reading | null>
  >({});
  const [readingLoading, setReadingLoading] = useState<
    Record<string, boolean>
  >({});
  const [readingErrors, setReadingErrors] = useState<
    Record<string, string>
  >({});

  const [samplingIntervals, setSamplingIntervals] = useState<
    Record<string, number>
  >({});
  const [trackingStates, setTrackingStates] = useState<
    Record<string, boolean>
  >({});
  const [samplingSaving, setSamplingSaving] = useState<
    Record<string, boolean>
  >({});
  const [samplingErrors, setSamplingErrors] = useState<
    Record<string, string>
  >({});
  const [samplingSuccess, setSamplingSuccess] = useState<
    Record<string, string>
  >({});

  const [deviceFamily, setDeviceFamily] =
    useState<DeviceFamily>("simulation");

  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [devicesLoading, setDevicesLoading] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
  const [deviceError, setDeviceError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadSensors() {
      try {
        setLoading(true);

        const data = await fetchSensors();

        if (!cancelled) {
          setSensors(data);
          setError("");

          const intervals: Record<string, number> = {};
          const tracking: Record<string, boolean> = {};

          data.forEach((sensor) => {
            const interval =
              sensor.default_config.sampling_interval_seconds;

            intervals[sensor.id] =
              typeof interval === "number"
                ? interval
                : 300;

            const trackingEnabled =
              sensor.default_config.tracking_enabled;

            tracking[sensor.id] =
              typeof trackingEnabled === "boolean"
                ? trackingEnabled
                : true;
          });

          setSamplingIntervals(intervals);
          setTrackingStates(tracking);
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

  useEffect(() => {
    if (sensors.length === 0) {
      return;
    }

    let cancelled = false;

    async function pollReadings() {
      for (const sensor of sensors) {
        try {
          const data = await fetchSensorReadings(
            sensor.id,
            1,
          );

          if (!cancelled) {
            setReadings((current) => ({
              ...current,
              [sensor.id]:
                data.length > 0 ? data[0] : null,
            }));

            setReadingErrors((current) => ({
              ...current,
              [sensor.id]: "",
            }));
          }
        } catch {
          if (!cancelled) {
            setReadingErrors((current) => ({
              ...current,
              [sensor.id]:
                "Failed to load latest reading.",
            }));
          }
        }
      }
    }

    pollReadings();

    // Phase 12 replaces this poll with WebSocket.

    const intervalId = window.setInterval(
      pollReadings,
      5000,
    );

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [sensors]);

  useEffect(() => {
    let cancelled = false;

    async function loadDevices() {
      try {
        setDevicesLoading(true);
        setDeviceError("");

        const data = await fetchDevices(deviceFamily);

        if (!cancelled) {
          setDevices(data);
        }
      } catch {
        if (!cancelled) {
          setDeviceError("Failed to load devices.");
        }
      } finally {
        if (!cancelled) {
          setDevicesLoading(false);
        }
      }
    }

    loadDevices();

    return () => {
      cancelled = true;
    };
  }, [deviceFamily]);

  async function handleCreateSensor(
    type: "moisture" | "light",
    displayName: string,
  ) {
    try {
      setCreating(true);
      setError("");

      await createSensor(type, displayName);

      const data = await fetchSensors();

      setSensors(data);

      const intervals: Record<string, number> = {};
      const tracking: Record<string, boolean> = {};

      data.forEach((sensor) => {
        const interval =
          sensor.default_config.sampling_interval_seconds;

        intervals[sensor.id] =
          typeof interval === "number"
            ? interval
            : 300;

        const trackingEnabled =
          sensor.default_config.tracking_enabled;

        tracking[sensor.id] =
          typeof trackingEnabled === "boolean"
            ? trackingEnabled
            : true;
      });

      setSamplingIntervals(intervals);
      setTrackingStates(tracking);
    } catch {
      setError("Failed to create sensor.");
    } finally {
      setCreating(false);
    }
  }

  async function handleReadNow(sensorId: string) {
    try {
      setReadingLoading((current) => ({
        ...current,
        [sensorId]: true,
      }));

      setReadingErrors((current) => ({
        ...current,
        [sensorId]: "",
      }));

      const reading = await readSensor(sensorId);

      setReadings((current) => ({
        ...current,
        [sensorId]: reading,
      }));
    } catch (err) {
      setReadingErrors((current) => ({
        ...current,
        [sensorId]:
          err instanceof Error
            ? err.message
            : "Failed to read sensor.",
      }));
    } finally {
      setReadingLoading((current) => ({
        ...current,
        [sensorId]: false,
      }));
    }
  }

  function handleIntervalChange(
    sensorId: string,
    value: string,
  ) {
    const interval = Number(value);

    setSamplingIntervals((current) => ({
      ...current,
      [sensorId]: Number.isNaN(interval) ? 5 : interval,
    }));

    setSamplingSuccess((current) => ({
      ...current,
      [sensorId]: "",
    }));
  }

  function handleTrackingChange(
    sensorId: string,
    enabled: boolean,
  ) {
    setTrackingStates((current) => ({
      ...current,
      [sensorId]: enabled,
    }));

    setSamplingSuccess((current) => ({
      ...current,
      [sensorId]: "",
    }));
  }

  async function handleSaveSampling(sensorId: string) {
    const interval = samplingIntervals[sensorId] ?? 300;

    if (interval < 5) {
      setSamplingErrors((current) => ({
        ...current,
        [sensorId]:
          "Sampling interval must be at least 5 seconds.",
      }));
      return;
    }

    try {
      setSamplingSaving((current) => ({
        ...current,
        [sensorId]: true,
      }));

      setSamplingErrors((current) => ({
        ...current,
        [sensorId]: "",
      }));

      setSamplingSuccess((current) => ({
        ...current,
        [sensorId]: "",
      }));

      const updatedDevice =
        await updateDeviceSampling(
          sensorId,
          {
            sampling_interval_seconds: interval,
            tracking_enabled:
              trackingStates[sensorId] ?? true,
          },
        );

      const updatedInterval =
        updatedDevice.default_config
          .sampling_interval_seconds;

      setSamplingIntervals((current) => ({
        ...current,
        [sensorId]:
          typeof updatedInterval === "number"
            ? updatedInterval
            : interval,
      }));

      setSamplingSuccess((current) => ({
        ...current,
        [sensorId]: "Sampling settings saved.",
      }));
    } catch (err) {
      setSamplingErrors((current) => ({
        ...current,
        [sensorId]:
          err instanceof Error
            ? err.message
            : "Failed to update sampling settings.",
      }));
    } finally {
      setSamplingSaving((current) => ({
        ...current,
        [sensorId]: false,
      }));
    }
  }

  async function handleProvisionFamily() {
    try {
      setProvisioning(true);
      setDeviceError("");

      await provisionDeviceFamily(deviceFamily);

      const data = await fetchDevices(deviceFamily);
      setDevices(data);
    } catch {
      setDeviceError(
        "Failed to provision device family.",
      );
    } finally {
      setProvisioning(false);
    }
  }

  function formatRecordedAt(recordedAt: string): string {
    const date = new Date(recordedAt);

    if (Number.isNaN(date.getTime())) {
      return recordedAt;
    }

    return date.toLocaleString();
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
        <section
          id="config"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm md:col-span-2 lg:col-span-3"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Configuration
          </h3>

          <div className="mt-5">
            <LocationConfigWizard />
          </div>
        </section>

        <section
          id="sensors"
          className="rounded-xl border bg-white p-6 shadow-sm md:col-span-2 lg:col-span-3"
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
                  "Greenhouse Moisture Sensor",
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
                  "Greenhouse Light Sensor",
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

          {!loading &&
            !error &&
            sensors.length === 0 && (
              <p className="mt-4 text-sm text-slate-500">
                No sensors found.
              </p>
            )}

          {!loading &&
            !error &&
            sensors.length > 0 && (
              <div className="mt-5 grid gap-5 lg:grid-cols-2">
                {sensors.map((sensor) => {
                  const latestReading =
                    readings[sensor.id] ?? null;
                  const isReading =
                    readingLoading[sensor.id] ?? false;
                  const readingError =
                    readingErrors[sensor.id] ?? "";
                  const samplingError =
                    samplingErrors[sensor.id] ?? "";
                  const samplingMessage =
                    samplingSuccess[sensor.id] ?? "";
                  const interval =
                    samplingIntervals[sensor.id] ?? 300;
                  const tracking =
                    trackingStates[sensor.id] ?? true;

                  return (
                    <div
                      key={sensor.id}
                      className="rounded-xl border bg-slate-50 p-5"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-slate-900">
                            {sensor.display_name ||
                              "Unnamed sensor"}
                          </p>

                          <p className="mt-1 text-sm text-slate-500">
                            Type: {sensor.device_type}
                          </p>
                        </div>

                        <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                          sensor
                        </span>
                      </div>

                      <p className="mt-2 text-sm text-slate-500">
                        Protocol:{" "}
                        {String(
                          sensor.default_config.protocol ??
                            "N/A",
                        )}
                      </p>

                      <p className="mt-1 break-all text-sm text-slate-500">
                        ID: {sensor.id}
                      </p>

                      <div className="mt-5 rounded-lg border bg-white p-4">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-medium text-slate-700">
                            Latest reading
                          </p>

                          {latestReading && (
                            <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">
                              {latestReading.source}
                            </span>
                          )}
                        </div>

                        {latestReading ? (
                          <>
                            <div className="mt-3 flex items-baseline gap-2">
                              <span className="text-3xl font-bold text-slate-900">
                                {latestReading.value.toFixed(2)}
                              </span>

                              <span className="text-sm text-slate-500">
                                {latestReading.unit}
                              </span>
                            </div>

                            <p className="mt-2 text-xs text-slate-400">
                              Recorded:{" "}
                              {formatRecordedAt(
                                latestReading.recorded_at,
                              )}
                            </p>
                          </>
                        ) : (
                          <p className="mt-3 text-sm text-slate-500">
                            No stored reading yet.
                          </p>
                        )}

                        {readingError && (
                          <p className="mt-3 text-sm text-red-500">
                            {readingError}
                          </p>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            handleReadNow(sensor.id)
                          }
                          disabled={isReading}
                          className="mt-4 w-full rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isReading
                            ? "Reading..."
                            : "Read now"}
                        </button>
                      </div>

                      <div className="mt-5 rounded-lg border bg-white p-4">
                        <h4 className="font-medium text-slate-800">
                          Sampling settings
                        </h4>

                        <label
                          htmlFor={`interval-${sensor.id}`}
                          className="mt-4 block text-sm font-medium text-slate-700"
                        >
                          Sampling interval
                        </label>

                        <div className="mt-2 flex items-center gap-2">
                          <input
                            id={`interval-${sensor.id}`}
                            type="number"
                            min="5"
                            step="1"
                            value={interval}
                            onChange={(event) =>
                              handleIntervalChange(
                                sensor.id,
                                event.target.value,
                              )
                            }
                            className="w-28 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                          />

                          <span className="text-sm text-slate-500">
                            seconds
                          </span>
                        </div>

                        <div className="mt-4 flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-slate-700">
                              Tracking
                            </p>

                            <p className="text-xs text-slate-500">
                              Automatic sensor sampling
                            </p>
                          </div>

                          <button
                            type="button"
                            role="switch"
                            aria-checked={tracking}
                            onClick={() =>
                              handleTrackingChange(
                                sensor.id,
                                !tracking,
                              )
                            }
                            className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                              tracking
                                ? "bg-emerald-600"
                                : "bg-slate-300"
                            }`}
                          >
                            <span
                              className={`inline-block h-4 w-4 rounded-full bg-white ${
                                tracking
                                  ? "translate-x-6"
                                  : "translate-x-1"
                              }`}
                            />
                          </button>
                        </div>

                        {samplingError && (
                          <p className="mt-3 text-sm text-red-500">
                            {samplingError}
                          </p>
                        )}

                        {samplingMessage && (
                          <p className="mt-3 text-sm text-emerald-600">
                            {samplingMessage}
                          </p>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            handleSaveSampling(sensor.id)
                          }
                          disabled={
                            samplingSaving[sensor.id] ??
                            false
                          }
                          className="mt-4 w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {samplingSaving[sensor.id]
                            ? "Saving..."
                            : "Save sampling settings"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
        </section>

        <section
          id="devices"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm md:col-span-2"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Device Families
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Select a device family and provision its complete device set.
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setDeviceFamily("simulation")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                deviceFamily === "simulation"
                  ? "bg-emerald-600 text-white"
                  : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              Simulation
            </button>

            <button
              type="button"
              onClick={() => setDeviceFamily("edge")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                deviceFamily === "edge"
                  ? "bg-emerald-600 text-white"
                  : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              Edge
            </button>
          </div>

          <button
            type="button"
            onClick={handleProvisionFamily}
            disabled={provisioning}
            className="mt-4 rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {provisioning
              ? "Provisioning..."
              : `Provision ${deviceFamily}`}
          </button>

          {deviceError && (
            <p className="mt-4 text-sm text-red-500">
              {deviceError}
            </p>
          )}

          <div className="mt-6">
            <h4 className="font-semibold text-slate-900">
              {deviceFamily === "simulation"
                ? "Simulation Devices"
                : "Edge Devices"}
            </h4>

            {devicesLoading && (
              <p className="mt-4 text-sm text-slate-500">
                Loading devices...
              </p>
            )}

            {!devicesLoading &&
              !deviceError &&
              devices.length === 0 && (
                <p className="mt-4 text-sm text-slate-500">
                  No devices found for this family.
                </p>
              )}

            {!devicesLoading &&
              !deviceError &&
              devices.length > 0 && (
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {devices.map((device) => (
                    <div
                      key={device.id}
                      className="rounded-lg border bg-slate-50 p-4"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <p className="font-medium text-slate-900">
                          {device.display_name}
                        </p>

                        <span
                          className={`rounded-full px-2 py-1 text-xs font-medium ${
                            device.role === "sensor"
                              ? "bg-blue-100 text-blue-700"
                              : "bg-orange-100 text-orange-700"
                          }`}
                        >
                          {device.role}
                        </span>
                      </div>

                      <p className="mt-2 text-sm text-slate-500">
                        Type: {device.device_type}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        Family: {device.device_family}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        Protocol:{" "}
                        {String(
                          device.default_config.protocol ??
                            "N/A",
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              )}
          </div>
        </section>

        <section
          id="automation"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Automation
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for the automation section.
          </p>
        </section>

        <section
          id="overview"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Overview
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for the overview section.
          </p>
        </section>

        <section
          id="controls"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Controls
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for the controls section.
          </p>
        </section>

        <section
          id="events"
          className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-emerald-700">
            Events
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for the events section.
          </p>
        </section>
      </div>
    </div>
  );
}