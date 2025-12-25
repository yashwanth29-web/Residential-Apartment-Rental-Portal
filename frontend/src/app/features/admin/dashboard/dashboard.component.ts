import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminService, OccupancyReport, BookingReport } from '../services/admin.service';
import { LoadingSpinnerComponent } from '../../../shared/components';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, LoadingSpinnerComponent],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  private adminService = inject(AdminService);

  occupancyReport = signal<OccupancyReport[]>([]);
  bookingReport = signal<BookingReport | null>(null);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Computed totals
  totalFlats = signal(0);
  totalOccupied = signal(0);
  totalVacant = signal(0);
  overallOccupancy = signal(0);

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.isLoading.set(true);
    this.error.set(null);

    // Load occupancy report
    this.adminService.getOccupancyReport().subscribe({
      next: (report) => {
        this.occupancyReport.set(report);
        this.calculateTotals(report);
      },
      error: (err) => {
        this.error.set('Failed to load occupancy data');
        this.isLoading.set(false);
      }
    });

    // Load booking report
    this.adminService.getBookingReport('month').subscribe({
      next: (report) => {
        this.bookingReport.set(report);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load booking data');
        this.isLoading.set(false);
      }
    });
  }

  private calculateTotals(report: OccupancyReport[]): void {
    const totals = report.reduce(
      (acc, tower) => ({
        total: acc.total + tower.total_flats,
        occupied: acc.occupied + tower.occupied_flats,
        vacant: acc.vacant + tower.vacant_flats
      }),
      { total: 0, occupied: 0, vacant: 0 }
    );

    this.totalFlats.set(totals.total);
    this.totalOccupied.set(totals.occupied);
    this.totalVacant.set(totals.vacant);
    this.overallOccupancy.set(
      totals.total > 0 ? Math.round((totals.occupied / totals.total) * 100) : 0
    );
  }

  getOccupancyColor(percentage: number): string {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  }

  getOccupancyBgColor(percentage: number): string {
    if (percentage >= 80) return 'bg-green-100';
    if (percentage >= 50) return 'bg-yellow-100';
    return 'bg-red-100';
  }
}
