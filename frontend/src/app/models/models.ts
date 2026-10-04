export interface SearchQuery {
  origins: string[];
  destinations: string[];
  date_from: string;
  date_to: string;
  hubs: string[];
  overnight: boolean;
  max_legs: number;
}

/** A remembered search; dates are relative (re-run from today over `span_days`). */
export interface SavedSearch {
  id: string;
  origins: string[];
  destinations: string[];
  hubs: string[];
  overnight: boolean;
  max_legs: number;
  span_days: number;
  savedAt: number;
}

export interface DaySummary {
  count: number;
  direct: boolean;
  has_overnight: boolean;
  best: { dep: string; arr: string };
}

/** route id ("Origin → Destination") -> ISO date -> summary */
export interface SearchResult {
  days: Record<string, Record<string, DaySummary>>;
}

export const routeId = (origin: string, destination: string) => `${origin} → ${destination}`;

/** Every origin × destination pair (same rule as the backend). */
export function routesOf(q: Pick<SearchQuery, 'origins' | 'destinations'>): string[] {
  return q.origins.flatMap((o) =>
    q.destinations.filter((d) => d.trim().toLowerCase() !== o.trim().toLowerCase()).map((d) => routeId(o, d)),
  );
}

export interface Leg {
  train_no: string;
  origin: string;
  destination: string;
  dep: string;
  arr: string;
}

export interface Itinerary {
  date: string;
  origin_date: string;
  dep: string;
  arr: string;
  duration_min: number;
  transfers: number;
  overnight: boolean;
  stay_city: string | null;
  legs: Leg[];
}

export interface DayResponse {
  date: string;
  itineraries: Record<string, Itinerary[]>;
}
