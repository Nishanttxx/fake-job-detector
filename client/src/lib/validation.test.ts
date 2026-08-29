import { describe, expect, it } from "vitest";
import { validateJobDescription } from "./validation";

describe("validateJobDescription", () => {
  it("explains why an empty description cannot be screened", () => {
    expect(validateJobDescription(" ")).toEqual(["Add a job description so the model has enough context to assess the posting."]);
  });

  it("rejects short or low-information descriptions", () => {
    expect(validateJobDescription("urgent hire")[0]).toContain("only 11 characters");
    expect(validateJobDescription("123 456 789 000 111")[0]).toContain("more readable words");
  });

  it("accepts a useful description and rejects oversized input", () => {
    expect(validateJobDescription("Join our customer support team in a full-time role with transparent pay, training, and clear responsibilities.")).toEqual([]);
    expect(validateJobDescription("word ".repeat(2401)).some((issue) => issue.includes("12,000"))).toBe(true);
  });
});
