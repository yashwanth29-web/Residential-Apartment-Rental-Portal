import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html'
})
export class NavbarComponent {
  private authService = inject(AuthService);
  
  isAuthenticated = this.authService.isAuthenticated;
  isAdmin = this.authService.isAdmin;
  currentUser = this.authService.currentUser;

  logout(): void {
    this.authService.logout();
  }
}
