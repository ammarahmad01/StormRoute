import { MapContainer, Polyline, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import type { Heatmap, Route } from "../types/api";
import { HeatLayer } from "./HeatLayer";

const colors = { Low: "#2e9d57", Moderate: "#e1a326", High: "#ed762c", Severe: "#d33c3c", "No Travel": "#702080" };

export function MapView({ routes, selectedId, heatmap, hour }: { routes: Route[]; selectedId: string; heatmap: Heatmap | null; hour: number }) {
  const selected = routes.find((route) => route.id === selectedId) ?? routes[0];
  const center: [number, number] = selected?.geometry[0] ?? [39, -98];
  return (
    <MapContainer center={center} zoom={5} className="map">
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {heatmap && <HeatLayer data={heatmap} hour={hour} />}
      {routes.map((route) => (
        <Polyline key={route.id} positions={route.geometry} pathOptions={{ color: route.id === selectedId ? colors[route.summary.max_risk] : "#8a93a3", weight: route.id === selectedId ? 6 : 3, opacity: route.id === selectedId ? 1 : 0.65 }} />
      ))}
      {selected?.checkpoints.map((checkpoint) => (
        <CircleMarker key={checkpoint.index} center={[checkpoint.lat, checkpoint.lon]} radius={6} pathOptions={{ color: checkpoint.risk ? colors[checkpoint.risk.overall] : "#7c8798" }}>
          <Popup>
            <strong>{checkpoint.risk?.overall ?? "Forecast unavailable"}</strong>
            <br />ETA: {new Date(checkpoint.eta).toLocaleString()}
            {checkpoint.weather.wind_mph !== undefined && <><br />Wind: {checkpoint.weather.wind_mph} mph</>}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
