import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, EMPTY, catchError, finalize, tap } from 'rxjs';
import { DayResponse, SearchQuery, SearchResult, routesOf } from '../models/models';
import { ApiService } from './api.service';

export const PALETTE = ['#2563eb', '#e11d48', '#16a34a', '#f59e0b', '#7c3aed', '#0891b2', '#db2777', '#65a30d'];

@Injectable({ providedIn: 'root' })
export class SearchStateService {
  private api = inject(ApiService);

  readonly query$ = new BehaviorSubject<SearchQuery | null>(null);
  readonly result$ = new BehaviorSubject<SearchResult | null>(null);
  readonly selectedDate$ = new BehaviorSubject<string | null>(null);
  readonly details$ = new BehaviorSubject<DayResponse | null>(null);
  readonly loading$ = new BehaviorSubject(false);
  readonly error$ = new BehaviorSubject<string | null>(null);

  /** One color per route ("Origin → Destination"), stable for a given search. */
  colorOf(route: string): string {
    const routes = this.query$.value ? routesOf(this.query$.value) : [];
    return PALETTE[Math.max(0, routes.indexOf(route)) % PALETTE.length];
  }

  search(query: SearchQuery): void {
    this.query$.next(query);
    this.selectedDate$.next(null);
    this.details$.next(null);
    this.error$.next(null);
    this.loading$.next(true);
    this.api
      .search(query)
      .pipe(
        tap((r) => this.result$.next(r)),
        catchError((e) => this.fail(e)),
        finalize(() => this.loading$.next(false)),
      )
      .subscribe();
  }

  retry(): void {
    const q = this.query$.value;
    if (q) this.search(q);
  }

  selectDay(date: string): void {
    const query = this.query$.value;
    if (!query) return;
    this.selectedDate$.next(date);
    this.details$.next(null);
    this.api
      .day(query, date)
      .pipe(
        tap((d) => this.details$.next(d)),
        catchError((e) => this.fail(e)),
      )
      .subscribe();
  }

  private fail(e: HttpErrorResponse) {
    this.error$.next(e.error?.error ?? 'Erreur réseau : le backend est-il démarré ?');
    this.result$.next(null);
    return EMPTY;
  }
}
