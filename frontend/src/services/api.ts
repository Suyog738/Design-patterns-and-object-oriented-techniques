const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export type HealthResponse = {
  status: string;
  db: "ok" | "fail";
};

export type Sensor = {
  id: string;
  device_type: string;
  display_name: string | null;
  default_config: Record<string, unknown>;
};

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("Health check failed");
  }

  return response.json();
}

export async function fetchSensors(): Promise<Sensor[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to fetch sensors");
  }

  return response.json();
}

export async function createSensor(
  type: "moisture" | "light",
  displayName: string
): Promise<Sensor> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create sensor");
  }

  return response.json();
}

export type DeviceFamily = "simulation" | "edge";

export type DeviceRole = "sensor" | "actuator";

export interface DeviceDto {
  id: string;
  device_type: string;
  role: DeviceRole;
  device_family: DeviceFamily;
  display_name: string;
  default_config: Record<string, unknown>;
}

export async function fetchDevices(
  family?: DeviceFamily,
  role?: DeviceRole,
): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.set("family", family);
  }

  if (role) {
    params.set("role", role);
  }

  const query = params.toString();

  const response = await fetch(
    `${API_BASE_URL}/api/devices${query ? `?${query}` : ""}`,
  );

  if (!response.ok) {
    throw new Error("Failed to fetch devices");
  }

  return response.json();
}


export async function provisionDeviceFamily(
  family: DeviceFamily,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${family}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to provision device family");
  }

  return response.json();
}