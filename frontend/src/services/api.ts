const API_BASE_URL = "http://127.0.0.1:8000";

export interface HealthResponse {
  status: string;
  db?: string;
}

export interface Sensor {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
}

export type DeviceFamily = "simulation" | "edge";

export interface DeviceDto {
  id: string;
  device_type: string;
  role: string;
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
  zone_id: string | null;
  location_id: string | null;
}

export interface LocationDto {
  id: string;
  name: string;
}

export interface ZoneDto {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
}

export interface LocationConfigDto {
  location: LocationDto;
  zones: ZoneDto[];
}

export interface ZoneConfigRequest {
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
}

export interface BuildLocationConfigRequest {
  location_name: string;
  zones: ZoneConfigRequest[];
}

export interface ZoneAssignmentRequest {
  zone_id: string | null;
}

async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Request failed.";

    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        detail = data.detail;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/* ---------------- Health ---------------- */

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/* ---------------- Sensors ---------------- */

export async function fetchSensors(): Promise<Sensor[]> {
  return request<Sensor[]>("/api/sensors");
}

export async function createSensor(
  type: "moisture" | "light",
  displayName: string,
): Promise<Sensor> {
  return request<Sensor>("/api/sensors", {
    method: "POST",
    body: JSON.stringify({
      type,
      display_name: displayName,
    }),
  });
}

/* ---------------- Devices ---------------- */

export async function fetchDevices(
  family?: DeviceFamily,
): Promise<DeviceDto[]> {
  const query = family
    ? `?family=${encodeURIComponent(family)}`
    : "";

  return request<DeviceDto[]>(`/api/devices${query}`);
}

export async function provisionDeviceFamily(
  family: DeviceFamily,
): Promise<DeviceDto[]> {
  return request<DeviceDto[]>(
    `/api/devices/provision?family=${encodeURIComponent(family)}`,
    {
      method: "POST",
    },
  );
}

/* ---------------- Locations ---------------- */

export async function fetchLocations(): Promise<LocationDto[]> {
  return request<LocationDto[]>("/api/locations");
}

export async function createLocationConfig(
  data: BuildLocationConfigRequest,
): Promise<LocationConfigDto> {
  return request<LocationConfigDto>("/api/locations/config", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchLocationConfig(
  locationId: string,
): Promise<LocationConfigDto> {
  return request<LocationConfigDto>(
    `/api/locations/${locationId}/config`,
  );
}

export async function deleteLocation(
  locationId: string,
): Promise<void> {
  await request<void>(`/api/locations/${locationId}`, {
    method: "DELETE",
  });
}

/* ---------------- Zones ---------------- */

export async function addZone(
  locationId: string,
  zone: ZoneConfigRequest,
): Promise<ZoneDto> {
  return request<ZoneDto>(
    `/api/locations/${locationId}/zones`,
    {
      method: "POST",
      body: JSON.stringify(zone),
    },
  );
}

export async function updateZone(
  locationId: string,
  zoneId: string,
  zone: ZoneConfigRequest,
): Promise<ZoneDto> {
  return request<ZoneDto>(
    `/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "PATCH",
      body: JSON.stringify(zone),
    },
  );
}

export async function deleteZone(
  locationId: string,
  zoneId: string,
): Promise<void> {
  await request<void>(
    `/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "DELETE",
    },
  );
}

/* ---------------- Device assignment ---------------- */

export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<void> {
  await request<void>(
    `/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  );
}

export async function fetchZoneDevices(
  locationId: string,
  zoneId: string,
): Promise<DeviceDto[]> {
  return request<DeviceDto[]>(
    `/api/locations/${locationId}/zones/${zoneId}/devices`,
  );
}

