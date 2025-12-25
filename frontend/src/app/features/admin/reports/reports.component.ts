import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, OccupancyReport, BookingReport, PaymentReport } from '../services/admin.service';
import { LoadingSpinnerComponent } from '../../../shared/components';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './reports.component.html'
})
export class ReportsComponent implements OnInit {
  private adminService = inject(AdminService);

  // Data
  occupancyReport = signal<OccupancyReport[]>([]);
  bookingReport = signal<BookingReport | null>(null);
  paymentReport = signal<PaymentReport | null>(null);

  // Loading states
  isLoadingOccupancy = signal(true);
  isLoadingBookings = signal(true);
  isLoadingPayments = signal(true);

  // Booking report period
  bookingPeriod: 'week' | 'month' | 'year' = 'month';

  // Computed totals for occupancy
  totalFlats = signal(0);
  totalOccupied = signal(0);
  overallOccupancy = signal(0);

  ngOnInit(): void {
    this.loadAllReports();
  }

  loadAllReports(): void {
    this.loadOccupancyReport();
    this.loadBookingReport();
    this.loadPaymentReport();
  }

  loadOccupancyReport(): void {
    this.isLoadingOccupancy.set(true);

    this.adminService.getOccupancyReport().subscribe({
      next: (report) => {
        this.occupancyReport.set(report);
        this.calculateOccupancyTotals(report);
        this.isLoadingOccupancy.set(false);
      },
      error: () => {
        this.isLoadingOccupancy.set(false);
      }
    });
  }

  loadBookingReport(): void {
    this.isLoadingBookings.set(true);

    this.adminService.getBookingReport(this.bookingPeriod).subscribe({
      next: (report) => {
        this.bookingReport.set(report);
        this.isLoadingBookings.set(false);
      },
      error: () => {
        this.isLoadingBookings.set(false);
      }
    });
  }

  loadPaymentReport(): void {
    this.isLoadingPayments.set(true);

    this.adminService.getPaymentReport().subscribe({
      next: (report) => {
        this.paymentReport.set(report);
        this.isLoadingPayments.set(false);
      },
      error: () => {
        this.isLoadingPayments.set(false);
      }
    });
  }

  onPeriodChange(): void {
    this.loadBookingReport();
  }

  private calculateOccupancyTotals(report: OccupancyReport[]): void {
    const totals = report.reduce(
      (acc, tower) => ({
        total: acc.total + tower.total_flats,
        occupied: acc.occupied + tower.occupied_flats
      }),
      { total: 0, occupied: 0 }
    );

    this.totalFlats.set(totals.total);
    this.totalOccupied.set(totals.occupied);
    this.overallOccupancy.set(
      totals.total > 0 ? Math.round((totals.occupied / totals.total) * 100) : 0
    );
  }

  getOccupancyBarWidth(percentage: number): string {
    return `${percentage}%`;
  }

  getOccupancyBarColor(percentage: number): string {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  }

  getCollectionRateColor(rate: number): string {
    if (rate >= 95) return 'text-green-600';
    if (rate >= 85) return 'text-yellow-600';
    return 'text-red-600';
  }
}
