const euros = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
  // Sin esto, en español los números de cuatro cifras salen sin punto de millar («4800 €»).
  useGrouping: "always",
});

const dateTime = new Intl.DateTimeFormat("es-ES", {
  dateStyle: "medium",
  timeStyle: "short",
  timeZone: "Europe/Madrid",
});

const day = new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeZone: "Europe/Madrid" });

/** 480000 → «4.800 €» */
export function formatPrice(priceCents: number): string {
  return euros.format(priceCents / 100);
}

/** Fecha y hora en hora peninsular. El backend las manda en UTC con la «Z». */
export function formatDateTime(iso: string): string {
  return dateTime.format(new Date(iso));
}

export function formatDay(iso: string): string {
  return day.format(new Date(iso));
}
