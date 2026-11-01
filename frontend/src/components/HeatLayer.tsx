import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";

import type { Heatmap } from "../types/api";

const heatOptions: L.HeatLayerOptions = {
  radius: 34,
  blur: 26,
  maxZoom: 8,
  max: 1,
  minOpacity: 0.28,
  gradient: {
    0.15: "#37a88d",
    0.35: "#e0b547",
    0.6: "#ec8040",
    0.8: "#d84b58",
    1: "#74429b",
  },
};

function pointsForHour(data: Heatmap, hour: number): Array<[number, number, number]> {
  const frame = data.frames[Math.min(hour, data.frames.length - 1)] ?? [];
  return data.points.map(([lat, lon], index) => {
    const score = frame[index] ?? 0;
    return [lat, lon, Math.max(0.12, score / 4)] as [number, number, number];
  });
}

export function HeatLayer({ data, hour }: { data: Heatmap; hour: number }) {
  const map = useMap();
  const layerRef = useRef<L.HeatLayer | null>(null);

  useEffect(() => {
    if (!data.points.length) return;

    const layer = L.heatLayer(pointsForHour(data, 0), heatOptions);
    layer.addTo(map);
    layerRef.current = layer;

    return () => {
      map.removeLayer(layer);
      layerRef.current = null;
    };
  }, [data, map]);

  useEffect(() => {
    const layer = layerRef.current;
    if (!layer || hour === 0 || !map.hasLayer(layer)) return;
    layer.setLatLngs(pointsForHour(data, hour));
  }, [data, hour]);

  return null;
}
