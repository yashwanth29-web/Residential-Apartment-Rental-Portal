import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from '../../../core/services/config.service';

export interface Booking {
  id: number;
  user_id: number;
  flat_id: number;
  flat: {
    id: number;
    tower_name: string;
    unit_number: string;
    floor: number;
    bedrooms: number;
    bathrooms: number;
    rent: number;
  };
  status: 'pending' | 'approved' | 'declined';
  requested_date: string;
  created_at: string;
  lease?: {
    id: number;
    start_date: string;
    end_date: string | null;
    monthly_rent: number;
    status: 'active' | 'terminated';
  };
}

export interface CreateBookingRequest {
  flat_id: number;
  requested_date: string;
}

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private configService = inject(ConfigService);
  private http = inject(HttpClient);

  private get apiUrl(): string {
    return `${this.configService.apiUrl}/bookings`;
  }

  getBookings(): Observable<Booking[]> {
    return this.http.get<Booking[]>(this.apiUrl);
  }

  getBookingById(id: number): Observable<Booking> {
    return this.http.get<Booking>(`${this.apiUrl}/${id}`);
  }

  createBooking(flatId: number, requestedDate: string): Observable<Booking> {
    const request: CreateBookingRequest = {
      flat_id: flatId,
      requested_date: requestedDate
    };
    return this.http.post<Booking>(this.apiUrl, request);
  }
}
