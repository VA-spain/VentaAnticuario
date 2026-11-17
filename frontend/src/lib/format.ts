const euros = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
  // Sin esto, en español los números de cuatro cifras salen sin punto de millar («4800 €»).
  useGrouping: "always",
});

/** 480000 → «4.800 €» */
export function formatPrice(priceCents: number): string {
  return euros.format(priceCents / 100);
}
