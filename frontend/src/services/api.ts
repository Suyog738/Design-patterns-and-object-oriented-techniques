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