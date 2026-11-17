"use client";

import { useEffect, useState } from "react";

/**
 * Para formularios que se envían de la forma clásica (POST y recarga de página): desactiva el
 * botón al enviar para evitar el doble clic, y lo reactiva si el navegador restaura la página al
 * volver atrás.
 */
export function usePendingSubmit() {
  const [active, setActive] = useState(false);

  useEffect(() => {
    const reset = (event: PageTransitionEvent) => {
      if (event.persisted) {
        setActive(false);
      }
    };
    window.addEventListener("pageshow", reset);
    return () => window.removeEventListener("pageshow", reset);
  }, []);

  return { active, start: () => setActive(true) };
}
