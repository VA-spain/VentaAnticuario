/** Clases de un enlace del menú principal, marcado o no como la página actual. */
export function navLinkClass(isCurrent: boolean): string {
  return `rounded-sm px-3 py-2 transition-colors hover:text-oxblood ${
    isCurrent ? "text-oxblood underline decoration-1 underline-offset-8" : "text-ink"
  }`;
}
