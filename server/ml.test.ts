import { describe, expect, it } from "vitest";
import { normalizeText, predictPosting } from "./ml";

describe("fake-job inference", () => {
  it("normalizes markup, URLs, and whitespace without dropping signal terms", () => {
    expect(normalizeText("<b>URGENT</b>   https://example.com")).toBe("urgent urltoken");
  });

  it("returns a bounded probability and explainable matched signals", () => {
    const result = predictPosting({
      job_title: "Work from home opportunity",
      job_desc: "Immediate hiring. Earn 5000week. No degree required. Contact now.",
      skills_desc: "Flexible hours and quick money.",
    });
    expect(result.probability).toBeGreaterThanOrEqual(0);
    expect(result.probability).toBeLessThanOrEqual(1);
    expect(result.legitimateProbability).toBeGreaterThanOrEqual(0);
    expect(result.signals.length).toBeGreaterThan(0);
    expect(result.signals.some((signal) => signal.id === "urgency")).toBe(true);
  });
});
