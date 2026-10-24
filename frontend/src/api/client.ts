/*
  Everything that talks to the backend lives here, so components never call
  fetch() directly. If the API changes (a new header, a different base URL),
  only this file changes.
*/

import { useEffect, useState } from 'react'

/**
 * Error carrying the HTTP status code, so a screen can tell
 * "not found" (404) apart from "server broke" (500).
 */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

/**
 * GET a JSON endpoint, e.g. getJSON<Skill[]>('/api/skills').
 *
 * <T> is a generic: the caller says what type the response is, and
 * TypeScript checks every use of the result against that type.
 *
 * The URL is relative ("/api/..."), so it works both locally (via the Vite
 * proxy) and in production (via CloudFront) with no config.
 */
export async function getJSON<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(path, { signal })

  // fetch() only throws on network failure. A 404 or 500 still "succeeds",
  // so the status has to be checked by hand.
  if (!res.ok) {
    throw new ApiError(res.status, `GET ${path} failed with ${res.status}`)
  }
  return res.json() as Promise<T>
}

/** POST a JSON body. Used by the contact form. */
export async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    // Tells FastAPI the body is JSON so it parses and validates it.
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    throw new ApiError(res.status, `POST ${path} failed with ${res.status}`)
  }
  return res.json() as Promise<T>
}

/** What useApi returns: exactly one of these three states at a time. */
export type ApiState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError | Error }
  | { status: 'success'; data: T }

/**
 * React hook: load data from the API when a component appears.
 *
 *   const projects = useApi<ProjectSummary[]>('/api/projects')
 *   if (projects.status === 'success') projects.data.map(...)
 *
 * Why a "discriminated union" (status + data) instead of three separate
 * useState calls (data, loading, error)? Separate flags allow impossible
 * combinations, like loading=true AND error set at the same time. With one
 * `status` field, TypeScript only lets me read `data` after checking
 * status === 'success', so I can't forget to handle loading or errors.
 *
 * (This is the job TanStack Query would do; for a few endpoints, a 30-line
 * hook is enough and keeps the dependency list short.)
 */
export function useApi<T>(path: string): ApiState<T> {
  // Store each finished result together with the path it was for.
  // null = nothing has finished loading yet.
  const [result, setResult] = useState<{ path: string; state: ApiState<T> } | null>(null)

  // useEffect runs after the component renders, and again whenever `path`
  // changes (e.g. navigating from one fighter page to another).
  useEffect(() => {
    // AbortController cancels the request if the component goes away or the
    // path changes before the response arrives. Without it, a slow old
    // response could arrive late and overwrite the newer page's data.
    const controller = new AbortController()

    getJSON<T>(path, controller.signal)
      .then((data) => setResult({ path, state: { status: 'success', data } }))
      .catch((error: unknown) => {
        // Cancelling on purpose isn't a real error, so ignore it.
        if (controller.signal.aborted) return
        const err = error instanceof Error ? error : new Error(String(error))
        setResult({ path, state: { status: 'error', error: err } })
      })

    // The cleanup function: React runs it before the next effect and when
    // the component unmounts.
    return () => controller.abort()
  }, [path])

  // "Loading" is derived, not stored: if the stored result belongs to a
  // different path (or there isn't one yet), the current path is still loading.
  // This avoids calling setState({status: 'loading'}) inside the effect,
  // which would force an extra render every time the path changes.
  return result?.path === path ? result.state : { status: 'loading' }
}
