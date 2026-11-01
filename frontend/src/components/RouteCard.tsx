import type { Route } from "../types/api";

export function RouteCard({ route, selected, onSelect }: { route: Route; selected: boolean; onSelect: () => void }) {
  return (
    <button className={`route-card ${selected ? "selected" : ""}`} onClick={onSelect}>
      <span className="route-card-top"><span className="route-title">{route.label}</span>{route.rank === 1 && <span className="best-badge">Best</span>}</span>
      <span className="route-meta"><span>{route.distance_miles} mi</span><span>{Math.round(route.duration_minutes)} min</span></span>
      <span className="route-risk"><span className={`risk-dot risk-${route.summary.max_risk.toLowerCase().replace(" ", "-")}`} />{route.summary.max_risk}<span className="risk-score">Avg {route.summary.average_risk.toFixed(2)}</span></span>
      <span className="route-exposure"><span>Severe <b>{route.summary.severe_miles} mi</b></span><span>High <b>{route.summary.high_miles} mi</b></span></span>
    </button>
  );
}
