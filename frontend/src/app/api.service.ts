import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Game, HealthResponse, Order, Publisher, TokenResponse } from './api.types';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'https://fsd-phase-2-8ulb.onrender.com/api';

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health/`);
  }

  register(payload: { username: string; email: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.baseUrl}/register/`, payload);
  }

  login(payload: { username: string; password: string }): Observable<{ token: string }> {
    return this.http.post<{ token: string }>(`${this.baseUrl}/token/`, payload);
  }

  listPublishers(token: string): Observable<Publisher[]> {
    return this.http.get<Publisher[]>(`${this.baseUrl}/publishers/`, { headers: this.authHeaders(token) });
  }

  listGames(token: string): Observable<Game[]> {
    return this.http.get<Game[]>(`${this.baseUrl}/games/`, { headers: this.authHeaders(token) });
  }

  listOrders(token: string): Observable<Order[]> {
    return this.http.get<Order[]>(`${this.baseUrl}/orders/`, { headers: this.authHeaders(token) });
  }

  createPublisher(token: string, payload: { name: string; webhook_url: string; webhook_secret: string }): Observable<Publisher> {
    return this.http.post<Publisher>(`${this.baseUrl}/publishers/`, payload, { headers: this.authHeaders(token) });
  }

  createGame(token: string, payload: { title: string; description: string; price: string; publisher: number; is_active: boolean }): Observable<Game> {
    return this.http.post<Game>(`${this.baseUrl}/games/`, payload, { headers: this.authHeaders(token) });
  }

  createOrder(token: string, gameId: number): Observable<Order> {
    return this.http.post<Order>(`${this.baseUrl}/orders/`, { game_id: gameId }, { headers: this.authHeaders(token) });
  }

  private authHeaders(token: string): HttpHeaders {
    return new HttpHeaders({ Authorization: `Token ${token}` });
  }
}
