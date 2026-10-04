import { Injectable, signal } from '@angular/core';
import { SavedSearch, SearchQuery } from '../models/models';

const RECENT_KEY = 'tgvmax.recent';
const FAVORITES_KEY = 'tgvmax.favorites';
const MAX_RECENT = 10;

const norm = (s: string) => s.trim().toLowerCase();

/** Same journey (origins in any order, same hubs/options) => same id. */
export function searchId(q: Pick<SearchQuery, 'origins' | 'destinations' | 'hubs' | 'overnight' | 'max_legs'>): string {
  return JSON.stringify([
    q.origins.map(norm).sort(),
    q.destinations.map(norm).sort(),
    q.hubs.map(norm).sort(),
    q.overnight,
    q.max_legs,
  ]);
}

@Injectable({ providedIn: 'root' })
export class HistoryService {
  readonly recent = signal<SavedSearch[]>(this.load(RECENT_KEY));
  readonly favorites = signal<SavedSearch[]>(this.load(FAVORITES_KEY));

  record(q: SearchQuery): void {
    const entry: SavedSearch = {
      id: searchId(q),
      origins: q.origins,
      destinations: q.destinations,
      hubs: q.hubs,
      overnight: q.overnight,
      max_legs: q.max_legs,
      span_days: Math.max(1, Math.round((Date.parse(q.date_to) - Date.parse(q.date_from)) / 864e5) + 1),
      savedAt: Date.now(),
    };
    this.recent.set([entry, ...this.recent().filter((e) => e.id !== entry.id)].slice(0, MAX_RECENT));
    // keep an existing favorite up to date with the latest options
    if (this.isFavorite(entry.id)) {
      this.favorites.update((l) => l.map((f) => (f.id === entry.id ? entry : f)));
      this.save(FAVORITES_KEY, this.favorites());
    }
    this.save(RECENT_KEY, this.recent());
  }

  isFavorite(id: string): boolean {
    return this.favorites().some((f) => f.id === id);
  }

  toggleFavorite(entry: SavedSearch): void {
    this.favorites.update((l) => (this.isFavorite(entry.id) ? l.filter((f) => f.id !== entry.id) : [entry, ...l]));
    this.save(FAVORITES_KEY, this.favorites());
  }

  removeRecent(id: string): void {
    this.recent.update((l) => l.filter((e) => e.id !== id));
    this.save(RECENT_KEY, this.recent());
  }

  removeFavorite(id: string): void {
    this.favorites.update((l) => l.filter((e) => e.id !== id));
    this.save(FAVORITES_KEY, this.favorites());
  }

  clearRecent(): void {
    this.recent.set([]);
    this.save(RECENT_KEY, []);
  }

  private load(key: string): SavedSearch[] {
    try {
      const data = JSON.parse(localStorage.getItem(key) ?? '[]');
      if (!Array.isArray(data)) return [];
      return data
        .map((e) => (e && !e.destinations && e.destination ? { ...e, destinations: [e.destination] } : e)) // old format
        .filter((e) => e && Array.isArray(e.origins) && Array.isArray(e.destinations) && e.destinations.length);
    } catch {
      return [];
    }
  }

  private save(key: string, value: SavedSearch[]): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* storage unavailable: the lists still work for this session */
    }
  }
}
