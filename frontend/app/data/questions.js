// questions.js —
// All questions, answer options, branching logic, and score conversion tables.

export const CLB_CONVERSION = {
  CELPIP: {
    convert: (score) => {
      const n = parseInt(score);
      if (isNaN(n)) return null;
      if (n >= 12) return 12;
      if (n >= 4) return n;
      return null;
    },
    range: "4–12",
    hint: "e.g. 9",
  },

  IELTS: {
    convert: (score, ability) => {
      const s = parseFloat(score);
      if (isNaN(s)) return null;
      const tables = {
        listening: [
          [10.0, 12],
          [9.0, 11],
          [8.5, 10],
          [8.0, 9],
          [7.5, 8],
          [6.0, 7],
          [5.5, 6],
          [5.0, 5],
          [4.5, 4],
        ],
        reading: [
          [8.5, 12],
          [8.0, 11],
          [7.5, 10],
          [7.0, 9],
          [6.5, 8],
          [6.0, 7],
          [5.0, 6],
          [4.0, 5],
          [3.5, 4],
        ],
        writing: [
          [7.5, 12],
          [7.0, 11],
          [6.5, 10],
          [6.0, 9],
          [5.5, 8],
          [5.0, 7],
          [4.5, 6],
          [4.0, 5],
          [3.5, 4],
        ],
        speaking: [
          [8.5, 12],
          [8.0, 11],
          [7.5, 10],
          [7.0, 9],
          [6.5, 8],
          [6.0, 7],
          [5.5, 6],
          [5.0, 5],
          [4.0, 4],
        ],
      };
      const table = tables[ability?.toLowerCase()];
      if (!table) return null;
      for (const [min, clb] of table) {
        if (s >= min) return clb;
      }
      return null;
    },
    range: "0–9",
    hint: "e.g. 7.5",
  },

  TEF: {
    convert: (score, ability) => {
      const n = parseInt(score);
      if (isNaN(n)) return null;
      const tables = {
        listening: [
          [298, 10],
          [249, 9],
          [217, 8],
          [181, 7],
          [145, 6],
          [121, 5],
          [0, 4],
        ],
        reading: [
          [263, 10],
          [248, 9],
          [233, 8],
          [207, 7],
          [181, 6],
          [151, 5],
          [0, 4],
        ],
        writing: [
          [393, 10],
          [371, 9],
          [349, 8],
          [310, 7],
          [271, 6],
          [226, 5],
          [0, 4],
        ],
        speaking: [
          [415, 10],
          [393, 9],
          [371, 8],
          [349, 7],
          [310, 6],
          [271, 5],
          [0, 4],
        ],
      };
      const table = tables[ability?.toLowerCase()];
      if (!table) return null;
      for (const [min, nclc] of table) {
        if (n >= min) return nclc;
      }
      return null;
    },
    range: "varies by section",
    hint: "Enter your section score",
  },

  TCF: {
    convert: (score, ability) => {
      const n = parseInt(score);
      if (isNaN(n)) return null;
      const tables = {
        listening: [
          [549, 10],
          [523, 9],
          [503, 8],
          [458, 7],
          [398, 6],
          [331, 5],
          [0, 4],
        ],
        reading: [
          [549, 10],
          [524, 9],
          [499, 8],
          [453, 7],
          [406, 6],
          [375, 5],
          [0, 4],
        ],
        writing: [
          [16, 10],
          [14, 9],
          [12, 8],
          [10, 7],
          [7, 6],
          [4, 5],
          [0, 4],
        ],
        speaking: [
          [16, 10],
          [14, 9],
          [12, 8],
          [10, 7],
          [7, 6],
          [4, 5],
          [0, 4],
        ],
      };
      const table = tables[ability?.toLowerCase()];
      if (!table) return null;
      for (const [min, nclc] of table) {
        if (n >= min) return nclc;
      }
      return null;
    },
    range: "varies by section",
    hint: "Enter your section score",
  },
};

export const EDUCATION_OPTIONS = [
  { label: "Less than high school", value: "less_than_high_school" },
  { label: "High school diploma", value: "high_school" },
  { label: "1-year post-secondary", value: "one_year" },
  { label: "2-year post-secondary", value: "two_year" },
  { label: "Bachelor's / 3+ year degree", value: "bachelors" },
  { label: "Two or more certificates", value: "two_or_more" },
  { label: "Master's / professional degree", value: "masters" },
  { label: "PhD", value: "phd" },
];

export const CANADIAN_EXPERIENCE_OPTIONS = [
  { label: "None", value: 0 },
  { label: "1 year", value: 1 },
  { label: "2 years", value: 2 },
  { label: "3 years", value: 3 },
  { label: "4 years", value: 4 },
  { label: "5+ years", value: 5 },
];

export const FOREIGN_EXPERIENCE_OPTIONS = [
  { label: "None", value: 0 },
  { label: "1–2 years", value: 1 },
  { label: "3+ years", value: 3 },
];

export const LANGUAGE_TEST_OPTIONS = [
  { label: "CELPIP (English)", value: "CELPIP" },
  { label: "IELTS (English)", value: "IELTS" },
  { label: "TEF Canada (French)", value: "TEF" },
  { label: "TCF Canada (French)", value: "TCF" },
  { label: "I haven't taken a test", value: "none" },
];

export const SECOND_LANGUAGE_TEST_OPTIONS = [
  { label: "CELPIP (English)", value: "CELPIP" },
  { label: "IELTS (English)", value: "IELTS" },
  { label: "TEF Canada (French)", value: "TEF" },
  { label: "TCF Canada (French)", value: "TCF" },
  { label: "No second language test", value: "none" },
];

export const QUESTIONS = [
  // 0. Current location / immigration status
  {
    id: "immigration_status",
    message: "Let's start! Are you currently in Canada or outside Canada?",
    type: "options",
    options: [
      { label: "I'm outside Canada", value: "outside_canada" },
      { label: "I'm in Canada on a study permit", value: "study_permit" },
      { label: "I'm in Canada on a work permit / PGWP", value: "work_permit" },
      { label: "I'm in Canada with other status", value: "other" },
    ],
    next: (profile) =>
      profile.immigration_status === "work_permit"
        ? "work_permit_expiry"
        : "marital_status",
  },

  // 0b. Work permit expiry (only if on work permit)
  {
    id: "work_permit_expiry",
    message: "How many months do you have left on your work permit?",
    type: "options",
    options: [
      { label: "Less than 6 months", value: "less_than_6" },
      { label: "6–12 months", value: "6_to_12" },
      { label: "1–2 years", value: "1_to_2_years" },
      { label: "2+ years", value: "2_plus_years" },
    ],
    next: () => "marital_status",
  },
  // 1. Marital status
  {
    id: "marital_status",
    message:
      "Let's start! Are you applying with a spouse or common-law partner?",
    type: "options",
    options: [
      { label: "Single / divorced / widowed", value: "single" },
      {
        label: "Married or common-law partner (coming to Canada)",
        value: "married_accompanying",
      },
      {
        label: "Married or common-law partner (not coming to Canada)",
        value: "married_not_accompanying",
      },
    ],
    next: () => "age",
  },

  // 2. Age
  {
    id: "age",
    message: "How old are you?",
    type: "text",
    inputHint: "Enter your age",
    validate: (val) => {
      const n = parseInt(val);
      if (isNaN(n) || n < 18 || n > 100)
        return "Please enter a valid age (18–100)";
      return null;
    },
    next: () => "education",
  },

  // 3. Education
  {
    id: "education",
    message: "What is your highest level of completed education?",
    note: (profile) =>
      profile.immigration_status === "study_permit"
        ? "Do not include the studies you are currently enrolled in."
        : null,
    type: "options",
    options: EDUCATION_OPTIONS,
    next: (profile) =>
      profile.marital_status === "married_accompanying"
        ? "spouse_education"
        : "first_language_test",
  },

  // 4. Spouse education
  {
    id: "spouse_education",
    message: "What is your spouse or partner's highest level of education?",
    type: "options",
    options: EDUCATION_OPTIONS,
    next: () => "first_language_test",
  },

  // 5. First language test
  {
    id: "first_language_test",
    message:
      "Which official language test have you taken for your first language?",
    type: "options",
    options: LANGUAGE_TEST_OPTIONS,
    next: (profile) =>
      profile.first_language_test === "none"
        ? "second_language_test"
        : "first_language_scores",
  },

  // 6. First language scores
  {
    id: "first_language_scores",
    message: null,
    type: "score_input",
    abilities: ["speaking", "listening", "reading", "writing"],
    next: (profile) =>
      profile.marital_status === "married_accompanying"
        ? "spouse_language_test"
        : "second_language_test",
  },

  // 7. Spouse language test
  {
    id: "spouse_language_test",
    message: "Has your spouse or partner taken an official language test?",
    type: "options",
    options: SECOND_LANGUAGE_TEST_OPTIONS,
    next: (profile) =>
      profile.spouse_language_test === "none"
        ? "second_language_test"
        : "spouse_language_scores",
  },

  // 8. Spouse language scores
  {
    id: "spouse_language_scores",
    message: null,
    type: "score_input",
    abilities: ["speaking", "listening", "reading", "writing"],
    next: () => "second_language_test",
  },

  // 9. Second language test
  {
    id: "second_language_test",
    message:
      "Have you taken a test in a second official language? (e.g. French if your first test was English)",
    type: "options",
    options: SECOND_LANGUAGE_TEST_OPTIONS,
    next: (profile) =>
      profile.second_language_test === "none"
        ? "canadian_experience"
        : "second_language_scores",
  },

  // 10. Second language scores
  {
    id: "second_language_scores",
    message: null,
    type: "score_input",
    abilities: ["speaking", "listening", "reading", "writing"],
    next: () => "canadian_experience",
  },

  // 11. Canadian work experience
  {
    id: "canadian_experience",
    message:
      "How many years of skilled Canadian work experience do you have in the last 10 years?",
    note: (profile) =>
      profile.immigration_status === "study_permit"
        ? "Only count full-time skilled work (NOC 0, A, or B). Co-op placements and part-time work do not qualify. If you are still studying, select None."
        : null,
    type: "options",
    options: CANADIAN_EXPERIENCE_OPTIONS,
    next: (profile) => {
      if (profile.canadian_experience > 0) return "canadian_noc";
      return profile.marital_status === "married_accompanying"
        ? "spouse_canadian_experience"
        : "foreign_experience";
    },
  },

  // 12. Canadian NOC level (only if canadian_experience > 0)
  {
    id: "canadian_noc",
    message: "What is the skill level of your Canadian job(s)?",
    type: "options",
    options: [
      { label: "NOC 0 — Manager / executive", value: "0" },
      { label: "NOC A — Professional (needs a degree)", value: "A" },
      { label: "NOC B — Technical / skilled trade", value: "B" },
      { label: "NOC C or D — Semi or low-skilled", value: "CD" },
    ],
    next: (profile) =>
      profile.marital_status === "married_accompanying"
        ? "spouse_canadian_experience"
        : "foreign_experience",
  },

  // 13. Spouse Canadian work experience
  {
    id: "spouse_canadian_experience",
    message:
      "How many years of Canadian work experience does your spouse or partner have?",
    type: "options",
    options: CANADIAN_EXPERIENCE_OPTIONS,
    next: () => "foreign_experience",
  },

  // 14. Foreign work experience
  {
    id: "foreign_experience",
    message:
      "How many years of skilled foreign work experience do you have in the last 10 years?",
    type: "options",
    options: FOREIGN_EXPERIENCE_OPTIONS,
    next: (profile) => {
      if (profile.foreign_experience > 0) return "foreign_noc";
      return "trade_certificate";
    },
  },

  // 15. Foreign work noc
  {
    id: "foreign_noc",
    message: "What is the skill level of your foreign job(s)?",
    type: "options",
    options: [
      { label: "NOC 0 — Manager / executive", value: "0" },
      { label: "NOC A — Professional (needs a degree)", value: "A" },
      { label: "NOC B — Technical / skilled trade", value: "B" },
      { label: "NOC C or D — Semi or low-skilled", value: "CD" },
    ],
    next: () => "trade_certificate",
  },

  // 16. Trade certificate
  {
    id: "trade_certificate",
    message: "Do you have a valid trade certificate (Red Seal or provincial)?",
    type: "options",
    options: [
      { label: "Yes", value: true },
      { label: "No", value: false },
    ],
    next: () => "canadian_education",
  },

  // 17. Canadian education
  {
    id: "canadian_education",
    message: "Did you complete any post-secondary education in Canada?",
    note: (profile) =>
      profile.immigration_status === "study_permit"
        ? "Only count completed Canadian degrees or diplomas. Do not include studies currently in progress."
        : null,
    type: "options",
    options: [
      { label: "No", value: "none" },
      { label: "1–2 years", value: "one_two_years" },
      { label: "3+ years", value: "three_plus_years" },
    ],
    next: (profile) =>
      profile.immigration_status === "study_permit"
        ? "current_canadian_study"
        : "sibling_in_canada",
  },

  // 17b. Current Canadian study (only for User B)
  {
    id: "current_canadian_study",
    message: "What program are you currently studying in Canada?",
    note: () =>
      "This helps us calculate your projected CRS score after graduation.",
    type: "options",
    options: [
      {
        label: "1–2 year college diploma or graduate certificate",
        value: "one_two_years",
      },
      { label: "3–4 year bachelor's degree", value: "three_plus_years" },
      { label: "Master's degree", value: "masters" },
      { label: "PhD", value: "phd" },
    ],
    next: () => "sibling_in_canada",
  },

  // 18. Sibling in Canada
  {
    id: "sibling_in_canada",
    message:
      "Do you have a brother or sister in Canada who is a Canadian citizen or permanent resident? (You must be 18+, and so must they)",
    type: "options",
    options: [
      { label: "Yes", value: true },
      { label: "No", value: false },
    ],
    next: () => "job_offer",
  },

  // 19. Job offer
  {
    id: "job_offer",
    message: "Do you have a valid job offer from a Canadian employer?",
    type: "options",
    options: [
      { label: "Yes", value: true },
      { label: "No", value: false },
    ],
    next: () => "provincial_nomination",
  },

  // 20. Provincial nomination
  {
    id: "provincial_nomination",
    message: "Have you received a provincial nomination (PNP)?",
    type: "options",
    options: [
      { label: "Yes", value: true },
      { label: "No", value: false },
    ],
    next: () => null,
  },
];

export function getQuestion(id) {
  return QUESTIONS.find((q) => q.id === id) ?? null;
}

export function getFirstQuestionId() {
  return "immigration_status";
}

export function getScoreMessage(questionId, profile) {
  const testKey =
    questionId === "first_language_scores"
      ? "first_language_test"
      : questionId === "spouse_language_scores"
        ? "spouse_language_test"
        : questionId === "second_language_scores"
          ? "second_language_test"
          : null;

  const test = testKey ? profile[testKey] : null;
  if (!test) return "Please enter your language test scores.";

  const testInfo = CLB_CONVERSION[test];
  const label =
    questionId === "spouse_language_scores" ? "your spouse's" : "your";
  return `Enter ${label} ${test} scores for each ability. (${testInfo?.range ?? ""})`;
}

export function convertScoresToCLB(test, scores) {
  const converter = CLB_CONVERSION[test];
  if (!converter) return null;

  const clb = {};
  for (const ability of ["speaking", "listening", "reading", "writing"]) {
    const raw = scores[ability];
    if (raw === undefined || raw === null) return null;
    const result =
      test === "CELPIP"
        ? converter.convert(raw)
        : converter.convert(raw, ability);
    if (result === null) return null;
    clb[ability] = result;
  }
  return clb;
}

export function isFlowComplete(profile) {
  return profile.provincial_nomination !== undefined;
}
