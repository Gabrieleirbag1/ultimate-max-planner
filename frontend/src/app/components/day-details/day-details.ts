import { Component, inject } from '@angular/core';
import { AsyncPipe, DatePipe } from '@angular/common';
import { SearchStateService } from '../../services/search-state.service';

@Component({
  selector: 'app-day-details',
  imports: [AsyncPipe, DatePipe],
  templateUrl: './day-details.html',
  styleUrl: './day-details.css',
})
export class DayDetails {
  state = inject(SearchStateService);

  entries(itineraries: Record<string, unknown[]>) {
    return Object.keys(itineraries);
  }

  minutes(m: number) {
    return `${Math.floor(m / 60)}h${String(m % 60).padStart(2, '0')}`;
  }
}
