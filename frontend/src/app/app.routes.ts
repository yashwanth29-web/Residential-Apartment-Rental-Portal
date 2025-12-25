import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './core/guards';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/flats',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'flats',
    loadComponent: () => import('./features/flats/flat-list/flat-list.component').then(m => m.FlatListComponent)
  },
  {
    path: 'flats/:id',
    loadComponent: () => import('./features/flats/flat-detail/flat-detail.component').then(m => m.FlatDetailComponent)
  },
  {
    path: 'amenities',
    loadComponent: () => import('./features/amenities/amenity-list/amenity-list.component').then(m => m.AmenityListComponent)
  },
  {
    path: 'bookings',
    loadComponent: () => import('./features/bookings/booking-list/booking-list.component').then(m => m.BookingListComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    loadComponent: () => import('./features/admin/admin-layout/admin-layout.component').then(m => m.AdminLayoutComponent),
    canActivate: [adminGuard],
    children: [
      {
        path: '',
        loadComponent: () => import('./features/admin/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'towers',
        loadComponent: () => import('./features/admin/tower-management/tower-management.component').then(m => m.TowerManagementComponent)
      },
      {
        path: 'flats',
        loadComponent: () => import('./features/admin/flat-management/flat-management.component').then(m => m.FlatManagementComponent)
      },
      {
        path: 'amenities',
        loadComponent: () => import('./features/admin/amenity-management/amenity-management.component').then(m => m.AmenityManagementComponent)
      },
      {
        path: 'bookings',
        loadComponent: () => import('./features/admin/booking-management/booking-management.component').then(m => m.BookingManagementComponent)
      },
      {
        path: 'tenants',
        loadComponent: () => import('./features/admin/tenant-management/tenant-management.component').then(m => m.TenantManagementComponent)
      },
      {
        path: 'reports',
        loadComponent: () => import('./features/admin/reports/reports.component').then(m => m.ReportsComponent)
      }
    ]
  }
];
