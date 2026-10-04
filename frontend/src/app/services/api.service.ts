import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../environments/environment';
import { DayResponse, SearchQuery, SearchResult } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/api`;

  stations(q: string): Observable<string[]> {
    return this.http
      .get<{ stations: string[] }>(`${this.base}/stations`, { params: { q } })
      .pipe(map((r) => r.stations));
  }

  search(query: SearchQuery): Observable<SearchResult> {
    return this.http.post<SearchResult>(`${this.base}/search`, query);
  }

  day(query: SearchQuery, date: string): Observable<DayResponse> {
    const params = new HttpParams()
      .set('origins', query.origins.join(','))
      .set('destinations', query.destinations.join(','))
      .set('date', date)
      .set('hubs', query.hubs.join(','))
      .set('overnight', query.overnight)
      .set('max_legs', query.max_legs);
    return this.http.get<DayResponse>(`${this.base}/day`, { params });
  }
}
