/** Valor de texto de un campo de formulario, o cadena vacía si no viene. */
export function field(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

/** Primer valor de un parámetro de la URL. */
export function firstParam(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/** Texto asociado a una clave que llega de la URL, sin tropezar con propiedades heredadas. */
export function pick(texts: Record<string, string>, key: string | undefined): string | null {
  return key !== undefined && Object.hasOwn(texts, key) ? texts[key] : null;
}
