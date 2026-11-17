"use client";

import type { ComponentProps, ReactNode } from "react";
import { useFormStatus } from "react-dom";

type Props = Omit<ComponentProps<"button">, "type" | "children"> & {
  children: ReactNode;
  /** Texto mientras se envía el formulario. */
  pendingLabel?: string;
  /** Si se indica, pide confirmación antes de enviar. */
  confirmMessage?: string;
};

/** Botón de envío para formularios con acción de servidor: se desactiva mientras se envía. */
export function SubmitButton({
  children,
  pendingLabel,
  confirmMessage,
  disabled,
  onClick,
  ...rest
}: Props) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending || disabled}
      onClick={(event) => {
        if (confirmMessage && !window.confirm(confirmMessage)) {
          event.preventDefault();
          return;
        }
        onClick?.(event);
      }}
      {...rest}
    >
      {pending && pendingLabel ? pendingLabel : children}
    </button>
  );
}
