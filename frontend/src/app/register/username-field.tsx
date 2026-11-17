"use client";

import { useEffect, useState } from "react";

import { type UsernameCheck, checkUsername } from "@/actions/auth";
import { USERNAME_HINT, USERNAME_PATTERN, normalizeUsername } from "@/lib/validation";

type CheckedName = UsernameCheck & { username: string };

/** Campo del nombre de usuario que comprueba, mientras se escribe, si ya existe. */
export function UsernameField({ defaultValue = "" }: { defaultValue?: string }) {
  const [value, setValue] = useState(defaultValue);
  const [checked, setChecked] = useState<CheckedName | null>(null);
  const username = normalizeUsername(value);
  const wellFormed = USERNAME_PATTERN.test(username);

  useEffect(() => {
    if (!wellFormed) {
      return;
    }
    let cancelled = false;
    // Se espera a que deje de escribir un momento para no preguntar en cada tecla.
    const timer = window.setTimeout(async () => {
      const result = await checkUsername(username);
      if (!cancelled) {
        setChecked({ username, ...result });
      }
    }, 350);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [username, wellFormed]);

  let tone: "muted" | "ok" | "bad" = "muted";
  let text = USERNAME_HINT;
  if (username && !wellFormed) {
    tone = "bad";
  } else if (wellFormed && checked?.username !== username) {
    text = "Comprobando si está libre…";
  } else if (wellFormed && checked?.available === true) {
    tone = "ok";
    text = `«${username}» está libre.`;
  } else if (wellFormed && checked?.available === false) {
    tone = "bad";
    text = checked.message ?? "Ese nombre de usuario ya existe.";
  }

  const toneClass = { muted: "text-ink-soft", ok: "text-brass", bad: "text-oxblood-deep" }[tone];

  return (
    <label className="field">
      Nombre de usuario
      <input
        name="username"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        autoComplete="username"
        autoCapitalize="none"
        spellCheck={false}
        required
        maxLength={30}
        aria-invalid={tone === "bad" || undefined}
        aria-describedby="username-status"
        className="input"
      />
      <span id="username-status" aria-live="polite" className={`text-xs font-normal ${toneClass}`}>
        {text}
      </span>
    </label>
  );
}
