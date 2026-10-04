import { Component, computed, inject, output } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarOptions, EventClickArg } from '@fullcalendar/core';
import frLocale from '@fullcalendar/core/locales/fr';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin, { DateClickArg } from '@fullcalendar/interaction';
import { routesOf } from '../../models/models';
import { SearchStateService } from '../../services/search-state.service';

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
        title: `${origin} · ${s.count}${s.has_overnight ? ' 🌙' : ''}`,
        color: this.state.colorOf(origin),
        extendedProps: { date },
      })),
    );
    return {
      plugins: [dayGridPlugin, interactionPlugin],
      locale: frLocale,
      initialView: 'dayGridMonth',
      initialDate: this.query()?.date_from,
      firstDay: 1,
      height: 'auto',
      dayMaxEvents: 4,
      events,
      dayCellClassNames: (arg) =>
        arg.date.toISOString().slice(0, 10) === this.selected() ? ['selected-day'] : [],
      dateClick: (a: DateClickArg) => this.daySelected.emit(a.dateStr),
      eventClick: (a: EventClickArg) => this.daySelected.emit(a.event.extendedProps['date']),
    };
  });
}
