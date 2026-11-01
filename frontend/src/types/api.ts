export type RiskLabel = "Low" | "Moderate" | "High" | "Severe" | "No Travel";

export interface Place {
  label: string;
  lat: number;
  lon: number;
}

export interface Checkpoint {
  index: number;
  distance_miles: number;
  lat: number;
  lon: number;
  eta: string;
  segment_miles: number;
  weather: {
    wind_mph?: number;
    gust_mph?: number;
    rain_in_hr?: number;
    snow_in_hr?: number;
    forecast_unavailable?: boolean;
  };
  risk: { overall: RiskLabel; score: number; dominant_factor: string | null } | null;
}

export interface Route {
  id: string;
  label: string;
  distance_miles: number;
  duration_minutes: number;
  geometry: [number, number][];
  rank: number;
  summary: {
    no_travel_miles: number;
    severe_miles: number;
    high_miles: number;
    moderate_miles: number;
    low_miles: number;
    average_risk: number;
    max_risk: RiskLabel;
    blocked: boolean;
  };
  checkpoints: Checkpoint[];
}

export interface Analysis {
  analysis_id: string;
  recommended_route_id: string;
  recommendation_reason: string;
  warnings: string[];
  routes: Route[];
}

export interface Heatmap {
  start_time: string;
  hours: number;
  points: [number, number][];
  frames: number[][];
  legend: RiskLabel[];
}

