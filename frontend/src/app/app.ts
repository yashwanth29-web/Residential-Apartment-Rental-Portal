import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent, FooterComponent, AlertComponent } from './shared';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, FooterComponent, AlertComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = 'Apartment Portal';
}
