import "server-only";

import { unstable_rethrow } from "next/navigation";

import { backendFetch } from "./backend";

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

/**
 * Catálogo completo, leído de MySQL a través del backend en cada visita.
 * Devuelve null si el backend no está disponible, para que la página lo diga en vez de romperse.
 */
export async function getProducts(): Promise<Product[] | null> {
  try {
    const response = await backendFetch("/api/products");
    if (!response.ok) {
      console.error(`El backend respondió ${response.status} al pedir el catálogo.`);
      return null;
    }
    return (await response.json()) as Product[];
  } catch (error) {
    // Los errores internos de Next.js (los que usa para prerenderizar) deben seguir su camino.
    unstable_rethrow(error);
    console.error("No se pudo leer el catálogo del backend:", error);
    return null;
  }
}
