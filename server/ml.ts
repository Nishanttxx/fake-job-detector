import fs from "node:fs";
import path from "node:path";

export type PostingInput = {
  job_title?: string;
  location?: string;
  industry?: string;
  salary_range?: string;
  company_profile?: string;
  job_desc?: string;
  skills_desc?: string;
  employment_type?: string;
  text?: string;
};

type Signal = { id: string; label: string; terms: string[]; weight: number };
type Bundle = {
  version: string;
  target: string;
  label_map: Record<string, string>;
  text_columns: string[];
  vectorizer: { vocabulary: Record<string, number>; idf: number[]; ngram_range: number[]; max_features: number };
  model: { name: string; features: string; coef: number[]; intercept: number; threshold: number; best_params: Record<string, unknown> };
  training: Record<string, number>;
  results: Array<Record<string, unknown>>;
  warning_signals: Signal[];
};

let cached: Bundle | null = null;
const recent: Array<{ id: string; title: string; label: string; probability: number; createdAt: string }> = [];

function loadBundle(): Bundle {
  if (!cached) {
    const file = path.resolve(process.cwd(), "artifacts/model_bundle.json");
    cached = JSON.parse(fs.readFileSync(file, "utf8")) as Bundle;
  }
  return cached;
}

export function normalizeText(value: unknown): string {
  return String(value ?? "").toLowerCase().replace(/<[^>]+>/g, " ").replace(/https?:\/\/\S+|www\.\S+/g, " urltoken ").replace(/\s+/g, " ").trim();
}

export function composeText(input: PostingInput): string {
  const b = loadBundle();
  return b.text_columns.map((column) => normalizeText(input[column as keyof PostingInput])).filter(Boolean).join(" ");
}

function tokens(text: string): string[] {
  return text.match(/[\w$@.-]{2,}/g) ?? [];
}

function sigmoid(value: number): number {
  return 1 / (1 + Math.exp(-Math.max(-30, Math.min(30, value))));
}

export function predictPosting(input: PostingInput) {
  const bundle = loadBundle();
  const text = composeText(input);
  const words = tokens(text);
  const counts = new Map<string, number>();
  for (let i = 0; i < words.length; i += 1) {
    const candidates = [words[i]];
    if (i < words.length - 1) candidates.push(`${words[i]} ${words[i + 1]}`);
    for (const candidate of candidates) counts.set(candidate, (counts.get(candidate) ?? 0) + 1);
  }
  const vector = new Array(bundle.model.coef.length).fill(0) as number[];
  let norm = 0;
  for (const [term, count] of Array.from(counts.entries())) {
    const index = bundle.vectorizer.vocabulary[term];
    if (index === undefined) continue;
    const value = (1 + Math.log(count)) * (bundle.vectorizer.idf[index] ?? 1);
    vector[index] = value;
    norm += value * value;
  }
  norm = Math.sqrt(norm) || 1;
  const score = bundle.model.intercept + vector.reduce((sum, value, index) => sum + (value / norm) * (bundle.model.coef[index] ?? 0), 0);
  const probability = sigmoid(score);
  const signals = bundle.warning_signals.filter((signal) => signal.terms.some((term) => text.includes(term))).map((signal) => ({ id: signal.id, label: signal.label, matched: signal.terms.filter((term) => text.includes(term)), impact: signal.weight }));
  const label = probability >= bundle.model.threshold ? "Fraudulent" : "Legitimate";
  const title = normalizeText(input.job_title || input.text).slice(0, 68) || "Untitled posting";
  recent.unshift({ id: `${Date.now()}`, title, label, probability: Number(probability.toFixed(4)), createdAt: new Date().toISOString() });
  recent.splice(8);
  return { label, probability: Number(probability.toFixed(4)), legitimateProbability: Number((1 - probability).toFixed(4)), signals, textLength: text.length, model: bundle.model.name, modelVersion: bundle.version };
}

export function getOverview() {
  const bundle = loadBundle();
  return { training: bundle.training, results: bundle.results, selectedModel: bundle.results[0], warningSignals: bundle.warning_signals, recentPredictions: recent, model: bundle.model, version: bundle.version };
}
