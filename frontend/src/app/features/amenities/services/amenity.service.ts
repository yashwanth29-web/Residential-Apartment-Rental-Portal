import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from '../../../core/services/config.service';
import { Amenity } from '../../../core/models';

@Injectable({
  providedIn: 'root'
})
export class AmenityService {
  private configService = inject(ConfigService);
  private http = inject(HttpClient);

  private get apiUrl(): string {
    return `${this.configService.apiUrl}/amenities`;
  }

  getAmenities(): Observable<Amenity[]> {
    return this.http.get<Amenity[]>(this.apiUrl);
  }

  getAmenityById(id: number): Observable<Amenity> {
    return this.http.get<Amenity>(`${this.apiUrl}/${id}`);
  }
}
