import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensors,
  fetchDevices,
  provisionDeviceFamily,
  type Sensor,
  type DeviceDto,
  type DeviceFamily,
} from "../services/api";

import LocationConfigWizard from "../components/LocationConfigWizard";



export default function DashboardPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

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
    } catch {
      setError("Failed to create sensor.");
    } finally {
      setCreating(false);
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
      setDeviceError("Failed to provision device family.");
    } finally {
      setProvisioning(false);
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

        {/* CONFIGURATION */}
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

        {/* SENSORS */}
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

        {/* DEVICE FAMILIES */}
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
                          device.default_config.protocol ?? "N/A"
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              )}
          </div>
        </section>

        {/* PHASE 3 OTHER SECTIONS */}
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

