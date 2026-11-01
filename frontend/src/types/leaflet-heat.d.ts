import "leaflet";

declare module "leaflet" {
  interface HeatLayer extends Layer {
    setLatLngs(latlngs: Array<[number, number, number]>): this;
  }

  interface HeatLayerOptions {
    radius?: number;
    blur?: number;
    maxZoom?: number;
    max?: number;
    minOpacity?: number;
    gradient?: Record<number, string>;
  }

  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: HeatLayerOptions,
  ): HeatLayer;
}

