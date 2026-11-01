import type { RiskLabel } from "../types/api";

export function riskToColor(risk: RiskLabel): string {
  return {
    Low: "#2e9d57",
    Moderate: "#e1a326",
    High: "#ed762c",
    Severe: "#d33c3c",
    "No Travel": "#702080",
  }[risk];
}

