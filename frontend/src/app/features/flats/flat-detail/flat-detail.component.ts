import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FlatService } from '../services/flat.service';
import { BookingService, Booking } from '../../bookings/services/booking.service';
import { Flat, Amenity } from '../../../core/models';
import { AuthService } from '../../../core/services';
import { AlertService } from '../../../shared/services';
import { LoadingSpinnerComponent } from '../../../shared/components';

@Component({
  selector: 'app-flat-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, LoadingSpinnerComponent],
  templateUrl: './flat-detail.component.html'
})
export class FlatDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private flatService = inject(FlatService);
  private bookingService = inject(BookingService);
  private authService = inject(AuthService);
  private alertService = inject(AlertService);

  flat = signal<Flat | null>(null);
  amenities = signal<Amenity[]>([]);
  isLoading = signal(true);
  isBooking = signal(false);
  error = signal<string | null>(null);
  userBooking = signal<Booking | null>(null);

  isAuthenticated = this.authService.isAuthenticated;

  ngOnInit(): void {
    const flatId = this.route.snapshot.paramMap.get('id');
    if (flatId) {
      this.loadFlat(parseInt(flatId, 10));
    } else {
      this.error.set('Invalid flat ID');
      this.isLoading.set(false);
    }
  }

  loadFlat(id: number): void {
    this.flatService.getFlatById(id).subscribe({
      next: (flat) => {
        this.flat.set(flat);
        this.isLoading.set(false);
        // Load tower amenities
        this.loadTowerAmenities(flat.tower_id);
        // Check if user has a booking for this flat
        if (this.isAuthenticated() && !flat.is_available) {
          this.checkUserBooking(id);
        }
      },
      error: () => {
        this.error.set('Flat not found or unavailable.');
        this.isLoading.set(false);
      }
    });
  }

  loadTowerAmenities(towerId: number): void {
    this.flatService.getTowerById(towerId).subscribe({
      next: (tower) => {
        this.amenities.set(tower.amenities || []);
      },
      error: () => {
        // Silently fail - amenities are optional
      }
    });
  }

  checkUserBooking(flatId: number): void {
    this.bookingService.getBookings().subscribe({
      next: (bookings) => {
        const booking = bookings.find(b => b.flat_id === flatId && b.status === 'approved');
        this.userBooking.set(booking || null);
      },
      error: () => {
        // Silently fail - just won't show personalized message
      }
    });
  }

  getAmenityIcon(type: string): string {
    switch (type) {
      case 'gym': return 'M4 6h16M4 10h16M4 14h16M4 18h16';
      case 'pool': return 'M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z';
      case 'parking': return 'M8 7h8m-8 4h8m-8 4h8M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z';
      default: return 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5';
    }
  }

  bookFlat(): void {
    if (!this.isAuthenticated()) {
      this.alertService.warning('Please login to book this flat.');
      this.router.navigate(['/login']);
      return;
    }

    const flat = this.flat();
    if (!flat) return;

    this.isBooking.set(true);
    
    // Use today's date as the requested move-in date
    const requestedDate = new Date().toISOString().split('T')[0];
    
    this.bookingService.createBooking(flat.id, requestedDate).subscribe({
      next: () => {
        this.alertService.success('Booking request submitted successfully!');
        this.router.navigate(['/bookings']);
      },
      error: (err) => {
        this.isBooking.set(false);
        const message = err.error?.error?.message || 'Failed to create booking. Please try again.';
        this.alertService.error(message);
      }
    });
  }
}
