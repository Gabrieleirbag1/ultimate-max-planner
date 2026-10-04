import { Component, inject, output } from '@angular/core';
import { SavedSearch } from '../../models/models';
import { HistoryService } from '../../services/history.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.html',
  styleUrl: './history.css',
})
export class History {
  history = inject(HistoryService);
  pick = output<SavedSearch>();

  label(e: SavedSearch): string {
    const via = e.hubs.length ? ` · via ${e.hubs.join(', ')}` : '';
    return `${e.origins.join(', ')} → ${e.destinations.join(', ')}${via}${e.overnight ? ' · 🌙' : ''}`;
  }
}
