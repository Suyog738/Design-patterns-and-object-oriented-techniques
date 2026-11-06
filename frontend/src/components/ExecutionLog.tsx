import { useEffect, useState } from "react";
import {
  applyActuatorCommand,
  fetchActuatorExecutions,
  fetchDevices,
  type ActuatorExecutionDto,
  type DeviceDto,
} from "../services/api";

export default function ExecutionLog() {
  const [executions, setExecutions] = useState<ActuatorExecutionDto[]>([]);
  const [actuators, setActuators] = useState<DeviceDto[]>([]);
  const [deviceId, setDeviceId] = useState("");
  const [command, setCommand] = useState("start_pump");
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadExecutions() {
    try {
      setLoading(true);
      setExecutions(await fetchActuatorExecutions(20));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load execution log.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadInitialData() {
      try {
        const [devices, initialExecutions] = await Promise.all([
          fetchDevices(),
          fetchActuatorExecutions(20),
        ]);

        if (cancelled) return;

        const onlyActuators = devices.filter(
          (device) => device.role === "actuator",
        );

        setActuators(onlyActuators);
        setDeviceId(onlyActuators[0]?.id ?? "");
        setExecutions(initialExecutions);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load execution log.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadInitialData();

    return () => {
      cancelled = true;
    };
  }, []);


  async function handleApply() {
    if (!deviceId) {
      setError("Select an actuator first.");
      return;
    }

    setApplying(true);
    setError("");
    setMessage("");

    try {
      await applyActuatorCommand(deviceId, command.trim());
      setMessage("Command applied.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to apply command.",
      );
    } finally {
      setApplying(false);
      // Blocked attempts are logged too, so always refresh.
      await loadExecutions();
    }
  }

  function deviceName(id: string): string {
    return (
      actuators.find((device) => device.id === id)?.display_name ||
      `${id.slice(0, 8)}…`
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-emerald-700">
            Actuator Execution Log
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Every apply attempt passes through logging → max run time →
            simulation adapter. The command itself is not validated in this
            phase. A successful row has an empty message; a blocked row shows
            the policy that stopped it.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadExecutions()}
          disabled={loading}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <div>
          <label
            htmlFor="execution-device"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Actuator
          </label>
          <select
            id="execution-device"
            value={deviceId}
            onChange={(event) => setDeviceId(event.target.value)}
            disabled={actuators.length === 0}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          >
            <option value="">
              {actuators.length === 0
                ? "No actuators found"
                : "Select actuator"}
            </option>
            {actuators.map((device) => (
              <option key={device.id} value={device.id}>
                {device.display_name} ({device.state ?? "unknown"})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="execution-command"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Command
          </label>
          <input
            id="execution-command"
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        <div className="flex items-end">
          <button
            type="button"
            onClick={handleApply}
            disabled={!deviceId || !command.trim() || applying}
            className="w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {applying ? "Applying..." : "Apply"}
          </button>
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-4 text-sm text-red-600">
          {error}
        </p>
      )}

      {message && (
        <p role="status" className="mt-4 text-sm text-emerald-700">
          {message}
        </p>
      )}

      {!loading && executions.length === 0 ? (
        <p className="mt-6 rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
          No executions yet. Apply a command to an actuator to see it here.
        </p>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2 pr-4">Time</th>
                <th className="py-2 pr-4">Device</th>
                <th className="py-2 pr-4">Result</th>
                <th className="py-2 pr-4">Policies</th>
                <th className="py-2">Message</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {executions.map((execution) => (
                <tr key={execution.id}>
                  <td className="whitespace-nowrap py-2 pr-4 text-slate-600">
                    {new Date(execution.created_at).toLocaleString()}
                  </td>
                  <td className="py-2 pr-4 text-slate-900">
                    {deviceName(execution.device_id)}
                  </td>
                  <td className="py-2 pr-4">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${
                        execution.success
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {execution.success ? "success" : "failed"}
                    </span>
                  </td>
                  <td className="py-2 pr-4">
                    <div className="flex flex-wrap gap-1">
                      {execution.policy_applied.map((policy) => (
                        <span
                          key={policy}
                          className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600"
                        >
                          {policy}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2 text-slate-600">
                    {execution.message ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
