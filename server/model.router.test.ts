import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function context(): TrpcContext {
  return { user: null, req: {} as TrpcContext["req"], res: {} as TrpcContext["res"] };
}

describe("model procedures", () => {
  it("returns persisted overview metadata and evaluated candidates", async () => {
    const overview = await appRouter.createCaller(context()).model.overview();
    expect(overview.training.raw_rows).toBe(54391);
    expect(overview.results.length).toBeGreaterThanOrEqual(5);
    expect(overview.selectedModel.model).toBe("Logistic Regression");
  });

  it("scores an unseen posting and returns explainability fields", async () => {
    const result = await appRouter.createCaller(context()).model.predict({ job_title: "Operations coordinator", job_desc: "Join our team with transparent pay and a clear interview process." });
    expect(["Legitimate", "Fraudulent"]).toContain(result.label);
    expect(result.probability + result.legitimateProbability).toBeCloseTo(1, 3);
    expect(result.model).toBe("Logistic Regression");
  });

  it("rejects malformed prediction input", async () => {
    await expect(appRouter.createCaller(context()).model.predict({ job_title: 42 } as never)).rejects.toThrow();
  });
});
