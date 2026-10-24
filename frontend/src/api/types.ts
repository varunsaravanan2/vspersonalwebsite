/*
  TypeScript types for the data the API returns.

  These mirror the Pydantic schemas in backend/app/schemas.py one-to-one.
  With them, TypeScript catches mistakes like `project.titel` while I'm typing,
  instead of the page silently showing "undefined" at runtime.

  If the backend schemas change, these must be updated too. A later upgrade
  is generating this file automatically from the backend's OpenAPI spec (/openapi.json).
*/

// A "union of string literals": the type only allows these exact values,
// matching the enums in backend/app/models.py.
export type SkillType = 'attack' | 'shield' | 'grab' | 'neutral'
export type SkillRank = 'novice' | 'advanced' | 'ace' | 'legend'
export type ExperienceKind = 'school' | 'job' | 'club'

export interface Move {
  input: string // e.g. "Neutral B"
  name: string
  description: string
}

/** One tile on the character select grid (GET /api/projects). */
export interface ProjectSummary {
  slug: string
  name: string
  tagline: string
  stack: string[]
  portrait_url: string | null // null = no screenshot yet
}

/**
 * A full fighter page (GET /api/projects/:slug).
 * `extends` reuses every ProjectSummary field, same as the Python inheritance.
 */
export interface ProjectDetail extends ProjectSummary {
  moves: Move[]
  stats: Record<string, number> // e.g. { complexity: 60, fun: 90 }
  repo_url: string | null
  demo_url: string | null
}

export interface Skill {
  name: string
  type: SkillType
  rank: SkillRank
}

export interface Experience {
  org: string
  role: string
  kind: ExperienceKind
  start_date: string // JSON has no date type, so dates arrive as "2024-08-01"
  end_date: string | null // null = present
  bullets: string[]
}

/** Body sent by the contact form (POST /api/messages). */
export interface MessageIn {
  name: string
  email: string
  body: string
  website: string // honeypot: always empty for real visitors
}
