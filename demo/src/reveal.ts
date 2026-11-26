// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Reveal a chart once, the first time it scrolls into view. Without
// IntersectionObserver the chart is simply shown.
import { useEffect, useState, type RefObject } from "react";

export function useRevealOnce(ref: RefObject<Element | null>): string {
  const [state, setState] = useState<"idle" | "armed" | "in">("idle");
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    setState("armed");
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setState("in");
          io.disconnect();
        }
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref]);
  return state === "idle" ? "" : state === "armed" ? " reveal-armed" : " reveal-armed is-in";
}
