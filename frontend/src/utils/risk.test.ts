import { describe, expect, it } from "vitest";

import { riskToColor } from "./risk";

describe("riskToColor", () => {
  it("maps every risk level to a visible color", () => {
    expect(riskToColor("Low")).toBe("#2e9d57");
    expect(riskToColor("Moderate")).toBe("#e1a326");
    expect(riskToColor("High")).toBe("#ed762c");
    expect(riskToColor("Severe")).toBe("#d33c3c");
    expect(riskToColor("No Travel")).toBe("#702080");
  });
});
