import { FormEvent, StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import { analyze, heatmap } from "./api/client";
import { MapView } from "./components/MapView";
import { RouteCard } from "./components/RouteCard";
import "./styles.css";
import type { Analysis, Heatmap } from "./types/api";

function App() {
  const [result, setResult] = useState<Analysis | null>(null);
  const [heatmapData, setHeatmapData] = useState<Heatmap | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [hour, setHour] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true);
    setError("");
    try {
      const analysis = await analyze({
        origin: { label: form.get("origin"), lat: Number(form.get("originLat")), lon: Number(form.get("originLon")) },
        destination: { label: form.get("destination"), lat: Number(form.get("destinationLat")), lon: Number(form.get("destinationLon")) },
        departure_time: new Date(String(form.get("departure"))).toISOString(),
        load_weight_lb: Number(form.get("weight")),
        sample_interval_miles: Number(form.get("interval")),
      });
      setResult(analysis);
      setSelectedId(analysis.recommended_route_id);
      setHeatmapData(await heatmap(analysis.analysis_id));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to analyze trip");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (result && !selectedId) setSelectedId(result.recommended_route_id);
  }, [result, selectedId]);

  return (
    <main className="app">
      <header className="site-header">
        <div className="brand">
          <span className="brand-mark">S</span>
          <div>
            <p className="eyebrow">Weather-aware logistics</p>
            <h1>StormRoute</h1>
          </div>
        </div>
        <p className="header-note">Safer decisions for every mile.</p>
      </header>
      <form className="trip-form" onSubmit={submit}>
        <div className="form-heading">
          <div>
            <p className="eyebrow">Plan a trip</p>
            <h2>Find your safest route</h2>
          </div>
          <span className="live-pill"><span /> Live weather data</span>
        </div>
        <div className="form-grid">
          <label className="field field-wide"><span>Origin</span><input name="origin" defaultValue="Dallas, TX" required /><input className="coordinate" name="originLat" type="number" step="any" defaultValue="32.7767" required /><input className="coordinate" name="originLon" type="number" step="any" defaultValue="-96.797" required /></label>
          <label className="field field-wide"><span>Destination</span><input name="destination" defaultValue="Denver, CO" required /><input className="coordinate" name="destinationLat" type="number" step="any" defaultValue="39.7392" required /><input className="coordinate" name="destinationLon" type="number" step="any" defaultValue="-104.9903" required /></label>
          <label className="field"><span>Departure</span><input name="departure" type="datetime-local" required /></label>
          <label className="field"><span>Load weight <small>lb</small></span><input name="weight" type="number" min="0" max="80000" defaultValue="20000" required /></label>
          <label className="field"><span>Weather sampling</span><select name="interval" defaultValue="25"><option value="10">Every 10 miles</option><option value="25">Every 25 miles</option><option value="50">Every 50 miles</option></select></label>
          <button className="primary-button" disabled={loading}>{loading ? "Analyzing trip…" : "Analyze routes"} <span aria-hidden="true">→</span></button>
        </div>
      </form>
      {error && <p className="message error">{error}</p>}
      {result && <>
        <section className="recommendation">
          <div className="recommendation-icon">✓</div>
          <div><p className="eyebrow">Recommended route</p><strong>{result.routes[0].label}</strong><span>{result.recommendation_reason}</span></div>
        </section>
        {result.warnings.map((warning) => <p className="message warning" key={warning}>{warning}</p>)}
        <div className="layout">
          <aside><div className="section-heading"><div><p className="eyebrow">Options</p><h2>Available routes</h2></div><span className="route-count">{result.routes.length}</span></div>{result.routes.map((route) => <RouteCard key={route.id} route={route} selected={route.id === selectedId} onSelect={() => setSelectedId(route.id)} />)}</aside>
          <section className="map-panel"><div className="map-header"><div><p className="eyebrow">Route overview</p><h2>Weather along the way</h2></div><span className="map-status"><span /> Heatmap active</span></div><MapView routes={result.routes} selectedId={selectedId} heatmap={heatmapData} hour={hour} /></section>
        </div>
        {heatmapData && <section className="heatmap-controls"><div className="heatmap-title"><div><p className="eyebrow">Forecast timeline</p><h2>Weather heatmap</h2></div><strong>+{hour}h</strong></div><label><span className="sr-only">Hours after departure</span><input type="range" min="0" max="48" value={hour} onChange={(event) => setHour(Number(event.target.value))} /><span className="range-labels"><span>Departure</span><span>48 hours</span></span></label><div className="heatmap-legend">{heatmapData.legend.map((label, index) => <span key={label}><i className={`legend-swatch legend-${index}`} />{label}</span>)}</div><small>All forecast frames are loaded once, so scrubbing stays instant.</small></section>}
      </>}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
