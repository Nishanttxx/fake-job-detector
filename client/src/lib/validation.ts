export function validateJobDescription(value: string) {
  const description = value.trim();
  const issues: string[] = [];
  if (!description) issues.push("Add a job description so the model has enough context to assess the posting.");
  else if (description.length < 40) issues.push(`The description is only ${description.length} characters. Add at least 40 characters for a more reliable screen.`);
  else if (description.split(/\s+/).filter((word) => /[a-z]{2}/i.test(word)).length < 5) issues.push("The description needs more readable words. Paste the main responsibilities, pay, and requirements.");
  if (description.length > 12000) issues.push("The description is longer than 12,000 characters. Shorten it to the core role details and try again.");
  return issues;
}
