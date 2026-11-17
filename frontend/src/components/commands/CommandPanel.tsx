import { useEffect, useState } from "react";
import {
  fetchCommands,
  fetchDevices,
  submitCommand,
  type CommandLogDto,
  type CommandType,
  type DeviceDto,
} from "../../services/api";

const COMMANDS: { type: CommandType; label: string }[] = [
  { type: "start_pump", label: "Start pump" },
  { type: "stop_pump", label: "Stop pump" },
  { type: "set_light_level", label: "Set light level" },
];

const STATUS_STYLES: Record<string, string> = {
  success: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  rejected: "bg-amber-100 text-amber-700",
};

interface ControlsData {
  actuators: DeviceDto[];
  history: CommandLogDto[];
}

// Pure data loader: fetches only, never touches React state.
async function loadControls(): Promise<ControlsData> {
  const [devices, commands] = await Promise.all([
    fetchDevices(),
    fetchCommands(50),
  ]);

  return {
    actuators: devices.filter((d) => d.role === "actuator"),
    history: commands,
  };
}

export default function CommandPanel() {
  const [actuators, setActuators] = useState<DeviceDto[]>([]);
  const [history, setHistory] = useState<CommandLogDto[]>([]);
  const [deviceId, setDeviceId] = useState("");
  const [level, setLevel] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  function applyControls(data: ControlsData) {
    setActuators(data.actuators);
    setHistory(data.history);
    setDeviceId((current) =>
      data.actuators.some((d) => d.id === current)
        ? current
        : data.actuators[0]?.id ?? "",
    );
  }

  async function reload() {
    applyControls(await loadControls());
  }

  useEffect(() => {
    let cancelled = false;

    loadControls()
      .then((data) => {
        if (!cancelled) applyControls(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load controls.",
          );
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selected = actuators.find((d) => d.id === deviceId);
  const allowed = selected?.allowed_commands ?? [];

  async function handleCommand(type: CommandType) {
    if (!deviceId) return;

    setBusy(true);
    setError("");
    setMessage("");

    try {
      const payload = type === "set_light_level" ? { level } : {};
      const log = await submitCommand(type, deviceId, payload);

      if (log.status === "success") {
        setMessage(`${type} succeeded.`);
      } else {
        setError(`${type} ${log.status}: ${log.error_message ?? ""}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Command failed.");
    } finally {
      // Rejected/failed rows are logged too, so always refresh.
      try {
        await reload();
      } catch {
        // keep the previous data
      }
      setBusy(false);
    }
  }

  function deviceName(id: string): string {
    return (
      actuators.find((d) => d.id === id)?.display_name ||
      `${id.slice(0, 8)}…`
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-emerald-700">Controls</h3>
      <p className="mt-1 text-sm text-slate-500">
        Each button submits a Command. Buttons are disabled when the command
        is not in the actuator's <code>allowed_commands</code>.
      </p>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div>
          <label
            htmlFor="command-device"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Actuator
          </label>
          <select
            id="command-device"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            disabled={actuators.length === 0}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          >
            {actuators.length === 0 && (
              <option value="">No actuators found</option>
            )}
            {actuators.map((d) => (
              <option key={d.id} value={d.id}>
                {d.display_name} ({d.state ?? "idle"})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="command-level"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Light level (0–1)
          </label>
          <input
            id="command-level"
            type="number"
            min={0}
            max={1}
            step={0.1}
            value={level}
            onChange={(e) => setLevel(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        {COMMANDS.map(({ type, label }) => (
          <button
            key={type}
            type="button"
            onClick={() => void handleCommand(type)}
            disabled={busy || !deviceId || !allowed.includes(type)}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {label}
          </button>
        ))}
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

      <h4 className="mt-6 font-semibold text-slate-900">Command history</h4>

      {history.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">No commands yet.</p>
      ) : (
        <div className="mt-2 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2 pr-4">Time</th>
                <th className="py-2 pr-4">Device</th>
                <th className="py-2 pr-4">Command</th>
                <th className="py-2 pr-4">Payload</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2">Error</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {history.map((row) => (
                <tr key={row.id}>
                  <td className="whitespace-nowrap py-2 pr-4 text-slate-600">
                    {new Date(row.created_at).toLocaleString()}
                  </td>
                  <td className="py-2 pr-4 text-slate-900">
                    {deviceName(row.device_id)}
                  </td>
                  <td className="py-2 pr-4 font-mono text-xs">
                    {row.command_type}
                  </td>
                  <td className="py-2 pr-4 font-mono text-xs">
                    {JSON.stringify(row.payload)}
                  </td>
                  <td className="py-2 pr-4">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${STATUS_STYLES[row.status]}`}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td className="py-2 text-slate-600">
                    {row.error_message ?? "—"}
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
