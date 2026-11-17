"use client";

import { useSyncExternalStore } from "react";

const noSubscription = () => () => {};

/**
 * Parámetros de la URL leídos en el navegador. Al prerenderizar se ven vacíos, y tras hidratar
 * React vuelve a pintar con los de verdad: así un formulario no necesita <Suspense> ni se
 * sustituye por otro mientras alguien ya está escribiendo en él.
 */
export function useUrlParams(): URLSearchParams {
  const search = useSyncExternalStore(
    noSubscription,
    () => window.location.search,
    () => "",
  );
  return new URLSearchParams(search);
}
