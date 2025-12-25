import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { FlatService } from '../services/flat.service';
import { Flat, FlatFilter, Tower } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components';

@Component({
  selector: 'app-flat-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, LoadingSpinnerComponent],
  templateUrl: './flat-list.component.html'
})
export class FlatListComponent implements OnInit {
  private flatService = inject(FlatService);

  flats = signal<Flat[]>([]);
  towers = signal<Tower[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Filter values
  selectedTowerId: number | null = null;
  selectedBedrooms: number | null = null;
  minRent: number | null = null;
  maxRent: number | null = null;

  bedroomOptions = [1, 2, 3, 4, 5];

  ngOnInit(): void {
    this.loadTowers();
    this.loadFlats();
  }

  loadTowers(): void {
    this.flatService.getTowers().subscribe({
      next: (towers) => this.towers.set(towers),
      error: () => {} // Silently fail for towers - they're optional for filtering
    });
  }

  loadFlats(): void {
    this.isLoading.set(true);
    this.error.set(null);

    const filter: FlatFilter = {};
    if (this.selectedTowerId) filter.tower_id = this.selectedTowerId;
    if (this.selectedBedrooms) filter.bedrooms = this.selectedBedrooms;
    if (this.minRent) filter.min_rent = this.minRent;
    if (this.maxRent) filter.max_rent = this.maxRent;

    this.flatService.getFlats(filter).subscribe({
      next: (flats) => {
        this.flats.set(flats);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load flats. Please try again.');
        this.isLoading.set(false);
      }
    });
  }

  applyFilters(): void {
    this.loadFlats();
  }

  clearFilters(): void {
    this.selectedTowerId = null;
    this.selectedBedrooms = null;
    this.minRent = null;
    this.maxRent = null;
    this.loadFlats();
  }
}
