import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

interface AppConfig {
  apiUrl: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private config: AppConfig = {
    apiUrl: environment.apiUrl
  };

  constructor(private http: HttpClient) {}

  async loadConfig(): Promise<void> {
    // Only load runtime config in production
    if (environment.production) {
      try {
        const config = await firstValueFrom(
          this.http.get<AppConfig>('/assets/config.json')
        );
        if (config?.apiUrl) {
          this.config = config;
        }
      } catch (error) {
        console.warn('Could not load runtime config, using defaults');
      }
    }
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
