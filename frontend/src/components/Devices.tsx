import { useEffect, useState } from "react";
import {
  fetchDevices,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
} from "../services/api";

type DevicesProps = {
  family: DeviceFamily;
};

export default function Devices({ family }: DevicesProps) {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchDevices(family);

        if (!cancelled) {
          setDevices(data);
          setError("");
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load devices.");
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [family]);

  async function handleProvision() {
    try {
      setProvisioning(true);
      setError("");

      const createdDevices = await provisionDeviceFamily(family);

      setDevices((currentDevices) => [
        ...currentDevices,
        ...createdDevices,
      ]);
    } catch {
      setError("Failed to provision device family.");
    } finally {
      setProvisioning(false);
    }
  }

  return (
    <section
      id="devices"
      className="min-h-40 rounded-xl border bg-white p-6 shadow-sm"
    >
      <h3 className="text-lg font-semibold text-emerald-700">
        Device Families
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        Manage devices for the selected device family.
      </p>

      <button
        type="button"
        onClick={handleProvision}
        disabled={provisioning}
        className="mt-4 rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {provisioning
          ? "Provisioning..."
          : `Provision ${family}`}
      </button>

      {error && (
        <p className="mt-4 text-sm text-red-500">
          {error}
        </p>
      )}

      {loading && (
        <p className="mt-4 text-sm text-slate-500">
          Loading devices...
        </p>
      )}

      {!loading && !error && devices.length === 0 && (
        <p className="mt-4 text-sm text-slate-500">
          No devices found for this family.
        </p>
      )}

      {!loading && !error && devices.length > 0 && (
        <div className="mt-5 grid gap-3 sm:grid-cols-2">
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
    </section>
  );
}