export interface HealthResponse {
  status: string;
}

export interface TokenResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}

export interface Publisher {
  id: number;
  name: string;
  webhook_url: string;
  user: string;
  game_count: number;
  created_at: string;
}

export interface Game {
  id: number;
  title: string;
  description: string;
  publisher: {
    id: number;
    name: string;
  };
  price: string;
  is_active: boolean;
  available_keys: number;
  created_at: string;
}

export interface OrderItem {
  id: number;
  game: number;
  game_title: string;
  game_key: number;
  key_string: string;
  price: string;
}

export interface Order {
  id: number;
  user: string;
  status: string;
  total_amount: string;
  created_at: string;
  completed_at: string | null;
  items: OrderItem[];
}
