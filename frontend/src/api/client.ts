import type { Analysis, Heatmap, Place } from "../types/api";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? (Object.values(body.errors ?? {}).flat().join(" ") || "Request failed"));
  }
  return response.json() as Promise<T>;
}

export const analyze = (payload: unknown) =>
  request<Analysis>("/routes/analyze", { method: "POST", body: JSON.stringify(payload) });

export const heatmap = (id: string) => request<Heatmap>(`/analyses/${id}/heatmap`);

export const geocode = (query: string) =>
  request<{ results: Place[] }>(`/geocode?q=${encodeURIComponent(query)}`);
