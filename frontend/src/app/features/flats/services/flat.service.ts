import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Flat, FlatFilter, Tower } from '../../../core/models';

@Injectable({
  providedIn: 'root'
})
export class FlatService {
  private readonly apiUrl = `${environment.apiUrl}`;
  private http = inject(HttpClient);

  getFlats(filter?: FlatFilter): Observable<Flat[]> {
    let params = new HttpParams();
    
    if (filter) {
      if (filter.tower_id) {
        params = params.set('tower_id', filter.tower_id.toString());
      }
      if (filter.bedrooms) {
        params = params.set('bedrooms', filter.bedrooms.toString());
      }
      if (filter.min_rent) {
        params = params.set('min_rent', filter.min_rent.toString());
      }
      if (filter.max_rent) {
        params = params.set('max_rent', filter.max_rent.toString());
      }
    }

    return this.http.get<Flat[]>(`${this.apiUrl}/flats`, { params });
  }

  getFlatById(id: number): Observable<Flat> {
    return this.http.get<Flat>(`${this.apiUrl}/flats/${id}`);
  }

  getTowers(): Observable<Tower[]> {
    return this.http.get<Tower[]>(`${this.apiUrl}/towers`);
  }

  getTowerById(id: number): Observable<Tower> {
    return this.http.get<Tower>(`${this.apiUrl}/towers/${id}`);
  }
}
