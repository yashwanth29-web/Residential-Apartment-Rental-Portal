import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, CreateAmenityRequest } from '../services/admin.service';
import { Amenity } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components';
import { AlertService } from '../../../shared/services';

@Component({
  selector: 'app-amenity-management',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './amenity-management.component.html'
})
export class AmenityManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  private alertService = inject(AlertService);

  amenities = signal<Amenity[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Modal state
  showModal = signal(false);
  isEditing = signal(false);
  editingAmenityId = signal<number | null>(null);
  isSaving = signal(false);

  // Form data
  formData: CreateAmenityRequest = {
    name: '',
    type: 'common',
    description: '',
    hours: '',
    fee: undefined
  };

  amenityTypes: Array<{ value: 'gym' | 'pool' | 'parking' | 'common'; label: string }> = [
    { value: 'gym', label: 'Gym' },
    { value: 'pool', label: 'Pool' },
    { value: 'parking', label: 'Parking' },
    { value: 'common', label: 'Common Area' }
  ];

  // Delete confirmation
  showDeleteConfirm = signal(false);
  deletingAmenityId = signal<number | null>(null);
  isDeleting = signal(false);

  ngOnInit(): void {
    this.loadAmenities();
  }

  loadAmenities(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.adminService.getAmenities().subscribe({
      next: (amenities) => {
        this.amenities.set(amenities);
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load amenities');
        this.isLoading.set(false);
      }
    });
  }

  openCreateModal(): void {
    this.formData = {
      name: '',
      type: 'common',
      description: '',
      hours: '',
      fee: undefined
    };
    this.isEditing.set(false);
    this.editingAmenityId.set(null);
    this.showModal.set(true);
  }

  openEditModal(amenity: Amenity): void {
    this.formData = {
      name: amenity.name,
      type: amenity.type as 'gym' | 'pool' | 'parking' | 'common',
      description: amenity.description || '',
      hours: amenity.hours || '',
      fee: amenity.fee || undefined
    };
    this.isEditing.set(true);
    this.editingAmenityId.set(amenity.id);
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  saveAmenity(): void {
    if (!this.formData.name || !this.formData.type) {
      this.alertService.error('Please fill in all required fields');
      return;
    }

    this.isSaving.set(true);

    if (this.isEditing() && this.editingAmenityId()) {
      this.adminService.updateAmenity(this.editingAmenityId()!, this.formData).subscribe({
        next: () => {
          this.alertService.success('Amenity updated successfully');
          this.closeModal();
          this.loadAmenities();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to update amenity');
          this.isSaving.set(false);
        }
      });
    } else {
      this.adminService.createAmenity(this.formData).subscribe({
        next: () => {
          this.alertService.success('Amenity created successfully');
          this.closeModal();
          this.loadAmenities();
          this.isSaving.set(false);
        },
        error: (err) => {
          this.alertService.error(err.error?.error?.message || 'Failed to create amenity');
          this.isSaving.set(false);
        }
      });
    }
  }

  confirmDelete(amenity: Amenity): void {
    this.deletingAmenityId.set(amenity.id);
    this.showDeleteConfirm.set(true);
  }

  cancelDelete(): void {
    this.showDeleteConfirm.set(false);
    this.deletingAmenityId.set(null);
  }

  deleteAmenity(): void {
    if (!this.deletingAmenityId()) return;

    this.isDeleting.set(true);

    this.adminService.deleteAmenity(this.deletingAmenityId()!).subscribe({
      next: () => {
        this.alertService.success('Amenity deleted successfully');
        this.cancelDelete();
        this.loadAmenities();
        this.isDeleting.set(false);
      },
      error: (err) => {
        this.alertService.error(err.error?.error?.message || 'Failed to delete amenity');
        this.isDeleting.set(false);
      }
    });
  }

  getTypeLabel(type: string): string {
    const found = this.amenityTypes.find(t => t.value === type);
    return found?.label || type;
  }

  getTypeBadgeClass(type: string): string {
    const classes: Record<string, string> = {
      gym: 'bg-blue-100 text-blue-800',
      pool: 'bg-cyan-100 text-cyan-800',
      parking: 'bg-gray-100 text-gray-800',
      common: 'bg-green-100 text-green-800'
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
  }
}
