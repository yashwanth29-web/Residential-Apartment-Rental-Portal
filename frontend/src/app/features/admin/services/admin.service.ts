import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from '../../../core/services/config.service';
import { Tower, Flat, Amenity } from '../../../core/models';

// Admin-specific interfaces
export interface OccupancyReport {
  tower_id: number;
  tower_name: string;
  total_flats: number;
  occupied_flats: number;
  vacant_flats: number;
  occupancy_percentage: number;
}

export interface BookingReport {
  period: string;
  start_date: string;
  end_date: string;
  total: {
    pending: number;
    approved: number;
    declined: number;
    total: number;
  };
  period_counts: {
    pending: number;
    approved: number;
    declined: number;
    total: number;
  };
}

export interface PaymentReport {
  active_leases_count: number;
  total_expected_monthly: number;
  monthly_breakdown: {
    month: string;
    expected: number;
    received: number;
    collection_rate: number;
  }[];
  note: string;
}

export interface AdminBooking {
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
  user?: {
    id: number;
    name: string;
    email: string;
    phone: string;
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

export interface Tenant {
  id: number;
  email: string;
  name: string;
  phone: string;
  role: string;
  created_at: string;
  active_leases: {
    id: number;
    start_date: string;
    end_date: string | null;
    monthly_rent: number;
    status: string;
    flat: {
      id: number;
      tower_name: string;
      unit_number: string;
    };
  }[];
}

export interface TenantDetails {
  user: {
    id: number;
    email: string;
    name: string;
    phone: string;
    role: string;
    created_at: string;
  };
  leases: {
    id: number;
    start_date: string;
    end_date: string | null;
    monthly_rent: number;
    status: string;
    flat: {
      id: number;
      tower_name: string;
      unit_number: string;
      floor: number;
      bedrooms: number;
      rent: number;
    };
  }[];
  payment_history: {
    month: string;
    amount: number;
    status: string;
  }[];
}

export interface CreateTowerRequest {
  name: string;
  address?: string;
  total_floors: number;
  flats_per_floor?: number;
  amenity_ids?: number[];
}

export interface CreateFlatRequest {
  tower_id: number;
  unit_number: string;
  floor: number;
  bedrooms: number;
  bathrooms: number;
  rent: number;
  area_sqft?: number;
  is_available?: boolean;
}

export interface CreateAmenityRequest {
  name: string;
  type: 'gym' | 'pool' | 'parking' | 'common';
  description?: string;
  hours?: string;
  fee?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private configService = inject(ConfigService);
  private http = inject(HttpClient);

  private get apiUrl(): string {
    return `${this.configService.apiUrl}/admin`;
  }

  // Tower Management
  getTowers(): Observable<Tower[]> {
    return this.http.get<Tower[]>(`${this.apiUrl}/towers`);
  }

  getTower(id: number): Observable<Tower> {
    return this.http.get<Tower>(`${this.apiUrl}/towers/${id}`);
  }

  createTower(data: CreateTowerRequest): Observable<Tower> {
    return this.http.post<Tower>(`${this.apiUrl}/towers`, data);
  }

  updateTower(id: number, data: Partial<CreateTowerRequest>): Observable<Tower> {
    return this.http.put<Tower>(`${this.apiUrl}/towers/${id}`, data);
  }

  deleteTower(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/towers/${id}`);
  }

  // Flat Management
  getFlats(): Observable<Flat[]> {
    return this.http.get<Flat[]>(`${this.apiUrl}/flats`);
  }

  getFlat(id: number): Observable<Flat> {
    return this.http.get<Flat>(`${this.apiUrl}/flats/${id}`);
  }

  createFlat(data: CreateFlatRequest): Observable<Flat> {
    return this.http.post<Flat>(`${this.apiUrl}/flats`, data);
  }

  updateFlat(id: number, data: Partial<CreateFlatRequest>): Observable<Flat> {
    return this.http.put<Flat>(`${this.apiUrl}/flats/${id}`, data);
  }

  deleteFlat(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/flats/${id}`);
  }

  // Amenity Management
  getAmenities(): Observable<Amenity[]> {
    return this.http.get<Amenity[]>(`${this.apiUrl}/amenities`);
  }

  getAmenity(id: number): Observable<Amenity> {
    return this.http.get<Amenity>(`${this.apiUrl}/amenities/${id}`);
  }

  createAmenity(data: CreateAmenityRequest): Observable<Amenity> {
    return this.http.post<Amenity>(`${this.apiUrl}/amenities`, data);
  }

  updateAmenity(id: number, data: Partial<CreateAmenityRequest>): Observable<Amenity> {
    return this.http.put<Amenity>(`${this.apiUrl}/amenities/${id}`, data);
  }

  deleteAmenity(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/amenities/${id}`);
  }

  // Booking Management
  getBookings(): Observable<AdminBooking[]> {
    return this.http.get<AdminBooking[]>(`${this.apiUrl}/bookings`);
  }

  getBooking(id: number): Observable<AdminBooking> {
    return this.http.get<AdminBooking>(`${this.apiUrl}/bookings/${id}`);
  }

  approveBooking(id: number): Observable<AdminBooking> {
    return this.http.put<AdminBooking>(`${this.apiUrl}/bookings/${id}/approve`, {});
  }

  declineBooking(id: number): Observable<AdminBooking> {
    return this.http.put<AdminBooking>(`${this.apiUrl}/bookings/${id}/decline`, {});
  }

  // Tenant Management
  getTenants(): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(`${this.apiUrl}/tenants`);
  }

  getTenant(id: number): Observable<TenantDetails> {
    return this.http.get<TenantDetails>(`${this.apiUrl}/tenants/${id}`);
  }

  terminateLease(leaseId: number): Observable<{ message: string; lease: any }> {
    return this.http.delete<{ message: string; lease: any }>(`${this.apiUrl}/leases/${leaseId}`);
  }

  // Reports
  getOccupancyReport(): Observable<OccupancyReport[]> {
    return this.http.get<OccupancyReport[]>(`${this.apiUrl}/reports/occupancy`);
  }

  getBookingReport(period: 'week' | 'month' | 'year' = 'month'): Observable<BookingReport> {
    return this.http.get<BookingReport>(`${this.apiUrl}/reports/bookings`, {
      params: { period }
    });
  }

  getPaymentReport(): Observable<PaymentReport> {
    return this.http.get<PaymentReport>(`${this.apiUrl}/reports/payments`);
  }
}
