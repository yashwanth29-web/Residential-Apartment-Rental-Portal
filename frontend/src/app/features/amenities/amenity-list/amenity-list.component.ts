import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AmenityService } from '../services/amenity.service';
import { Amenity, AmenityType } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components';

@Component({
  selector: 'app-amenity-list',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  templateUrl: './amenity-list.component.html'
})
export class AmenityListComponent implements OnInit {
  private amenityService = inject(AmenityService);

  amenities = signal<Amenity[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);
  selectedType = signal<AmenityType | 'all'>('all');

  filteredAmenities = computed(() => {
    const type = this.selectedType();
    const all = this.amenities();
    if (type === 'all') return all;
    return all.filter(a => a.type === type);
  });

  amenityTypes: { value: AmenityType | 'all'; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'gym', label: 'Gym' },
    { value: 'pool', label: 'Pool' },
    { value: 'parking', label: 'Parking' },
    { value: 'common', label: 'Common Areas' }
  ];

  ngOnInit(): void {
    this.loadAmenities();
  }

  loadAmenities(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.amenityService.getAmenities().subscribe({
      next: (amenities) => {
        this.amenities.set(amenities);
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load amenities. Please try again.');
        this.isLoading.set(false);
      }
    });
  }

  filterByType(type: AmenityType | 'all'): void {
    this.selectedType.set(type);
  }

  getTypeIcon(type: AmenityType): string {
    const icons: Record<AmenityType, string> = {
      gym: 'M4 6h16M4 10h16M4 14h16M4 18h16',
      pool: 'M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5',
      parking: 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2',
      common: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    };
    return icons[type] || icons.common;
  }

  getTypeColor(type: AmenityType): string {
    const colors: Record<AmenityType, string> = {
      gym: 'bg-red-100 text-red-800',
      pool: 'bg-blue-100 text-blue-800',
      parking: 'bg-gray-100 text-gray-800',
      common: 'bg-green-100 text-green-800'
    };
    return colors[type] || colors.common;
  }
}
