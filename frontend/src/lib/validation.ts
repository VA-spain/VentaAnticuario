/** Reglas del nombre de usuario y la contraseña: las mismas que aplica el backend. */

export const USERNAME_PATTERN = /^[a-z][a-z0-9._-]{2,29}$/;
export const MIN_PASSWORD_LENGTH = 8;
export const MAX_PASSWORD_LENGTH = 128;

export const USERNAME_HINT =
  "De 3 a 30 caracteres: empieza por una letra y usa solo letras, números, punto, guion o guion bajo.";

/** Los nombres de usuario no distinguen mayúsculas: se guardan en minúsculas. */
export function normalizeUsername(value: string): string {
  return value.trim().toLowerCase();
}
