import { Component, OnInit, WritableSignal, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AsyncPipe } from '@angular/common';
import { Subject, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';
import { History } from '../history/history';
import { SavedSearch } from '../../models/models';
import { ApiService } from '../../services/api.service';
import { HistoryService } from '../../services/history.service';
import { SearchStateService } from '../../services/search-state.service';

const iso = (d: Date) => d.toISOString().slice(0, 10);

@Component({
  selector: 'app-search-panel',
  imports: [FormsModule, AsyncPipe, History],
  templateUrl: './search-panel.html',
  styleUrl: './search-panel.css',
})
export class SearchPanel implements OnInit {
  private api = inject(ApiService);
  state = inject(SearchStateService);
  private history = inject(HistoryService);

  origins = signal<string[]>(['Strasbourg', 'Mulhouse', 'Colmar']);
  hubs = signal<string[]>([]);
  suggestions = signal<string[]>([]);
  originInput = '';
  hubInput = '';
  destinations = signal<string[]>(['Bordeaux']);
  destInput = '';
  dateFrom = iso(new Date());
  dateTo = iso(new Date(Date.now() + 30 * 864e5));
  overnight = false;
  maxLegs = 3;

  readonly defaultHubs = ['Paris', 'Massy TGV', 'Marne-la-Vallée Chessy', 'Aéroport CDG 2'];
  private typing$ = new Subject<string>();

  ngOnInit() {
    this.typing$
      .pipe(debounceTime(250), distinctUntilChanged(), switchMap((q) => this.api.stations(q)))
      .subscribe((s) => this.suggestions.set(s));
  }

  suggest(q: string) {
    this.typing$.next(q);
  }

  add(list: WritableSignal<string[]>, value: string) {
    const v = value.trim();
    if (v && !list().some((x) => x.toLowerCase() === v.toLowerCase())) list.update((l) => [...l, v]);
  }

  addOrigin() {
    this.add(this.origins, this.originInput);
    this.originInput = '';
  }

  addDestination() {
    this.add(this.destinations, this.destInput);
    this.destInput = '';
  }

  addHub() {
    this.add(this.hubs, this.hubInput);
    this.hubInput = '';
  }

  remove(list: WritableSignal<string[]>, value: string) {
    list.update((l) => l.filter((x) => x !== value));
  }

  /** Swap outward and return journeys: origins become destinations and vice versa. */
  swap() {
    const origins = this.origins();
    this.origins.set(this.destinations());
    this.destinations.set(origins);
  }

  /** Restore a remembered search and run it again from today over the same span. */
  apply(s: SavedSearch) {
    this.origins.set([...s.origins]);
    this.destinations.set([...s.destinations]);
    this.hubs.set([...s.hubs]);
    this.overnight = s.overnight;
    this.maxLegs = s.max_legs;
    this.dateFrom = iso(new Date());
    this.dateTo = iso(new Date(Date.now() + (s.span_days - 1) * 864e5));
    this.submit();
  }

  submit() {
    const query = {
      origins: this.origins(),
      destinations: this.destinations(),
      date_from: this.dateFrom,
      date_to: this.dateTo,
      hubs: this.hubs(),
      overnight: this.overnight,
      max_legs: this.maxLegs,
    };
    this.history.record(query);
    this.state.search(query);
  }
}
