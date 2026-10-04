import { Component, computed, inject, output } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarOptions, EventClickArg } from '@fullcalendar/core';
import frLocale from '@fullcalendar/core/locales/fr';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin, { DateClickArg } from '@fullcalendar/interaction';
import { routesOf } from '../../models/models';
import { SearchStateService } from '../../services/search-state.service';

// Crescent moon icon: marks routes whose day includes a stay-overnight connection.
const MOON =
  '<svg class="moon" viewBox="0 0 24 24" width="13" height="13" aria-label="Nuit sur place"><path fill="currentColor" d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

@Component({
  selector: 'app-calendar',
  imports: [FullCalendarModule],
  templateUrl: './calendar.html',
  styleUrl: './calendar.css',
})
export class CalendarView {
  private state = inject(SearchStateService);
  daySelected = output<string>();

  private result = toSignal(this.state.result$, { initialValue: null });
  private query = toSignal(this.state.query$, { initialValue: null });
  private selected = toSignal(this.state.selectedDate$, { initialValue: null });

  routes = computed(() => {
    const q = this.query();
    return (q ? routesOf(q) : []).map((r) => ({ name: r, color: this.state.colorOf(r) }));
  });

  options = computed<CalendarOptions>(() => {
    const result = this.result();
    const events = Object.entries(result?.days ?? {}).flatMap(([origin, days]) =>
      Object.entries(days).map(([date, s]) => ({
        start: date,
        allDay: true,
        title: `${origin} · ${s.count}`,
        color: this.state.colorOf(origin),
        extendedProps: { date, overnight: s.has_overnight },
      })),
    );
    return {
      plugins: [dayGridPlugin, interactionPlugin],
      locale: frLocale,
      initialView: 'dayGridMonth',
      initialDate: this.query()?.date_from,
      firstDay: 1,
      height: 'auto',
      dayMaxEvents: window.innerWidth < 900 ? 2 : 4,
      events,
      dayCellClassNames: (arg) =>
        arg.date.toISOString().slice(0, 10) === this.selected() ? ['selected-day'] : [],
      eventContent: (arg) => {
        const night = arg.event.extendedProps['overnight'];
        const title = arg.event.title.replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);
        return { html: `<span class="ev-line" ${night ? 'title="Inclut une correspondance avec nuit sur place"' : ''}>${night ? MOON : ''}<span class="ev-text">${title}</span></span>` };
      },
      dateClick: (a: DateClickArg) => this.daySelected.emit(a.dateStr),
      eventClick: (a: EventClickArg) => this.daySelected.emit(a.event.extendedProps['date']),
    };
  });
}
