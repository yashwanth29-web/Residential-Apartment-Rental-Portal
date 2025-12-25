import { Component, inject } from '@angular/core';
import { AlertService, Alert } from '../../services/alert.service';

@Component({
  selector: 'app-alert',
  standalone: true,
  templateUrl: './alert.component.html'
})
export class AlertComponent {
  private alertService = inject(AlertService);
  
  alerts = this.alertService.alerts;

  getAlertClasses(type: Alert['type']): string {
    const baseClasses = 'p-4 rounded-md shadow-lg flex items-center justify-between';
    const typeClasses = {
      success: 'bg-green-100 text-green-800 border border-green-200',
      error: 'bg-red-100 text-red-800 border border-red-200',
      warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
      info: 'bg-blue-100 text-blue-800 border border-blue-200'
    };
    return `${baseClasses} ${typeClasses[type]}`;
  }

  getIconClasses(type: Alert['type']): string {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type];
  }

  dismiss(id: number): void {
    this.alertService.removeAlert(id);
  }
}
