import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, CreateFlatRequest } from '../services/admin.service';
import { Flat, Tower } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components';
import { AlertService } from '../../../shared/services';

@Component({
  selector: 'app-flat-management',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './flat-management.component.html'
})
export class FlatManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  private alertService = inject(AlertService);

  flats = signal<Flat[]>([]);
  towers = signal<Tower[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Modal state
  showModal = signal(false);
  isEditing = signal(false);
  editingFlatId = signal<number | null>(null);
  isSaving = signal(false);

  // Form data
  formData: CreateFlatRequest = {
    tower_id: 0,
    unit_number: '',
    floor: 1,
    bedrooms: 1,
    bathrooms: 1,
    rent: 0,
    area_sqft: undefined,
    is_available: true
  };

  // Delete confirmation
  showDeleteConfirm = signal(false);
  deletingFlatId = signal<number | null>(null);
  isDeleting = signal(false);

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading.set(true);
    this.error.set(null);

    // Load towers first
    this.adminService.getTowers().subscribe({
      next: (towers) => {
        this.towers.set(towers);
        this.loadFlats();
      },
      error: () => {
        this.error.set('Failed to load towers');
        this.isLoading.set(false);
      }
    });
  }

  loadFlats(): void {
    this.adminService.getFlats().subscribe({
      next: (flats) => {
        this.flats.set(flats);
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load flats');
        this.isLoading.set(false);
      }
    });
  }

  openCreateModal(): void {
    this.formData = {
      tower_id: this.towers().length > 0 ? this.towers()[0].id : 0,
      unit_number: '',
      floor: 1,
      bedrooms: 1,
      bathrooms: 1,
      rent: 0,
      area_sqft: undefined,
      is_available: true
    };
    this.isEditing.set(false);
    this.editingFlatId.set(null);
    this.showModal.set(true);
  }

  openEditModal(flat: Flat): void {
    this.formData = {
      tower_id: flat.tower_id,
      unit_number: flat.unit_number,
      floor: flat.floor,
      bedrooms: flat.bedrooms,
      bathrooms: flat.bathrooms,
      rent: flat.rent,
      area_sqft: flat.area_sqft || undefined,
      is_available: flat.is_available
    };
    this.isEditing.set(true);
    this.editingFlatId.set(flat.id);
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  saveFlat(): void {
    if (!this.formData.tower_id || !this.formData.unit_number || this.formData.rent <= 0) {
      this.alertService.error('Please fill in all required fields');
      return;
    }

    // Ensure numeric fields are proper integers/numbers (HTML inputs can return strings)
    const payload: CreateFlatRequest = {
      tower_id: Number(this.formData.tower_id),
      unit_number: this.formData.unit_number,
      floor: Number(this.formData.floor),
      bedrooms: Number(this.formData.bedrooms),
      bathrooms: Number(this.formData.bathrooms),
      rent: Number(this.formData.rent),
      area_sqft: this.formData.area_sqft ? Number(this.formData.area_sqft) : undefined,
      is_available: this.formData.is_available
    };

    this.isSaving.set(true);

    if (this.isEditing() && this.editingFlatId()) {
      this.adminService.updateFlat(this.editingFlatId()!, payload).subscribe({
        next: () => {
          this.alertService.success('Flat updated successfully');
          this.closeModal();
          this.loadFlats();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to update flat');
          this.isSaving.set(false);
        }
      });
    } else {
      this.adminService.createFlat(payload).subscribe({
        next: () => {
          this.alertService.success('Flat created successfully');
          this.closeModal();
          this.loadFlats();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to create flat');
          this.isSaving.set(false);
        }
      });
    }
  }

  confirmDelete(flat: Flat): void {
    this.deletingFlatId.set(flat.id);
    this.showDeleteConfirm.set(true);
  }

  cancelDelete(): void {
    this.showDeleteConfirm.set(false);
    this.deletingFlatId.set(null);
  }

  deleteFlat(): void {
    if (!this.deletingFlatId()) return;

    this.isDeleting.set(true);

    this.adminService.deleteFlat(this.deletingFlatId()!).subscribe({
      next: () => {
        this.alertService.success('Flat deleted successfully');
        this.cancelDelete();
        this.loadFlats();
        this.isDeleting.set(false);
      },
      error: (err) => {
        this.alertService.error(err.error?.error?.message || 'Failed to delete flat');
        this.isDeleting.set(false);
      }
    });
  }

  getTowerName(towerId: number): string {
    const tower = this.towers().find(t => t.id === towerId);
    return tower?.name || 'Unknown';
  }
}
