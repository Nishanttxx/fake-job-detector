import { describe, expect, it } from "vitest";
import { validateJobDescription } from "../client/src/lib/validation";

describe("screening description validation", () => {
  it("reports a useful empty-input error", () => {
    expect(validateJobDescription(" ")[0]).toContain("Add a job description");
  });

  it("rejects short and low-information text", () => {
    expect(validateJobDescription("urgent hire")[0]).toContain("only 11 characters");
    expect(validateJobDescription("123 456 789 000 111 ".repeat(3))[0]).toContain("more readable words");
  });

  it("accepts realistic content and rejects oversized content", () => {
    expect(validateJobDescription("Join our customer support team in a full-time role with transparent pay, training, and clear responsibilities.")).toEqual([]);
    expect(validateJobDescription("word ".repeat(2401)).some((issue) => issue.includes("12,000"))).toBe(true);
  });
});
