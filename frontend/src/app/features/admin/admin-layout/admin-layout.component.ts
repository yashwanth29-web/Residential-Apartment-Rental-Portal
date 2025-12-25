import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './admin-layout.component.html'
})
export class AdminLayoutComponent {
  navItems = [
    { path: '/admin', label: 'Dashboard', exact: true },
    { path: '/admin/towers', label: 'Towers', exact: false },
    { path: '/admin/flats', label: 'Flats', exact: false },
    { path: '/admin/amenities', label: 'Amenities', exact: false },
    { path: '/admin/bookings', label: 'Bookings', exact: false },
    { path: '/admin/tenants', label: 'Tenants', exact: false },
    { path: '/admin/reports', label: 'Reports', exact: false }
  ];
}
