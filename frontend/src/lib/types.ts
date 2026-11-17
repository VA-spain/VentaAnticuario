/** Formas de los datos que devuelve el backend. */

export type Product = {
  id: number;
  slug: string;
  name: string;
  category: string;
  period: string;
  origin: string;
  description: string;
  price_cents: number;
  image_path: string;
  image_alt: string;
  image_author: string;
  image_license: string;
  image_source_url: string;
};

/** Quién tiene la sesión abierta. `is_admin` depende del formato de su cookie. */
export type SessionUser = {
  username: string;
  is_admin: boolean;
  first_name: string | null;
  last_name: string | null;
};

export type Profile = {
  username: string;
  is_admin: boolean;
  is_active: boolean;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  passport_number: string | null;
  card_number: string | null;
  card_expiry: string | null;
  card_cvv: string | null;
  created_at: string;
  last_login_at: string | null;
};

export type OrderStatus = "confirmed" | "shipped" | "delivered" | "cancelled";

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  confirmed: "Confirmado",
  shipped: "Enviado",
  delivered: "Entregado",
  cancelled: "Cancelado",
};

export type Order = {
  id: number;
  product: Product;
  quantity: number;
  unit_price_cents: number;
  status: OrderStatus;
  created_at: string;
};

export type AdminUserRow = {
  username: string;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  orders_count: number;
  favorites_count: number;
};
