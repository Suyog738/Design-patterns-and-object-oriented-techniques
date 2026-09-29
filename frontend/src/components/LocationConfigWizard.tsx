import { useEffect, useMemo, useState } from "react";

import {
  addZone,
  assignDeviceToZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  fetchDevices,
  fetchLocationConfig,
  fetchLocations,
  updateZone,
  type DeviceDto,
  type LocationConfigDto,
  type LocationDto,
  type ZoneConfigRequest,
  type ZoneDto,
} from "../services/api";

interface ZoneForm {
  name: string;
  low: string;
  high: string;
  schedule: string;
}

const emptyZone: ZoneForm = {
  name: "",
  low: "0.3",
  high: "0.7",
  schedule: "{}",
};

function zoneToForm(zone: ZoneDto): ZoneForm {
  return {
    name: zone.name,
    low: String(zone.moisture_threshold_low),
    high: String(zone.moisture_threshold_high),
    schedule: JSON.stringify(
      zone.schedule ?? {},
      null,
      2,
    ),
  };
}

function parseZone(
  form: ZoneForm,
): ZoneConfigRequest {
  const name = form.name.trim();

  if (!name) {
    throw new Error("Zone name is required.");
  }

  const low = Number(form.low);
  const high = Number(form.high);

  if (!Number.isFinite(low) || !Number.isFinite(high)) {
    throw new Error(
      "Moisture thresholds must be numbers.",
    );
  }

  if (low < 0 || low > 1) {
    throw new Error(
      "Low threshold must be between 0 and 1.",
    );
  }

  if (high < 0 || high > 1) {
    throw new Error(
      "High threshold must be between 0 and 1.",
    );
  }

  if (low >= high) {
    throw new Error(
      "Low threshold must be lower than high threshold.",
    );
  }

  let schedule: Record<string, unknown>;

  try {
    schedule = JSON.parse(form.schedule || "{}");
  } catch {
    throw new Error(
      "Schedule must contain valid JSON.",
    );
  }

  if (
    typeof schedule !== "object" ||
    Array.isArray(schedule) ||
    schedule === null
  ) {
    throw new Error(
      "Schedule must be a JSON object.",
    );
  }

  return {
    name,
    moisture_threshold_low: low,
    moisture_threshold_high: high,
    schedule,
  };
}

export default function LocationConfigWizard() {
  const [locations, setLocations] = useState<
    LocationDto[]
  >([]);

  const [selectedLocationId, setSelectedLocationId] =
    useState<string>("");

  const [config, setConfig] =
    useState<LocationConfigDto | null>(null);

  const [devices, setDevices] = useState<DeviceDto[]>(
    [],
  );

  const [locationName, setLocationName] =
    useState("");

  const [newZone, setNewZone] =
    useState<ZoneForm>(emptyZone);

  const [editingZoneId, setEditingZoneId] =
    useState<string | null>(null);

  const [editingZone, setEditingZone] =
    useState<ZoneForm>(emptyZone);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadLocations() {
    const data = await fetchLocations();

    setLocations(data);

    if (
      selectedLocationId &&
      data.some(
        (location) =>
          location.id === selectedLocationId,
      )
    ) {
      return;
    }

    if (data.length > 0) {
      setSelectedLocationId(data[0].id);
    } else {
      setSelectedLocationId("");
      setConfig(null);
    }
  }

  async function loadDevices() {
    const data = await fetchDevices();
    setDevices(data);
  }

  async function loadConfig(locationId: string) {
    const data =
      await fetchLocationConfig(locationId);

    setConfig(data);
  }

useEffect(() => {
  async function load() {
    try {
      setLoading(true);
      setError("");

      await loadLocations();
      await loadDevices();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load configuration.",
      );
    } finally {
      setLoading(false);
    }
  }

  load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);

  useEffect(() => {
  if (!selectedLocationId) {
    return;
  }

  async function load() {
    try {
      setError("");
      await loadConfig(selectedLocationId);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load location.",
      );
    }
  }

  load();
}, [selectedLocationId]);

  async function handleCreateLocation(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      setMessage("");

      if (!locationName.trim()) {
        throw new Error(
          "Location name is required.",
        );
      }

      const zone = parseZone(newZone);

      const created =
        await createLocationConfig({
          location_name: locationName.trim(),
          zones: [zone],
        });

      setLocationName("");
      setNewZone(emptyZone);

      await loadLocations();

      setSelectedLocationId(
        created.location.id,
      );

      setConfig(created);

      setMessage(
        "Location created successfully.",
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create location.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleAddZone(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!config) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const zone = parseZone(newZone);

      await addZone(
        config.location.id,
        zone,
      );

      setNewZone(emptyZone);

      await loadConfig(
        config.location.id,
      );

      setMessage("Zone added successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to add zone.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateZone(
    zoneId: string,
  ) {
    if (!config) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const zone = parseZone(editingZone);

      await updateZone(
        config.location.id,
        zoneId,
        zone,
      );

      setEditingZoneId(null);

      await loadConfig(
        config.location.id,
      );

      setMessage("Zone updated successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update zone.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteZone(
    zoneId: string,
  ) {
    if (!config) {
      return;
    }

    if (config.zones.length <= 1) {
      setError(
        "A location must contain at least one zone.",
      );
      return;
    }

    if (
      !window.confirm(
        "Delete this zone?",
      )
    ) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      await deleteZone(
        config.location.id,
        zoneId,
      );

      await loadConfig(
        config.location.id,
      );

      await loadDevices();

      setMessage("Zone deleted.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete zone.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteLocation() {
    if (!config) {
      return;
    }

    if (
      !window.confirm(
        `Delete "${config.location.name}"?`,
      )
    ) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      await deleteLocation(
        config.location.id,
      );

      await loadLocations();

      setConfig(null);

      await loadDevices();

      setMessage("Location deleted.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete location.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleAssignment(
    deviceId: string,
    zoneId: string,
  ) {
    try {
      setError("");
      setMessage("");

      await assignDeviceToZone(
        deviceId,
        zoneId || null,
      );

      await loadDevices();

      setMessage(
        "Device assignment updated.",
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to assign device.",
      );
    }
  }

  const allZones = useMemo(() => {
    return config?.zones ?? [];
  }, [config]);

  if (loading) {
    return (
      <div className="rounded-xl border bg-white p-6">
        <p className="text-slate-500">
          Loading configuration...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          Location Configuration
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Create locations, configure zones,
          and assign devices.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {message}
        </div>
      )}

      {/* CREATE LOCATION */}
      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Add Location
        </h3>

        <form
          onSubmit={handleCreateLocation}
          className="mt-5 space-y-4"
        >
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Location name
            </label>

            <input
              value={locationName}
              onChange={(event) =>
                setLocationName(
                  event.target.value,
                )
              }
              placeholder="Main Greenhouse"
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </div>

          <ZoneFields
            value={newZone}
            onChange={setNewZone}
          />

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {saving
              ? "Creating..."
              : "Create Location"}
          </button>
        </form>
      </section>

      {/* LOCATION SELECT */}
      {locations.length > 0 && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex-1">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Select location
              </label>

              <select
                value={selectedLocationId}
                onChange={(event) =>
                  setSelectedLocationId(
                    event.target.value,
                  )
                }
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              >
                {locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.id}
                  >
                    {location.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={handleDeleteLocation}
              disabled={saving}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
            >
              Delete Location
            </button>
          </div>
        </section>
      )}

      {/* ZONES */}
      {config && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              {config.location.name}
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Zones
            </p>
          </div>

          <div className="mt-5 space-y-4">
            {config.zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded-lg border bg-slate-50 p-4"
              >
                {editingZoneId === zone.id ? (
                  <div className="space-y-4">
                    <ZoneFields
                      value={editingZone}
                      onChange={setEditingZone}
                    />

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          handleUpdateZone(
                            zone.id,
                          )
                        }
                        disabled={saving}
                        className="rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white"
                      >
                        Save
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          setEditingZoneId(null)
                        }
                        className="rounded-lg border px-4 py-2 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h4 className="font-semibold text-slate-900">
                          {zone.name}
                        </h4>

                        <p className="mt-1 text-sm text-slate-500">
                          Moisture:
                          {" "}
                          {zone.moisture_threshold_low}
                          {" - "}
                          {zone.moisture_threshold_high}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setEditingZoneId(
                              zone.id,
                            );
                            setEditingZone(
                              zoneToForm(zone),
                            );
                          }}
                          className="rounded-lg border px-3 py-2 text-sm"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            handleDeleteZone(
                              zone.id,
                            )
                          }
                          className="rounded-lg bg-red-600 px-3 py-2 text-sm text-white"
                        >
                          Delete
                        </button>
                      </div>
                    </div>

                    <DeviceAssignment
                      devices={devices}
                      locations={locations}
                      zones={allZones}
                      onAssign={handleAssignment}
                    />
                  </>
                )}
              </div>
            ))}
          </div>

          {/* ADD ZONE */}
          <form
            onSubmit={handleAddZone}
            className="mt-6 border-t pt-6"
          >
            <h4 className="font-semibold text-slate-900">
              Add Zone
            </h4>

            <div className="mt-4">
              <ZoneFields
                value={newZone}
                onChange={setNewZone}
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white"
            >
              Add Zone
            </button>
          </form>
        </section>
      )}
    </div>
  );
}


function ZoneFields({
  value,
  onChange,
}: {
  value: ZoneForm;
  onChange: (value: ZoneForm) => void;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">
          Zone name
        </label>

        <input
          value={value.name}
          onChange={(event) =>
            onChange({
              ...value,
              name: event.target.value,
            })
          }
          placeholder="Zone 1"
          className="w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">
          Low threshold
        </label>

        <input
          type="number"
          min="0"
          max="1"
          step="0.01"
          value={value.low}
          onChange={(event) =>
            onChange({
              ...value,
              low: event.target.value,
            })
          }
          className="w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">
          High threshold
        </label>

        <input
          type="number"
          min="0"
          max="1"
          step="0.01"
          value={value.high}
          onChange={(event) =>
            onChange({
              ...value,
              high: event.target.value,
            })
          }
          className="w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">
          Schedule JSON
        </label>

        <textarea
          value={value.schedule}
          onChange={(event) =>
            onChange({
              ...value,
              schedule: event.target.value,
            })
          }
          rows={4}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
        />
      </div>
    </div>
  );
}


function DeviceAssignment({
  devices,
  locations,
  zones,
  onAssign,
}: {
  devices: DeviceDto[];
  locations: LocationDto[];
  zones: ZoneDto[];
  onAssign: (
    deviceId: string,
    zoneId: string,
  ) => void;
}) {
  if (devices.length === 0) {
    return (
      <p className="mt-4 text-sm text-slate-500">
        No devices available.
      </p>
    );
  }

  return (
    <div className="mt-5 border-t pt-4">
      <h5 className="text-sm font-semibold text-slate-800">
        Device Assignment
      </h5>

      <div className="mt-3 space-y-3">
        {devices.map((device) => {
          const currentZone =
            zones.find(
              (zone) =>
                zone.id === device.zone_id,
            );

          const currentLocation =
            locations.find(
              (location) =>
                location.id ===
                device.location_id,
            );

          return (
            <div
              key={device.id}
              className="flex flex-col gap-2 rounded-lg border bg-white p-3 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <p className="font-medium text-slate-900">
                  {device.display_name}
                </p>

                <p className="text-xs text-slate-500">
                  {device.device_type}
                </p>

                {currentZone && (
                  <p className="mt-1 text-xs text-emerald-600">
                    Assigned:
                    {" "}
                    {currentLocation?.name ??
                      "Unknown"}
                    {" — "}
                    {currentZone.name}
                  </p>
                )}
              </div>

              <select
                value={device.zone_id ?? ""}
                onChange={(event) =>
                  onAssign(
                    device.id,
                    event.target.value,
                  )
                }
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">
                  Unassigned
                </option>

                {locations.map((location) => {
                  const locationZones =
                    zones.filter(
                      (zone) =>
                        zone.location_id ===
                        location.id,
                    );

                  return locationZones.map(
                    (zone) => (
                      <option
                        key={zone.id}
                        value={zone.id}
                      >
                        {location.name}
                        {" — "}
                        {zone.name}
                      </option>
                    ),
                  );
                })}
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}