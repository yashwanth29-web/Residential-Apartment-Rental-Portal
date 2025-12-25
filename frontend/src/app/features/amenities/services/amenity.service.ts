import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Amenity } from '../../../core/models';

@Injectable({
  providedIn: 'root'
})
export class AmenityService {
  private readonly apiUrl = `${environment.apiUrl}/amenities`;
  private http = inject(HttpClient);

  getAmenities(): Observable<Amenity[]> {
    return this.http.get<Amenity[]>(this.apiUrl);
  }

  getAmenityById(id: number): Observable<Amenity> {
    return this.http.get<Amenity>(`${this.apiUrl}/${id}`);
  }
}
