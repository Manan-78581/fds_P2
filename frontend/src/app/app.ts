import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { ApiService } from './api.service';
import { Game, Order, Publisher } from './api.types';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly api = inject(ApiService);

  protected readonly title = signal('GameKey Platform');
  protected readonly token = signal('');
  protected readonly status = signal('Checking API...');
  protected readonly publishers = signal<Publisher[]>([]);
  protected readonly games = signal<Game[]>([]);
  protected readonly orders = signal<Order[]>([]);
  protected readonly busy = signal(false);
  protected readonly message = signal('');

  protected authUser = '';
  protected authEmail = '';
  protected authPassword = '';

  protected publisherName = '';
  protected webhookUrl = '';
  protected webhookSecret = '';

  protected gameTitle = '';
  protected gameDescription = '';
  protected gamePrice = '29.99';
  protected selectedPublisherId: number | null = null;

  protected orderGameId: number | null = null;

  protected readonly hasToken = computed(() => this.token().length > 0);

  constructor() {
    void this.loadHealth();
  }

  protected async loadHealth(): Promise<void> {
    try {
      const result = await firstValueFrom(this.api.health());
      this.status.set(`API online: ${result.status}`);
    } catch {
      this.status.set('API offline. Start the Django backend at http://127.0.0.1:8000/');
    }
  }

  protected async register(): Promise<void> {
    if (!this.authUser || !this.authEmail || !this.authPassword) {
      this.message.set('Enter username, email, and password first.');
      return;
    }

    this.busy.set(true);
    try {
      const response = await firstValueFrom(
        this.api.register({
          username: this.authUser,
          email: this.authEmail,
          password: this.authPassword,
        })
      );
      this.token.set(response.token);
      this.message.set(`Registered ${response.user.username} and stored API token.`);
      await this.refreshData();
    } catch (error) {
      this.message.set('Registration failed. Check the backend and your inputs.');
    } finally {
      this.busy.set(false);
    }
  }

  protected async login(): Promise<void> {
    if (!this.authUser || !this.authPassword) {
      this.message.set('Enter username and password first.');
      return;
    }

    this.busy.set(true);
    try {
      const response = await firstValueFrom(
        this.api.login({
          username: this.authUser,
          password: this.authPassword,
        })
      );
      this.token.set(response.token);
      this.message.set('Token loaded. You are authenticated.');
      await this.refreshData();
    } catch {
      this.message.set('Login failed. Verify credentials and backend availability.');
    } finally {
      this.busy.set(false);
    }
  }

  protected async createPublisher(): Promise<void> {
    if (!this.hasToken()) {
      this.message.set('Register or log in first.');
      return;
    }
    if (!this.publisherName || !this.webhookUrl || !this.webhookSecret) {
      this.message.set('Fill in the publisher form first.');
      return;
    }

    this.busy.set(true);
    try {
      await firstValueFrom(
        this.api.createPublisher(this.token(), {
          name: this.publisherName,
          webhook_url: this.webhookUrl,
          webhook_secret: this.webhookSecret,
        })
      );
      this.publisherName = '';
      this.webhookUrl = '';
      this.webhookSecret = '';
      this.message.set('Publisher created.');
      await this.refreshData();
    } catch {
      this.message.set('Could not create publisher. Make sure the token is valid.');
    } finally {
      this.busy.set(false);
    }
  }

  protected async createGame(): Promise<void> {
    if (!this.hasToken() || this.selectedPublisherId === null) {
      this.message.set('Create or select a publisher first.');
      return;
    }
    if (!this.gameTitle || !this.gamePrice) {
      this.message.set('Fill in the game form first.');
      return;
    }

    this.busy.set(true);
    try {
      await firstValueFrom(
        this.api.createGame(this.token(), {
          title: this.gameTitle,
          description: this.gameDescription,
          price: this.gamePrice,
          publisher: this.selectedPublisherId!,
          is_active: true,
        })
      );
      this.gameTitle = '';
      this.gameDescription = '';
      this.message.set('Game created.');
      await this.refreshData();
    } catch {
      this.message.set('Could not create game. Check that the selected publisher belongs to this account.');
    } finally {
      this.busy.set(false);
    }
  }

  protected async purchaseGame(): Promise<void> {
    if (!this.hasToken() || this.orderGameId === null) {
      this.message.set('Select a game first.');
      return;
    }

    this.busy.set(true);
    try {
      await firstValueFrom(this.api.createOrder(this.token(), this.orderGameId!));
      this.message.set('Order completed and game key assigned.');
      await this.refreshData();
    } catch {
      this.message.set('Purchase failed. Ensure an active key exists for the selected game.');
    } finally {
      this.busy.set(false);
    }
  }

  protected pickPublisher(id: number): void {
    this.selectedPublisherId = id;
  }

  protected pickGame(id: number): void {
    this.orderGameId = id;
  }

  protected async refreshData(): Promise<void> {
    if (!this.hasToken()) {
      return;
    }

    try {
      const [publishers, games, orders] = await Promise.all([
        firstValueFrom(this.api.listPublishers(this.token())),
        firstValueFrom(this.api.listGames(this.token())),
        firstValueFrom(this.api.listOrders(this.token())),
      ]);

      this.publishers.set(publishers);
      this.games.set(games);
      this.orders.set(orders);
      if (this.selectedPublisherId === null && publishers.length > 0) {
        this.selectedPublisherId = publishers[0].id;
      }
      if (this.orderGameId === null && games.length > 0) {
        this.orderGameId = games[0].id;
      }
    } catch {
      this.message.set('Authenticated, but data could not be loaded.');
    }
  }
}
