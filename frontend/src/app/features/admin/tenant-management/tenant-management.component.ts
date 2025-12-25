import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService, Tenant, TenantDetails } from '../services/admin.service';
import { LoadingSpinnerComponent } from '../../../shared/components';
import { AlertService } from '../../../shared/services';

@Component({
  selector: 'app-tenant-management',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  templateUrl: './tenant-management.component.html'
})
export class TenantManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  private alertService = inject(AlertService);

  tenants = signal<Tenant[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Detail modal
  showDetailModal = signal(false);
  selectedTenantDetails = signal<TenantDetails | null>(null);
  isLoadingDetails = signal(false);

  // Terminate lease confirmation
  showTerminateConfirm = signal(false);
  terminatingLeaseId = signal<number | null>(null);
  isTerminating = signal(false);

  ngOnInit(): void {
    this.loadTenants();
  }

  loadTenants(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.adminService.getTenants().subscribe({
      next: (tenants) => {
        this.tenants.set(tenants);
        this.isLoading.set(false);
      },
      error: () => {
        this.error.set('Failed to load tenants');
        this.isLoading.set(false);
      }
    });
  }

  viewTenantDetails(tenant: Tenant): void {
    this.isLoadingDetails.set(true);
    this.showDetailModal.set(true);

    this.adminService.getTenant(tenant.id).subscribe({
      next: (details) => {
        this.selectedTenantDetails.set(details);
        this.isLoadingDetails.set(false);
      },
      error: () => {
        this.alertService.error('Failed to load tenant details');
        this.closeDetailModal();
      }
    });
  }

  closeDetailModal(): void {
    this.showDetailModal.set(false);
    this.selectedTenantDetails.set(null);
    this.isLoadingDetails.set(false);
  }

  confirmTerminateLease(leaseId: number): void {
    this.terminatingLeaseId.set(leaseId);
    this.showTerminateConfirm.set(true);
  }

  cancelTerminate(): void {
    this.showTerminateConfirm.set(false);
    this.terminatingLeaseId.set(null);
  }

  terminateLease(): void {
    const leaseId = this.terminatingLeaseId();
    if (!leaseId) return;

    this.isTerminating.set(true);

    this.adminService.terminateLease(leaseId).subscribe({
      next: () => {
        this.alertService.success('Lease terminated successfully');
        this.cancelTerminate();
        this.closeDetailModal();
        this.loadTenants();
        this.isTerminating.set(false);
      },
      error: (err) => {
        this.alertService.error(err.error?.error?.message || 'Failed to terminate lease');
        this.isTerminating.set(false);
      }
    });
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  getActiveLeaseCount(tenant: Tenant): number {
    return tenant.active_leases?.length || 0;
  }
}
