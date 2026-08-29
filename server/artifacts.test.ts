import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

describe("trained artifacts", () => {
  it("contains source coverage, tuning ranges, and evaluation outputs", () => {
    const overview = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), "artifacts/overview.json"), "utf8"));
    expect(overview.source_files).toEqual(expect.arrayContaining(["processed_labeled_dataset_without_encoding.xlsx", "preprocessed_unlabelled_data_bert.xlsx"]));
    expect(overview.training.raw_rows).toBe(54391);
    expect(overview.training.unlabelled_rows).toBe(126549);
    expect(overview.tuning.multinomial_nb.alpha).toEqual([0.1, 0.5, 1, 2]);
    expect(overview.results.some((row: any) => row.features === "TF-IDF + structured")).toBe(true);
  });

  it("contains a portable vectorizer and coefficient bundle", () => {
    const bundle = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), "artifacts/model_bundle.json"), "utf8"));
    expect(bundle.target).toBe("fraudulent");
    expect(Object.keys(bundle.vectorizer.vocabulary).length).toBeGreaterThan(100);
    expect(bundle.vectorizer.idf.length).toBe(bundle.model.coef.length);
    expect(bundle.warning_signals.length).toBeGreaterThanOrEqual(4);
  });
});
