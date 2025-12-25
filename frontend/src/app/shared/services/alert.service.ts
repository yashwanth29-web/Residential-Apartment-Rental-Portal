import { Injectable, signal } from '@angular/core';

export interface Alert {
  id: number;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private alertsSignal = signal<Alert[]>([]);
  private nextId = 0;

  readonly alerts = this.alertsSignal.asReadonly();

  success(message: string, duration = 5000): void {
    this.addAlert('success', message, duration);
  }

  error(message: string, duration = 5000): void {
    this.addAlert('error', message, duration);
  }

  warning(message: string, duration = 5000): void {
    this.addAlert('warning', message, duration);
  }

  info(message: string, duration = 5000): void {
    this.addAlert('info', message, duration);
  }

  private addAlert(type: Alert['type'], message: string, duration: number): void {
    const id = this.nextId++;
    const alert: Alert = { id, type, message };
    
    this.alertsSignal.update(alerts => [...alerts, alert]);

    if (duration > 0) {
      setTimeout(() => this.removeAlert(id), duration);
    }
  }

  removeAlert(id: number): void {
    this.alertsSignal.update(alerts => alerts.filter(a => a.id !== id));
  }
}
