import { Component, inject } from '@angular/core';
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
}
