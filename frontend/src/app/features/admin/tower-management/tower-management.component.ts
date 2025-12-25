import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, CreateTowerRequest } from '../services/admin.service';
import { Tower, Amenity } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components';
import { AlertService } from '../../../shared/services';

@Component({
  selector: 'app-tower-management',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './tower-management.component.html'
})
export class TowerManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  private alertService = inject(AlertService);

  towers = signal<Tower[]>([]);
  amenities = signal<Amenity[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Modal state
  showModal = signal(false);
  isEditing = signal(false);
  editingTowerId = signal<number | null>(null);
  isSaving = signal(false);

  // Form data
  formData: CreateTowerRequest = {
    name: '',
    address: '',
    total_floors: 1,
    flats_per_floor: 4,
    amenity_ids: []
  };

  // Selected amenities for the form
  selectedAmenityIds: number[] = [];

  // Delete confirmation
  showDeleteConfirm = signal(false);
  deletingTowerId = signal<number | null>(null);
  isDeleting = signal(false);

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    this.error.set(null);

    // Load amenities first
    this.adminService.getAmenities().subscribe({
      next: (amenities) => {
        this.amenities.set(amenities);
        this.loadTowers();
      },
      error: () => {
        // Continue loading towers even if amenities fail
        this.loadTowers();
      }
    });
  }

  loadTowers(): void {
    this.adminService.getTowers().subscribe({
      next: (towers) => {
        this.towers.set(towers);
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load towers');
        this.isLoading.set(false);
      }
    });
  }

  openCreateModal(): void {
    this.formData = { name: '', address: '', total_floors: 1, flats_per_floor: 4, amenity_ids: [] };
    this.selectedAmenityIds = [];
    this.isEditing.set(false);
    this.editingTowerId.set(null);
    this.showModal.set(true);
  }

  openEditModal(tower: Tower): void {
    this.formData = {
      name: tower.name,
      address: tower.address || '',
      total_floors: tower.total_floors,
      flats_per_floor: tower.flats_per_floor || 4,
      amenity_ids: tower.amenity_ids || []
    };
    this.selectedAmenityIds = tower.amenity_ids || [];
    this.isEditing.set(true);
    this.editingTowerId.set(tower.id);
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.formData = { name: '', address: '', total_floors: 1, flats_per_floor: 4, amenity_ids: [] };
    this.selectedAmenityIds = [];
  }

  toggleAmenity(amenityId: number): void {
    const index = this.selectedAmenityIds.indexOf(amenityId);
    if (index > -1) {
      this.selectedAmenityIds.splice(index, 1);
    } else {
      this.selectedAmenityIds.push(amenityId);
    }
  }

  isAmenitySelected(amenityId: number): boolean {
    return this.selectedAmenityIds.includes(amenityId);
  }

  saveTower(): void {
    if (!this.formData.name || this.formData.total_floors < 1 || (this.formData.flats_per_floor && this.formData.flats_per_floor < 1)) {
      this.alertService.error('Please fill in all required fields');
      return;
    }

    // Ensure numeric fields are proper integers
    const payload: CreateTowerRequest = {
      name: this.formData.name,
      address: this.formData.address,
      total_floors: Number(this.formData.total_floors),
      flats_per_floor: Number(this.formData.flats_per_floor),
      amenity_ids: this.selectedAmenityIds
    };

    this.isSaving.set(true);

    if (this.isEditing() && this.editingTowerId()) {
      this.adminService.updateTower(this.editingTowerId()!, payload).subscribe({
        next: () => {
          this.alertService.success('Tower updated successfully');
          this.closeModal();
          this.loadTowers();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to update tower');
          this.isSaving.set(false);
        }
      });
    } else {
      this.adminService.createTower(payload).subscribe({
        next: () => {
          this.alertService.success('Tower created successfully');
          this.closeModal();
          this.loadTowers();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to create tower');
          this.isSaving.set(false);
        }
      });
    }
  }

  confirmDelete(tower: Tower): void {
    this.deletingTowerId.set(tower.id);
    this.showDeleteConfirm.set(true);
  }

  cancelDelete(): void {
    this.showDeleteConfirm.set(false);
    this.deletingTowerId.set(null);
  }

  deleteTower(): void {
    if (!this.deletingTowerId()) return;

    this.isDeleting.set(true);

    this.adminService.deleteTower(this.deletingTowerId()!).subscribe({
      next: () => {
        this.alertService.success('Tower deleted successfully');
        this.cancelDelete();
        this.loadTowers();
        this.isDeleting.set(false);
      },
      error: (err) => {
        this.alertService.error(err.error?.error?.message || 'Failed to delete tower');
        this.isDeleting.set(false);
      }
    });
  }

  getAmenityNames(tower: Tower): string {
    if (!tower.amenities || tower.amenities.length === 0) {
      return '-';
    }
    return tower.amenities.map(a => a.name).join(', ');
  }
}
