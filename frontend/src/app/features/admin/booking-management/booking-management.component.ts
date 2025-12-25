import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, AdminBooking } from '../services/admin.service';
import { LoadingSpinnerComponent } from '../../../shared/components';
import { AlertService } from '../../../shared/services';

@Component({
  selector: 'app-booking-management',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './booking-management.component.html'
})
export class BookingManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  private alertService = inject(AlertService);

  bookings = signal<AdminBooking[]>([]);
  filteredBookings = signal<AdminBooking[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Filter
  statusFilter = 'all';

  // Action state
  processingBookingId = signal<number | null>(null);

  // Confirmation modal
  showConfirmModal = signal(false);
  confirmAction = signal<'approve' | 'decline' | null>(null);
  selectedBooking = signal<AdminBooking | null>(null);

  ngOnInit(): void {
    this.loadBookings();
  }

  loadBookings(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.adminService.getBookings().subscribe({
      next: (bookings) => {
        this.bookings.set(bookings);
        this.applyFilter();
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load bookings');
        this.isLoading.set(false);
      }
    });
  }

  applyFilter(): void {
    const all = this.bookings();
    if (this.statusFilter === 'all') {
      this.filteredBookings.set(all);
    } else {
      this.filteredBookings.set(all.filter(b => b.status === this.statusFilter));
    }
  }

  openConfirmModal(booking: AdminBooking, action: 'approve' | 'decline'): void {
    this.selectedBooking.set(booking);
    this.confirmAction.set(action);
    this.showConfirmModal.set(true);
  }

  closeConfirmModal(): void {
    this.showConfirmModal.set(false);
    this.selectedBooking.set(null);
    this.confirmAction.set(null);
  }

  confirmBookingAction(): void {
    const booking = this.selectedBooking();
    const action = this.confirmAction();
    
    if (!booking || !action) return;

    this.processingBookingId.set(booking.id);
    this.closeConfirmModal();

    if (action === 'approve') {
      this.adminService.approveBooking(booking.id).subscribe({
        next: () => {
          this.alertService.success('Booking approved successfully');
          this.loadBookings();
          this.processingBookingId.set(null);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to approve booking');
          this.processingBookingId.set(null);
        }
      });
    } else {
      this.adminService.declineBooking(booking.id).subscribe({
        next: () => {
          this.alertService.success('Booking declined');
          this.loadBookings();
          this.processingBookingId.set(null);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to decline booking');
          this.processingBookingId.set(null);
        }
      });
    }
  }

  getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      declined: 'bg-red-100 text-red-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }
}
