import { Component, inject, signal } from '@angular/core';
import { CalendarView } from './components/calendar/calendar';
import { DayDetails } from './components/day-details/day-details';
import { SearchPanel } from './components/search-panel/search-panel';
import { SearchStateService } from './services/search-state.service';

@Component({
  selector: 'app-root',
  imports: [SearchPanel, CalendarView, DayDetails],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  state = inject(SearchStateService);
  /** Phone only: which pane is visible (all three are shown side by side on large screens). */
  tab = signal<'search' | 'calendar' | 'details'>('search');

  onDay(date: string) {
    this.state.selectDay(date);
    this.tab.set('details');
  }
}
