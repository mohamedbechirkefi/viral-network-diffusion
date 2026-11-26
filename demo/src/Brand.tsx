// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Brand mark and wordmark as inline SVG paths (same geometry as public/brand/*.svg).
// The mark is a cascade in its first round: a seed (bottom) has passed the
// content to one neighbour (filled) and not yet to the other (ring); the two
// links draw a V. Wordmark: "Viral" in Archivo (OFL 1.1, weight 760, width 78),
// converted to outlines.
export const LINKS = "M121.12 144.09L87.65 86.11L63.4 100.11L96.88 158.09ZM159.12 158.09L192.6 100.11L168.35 86.11L134.88 144.09Z";
export const SEED = "M86 184A42 42 0 1 0 170 184A42 42 0 1 0 86 184Z";
export const LEFT = "M28.03 68A33 33 0 1 0 94.03 68A33 33 0 1 0 28.03 68Z";
export const RIGHT = "M161.97 68A33 33 0 1 0 227.97 68A33 33 0 1 0 161.97 68ZM175.97 68A19 19 0 1 0 213.97 68A19 19 0 1 0 175.97 68Z";
export const WORD = "M28.29 0 1.37 -103.07H25.85L39.13 -45.22Q39.66 -42.79 40.29 -39.26Q40.93 -35.72 41.62 -32.13Q42.32 -28.54 42.78 -25.76H43.8Q44.19 -27.74 44.76 -30.85Q45.33 -33.97 46.03 -37.7Q46.72 -41.43 47.4 -45.18L60.68 -103.07H84.33L57.45 0ZM94.75 -90.56V-108.62H115.48V-90.56ZM94.75 0V-79.07H115.48V0ZM131.95 0V-79.07H149.3L150.69 -67.78H151.48Q152.9 -71.78 155.01 -74.7Q157.11 -77.63 160.01 -79.27Q162.92 -80.9 166.56 -80.9Q168.32 -80.9 169.91 -80.58Q171.5 -80.26 172.62 -79.75V-59.39H165.84Q162.32 -59.39 159.82 -58.14Q157.31 -56.89 155.72 -54.38Q154.14 -51.88 153.41 -48.1Q152.68 -44.31 152.68 -39.29V0ZM199.78 1.8Q195.39 1.8 191.52 0.6Q187.65 -0.6 184.7 -3.19Q181.74 -5.79 180.09 -10Q178.44 -14.22 178.44 -20.15Q178.44 -27.22 181.04 -32.39Q183.64 -37.57 188.76 -40.96Q193.89 -44.35 201.58 -46Q209.27 -47.64 219.39 -47.64V-55.22Q219.39 -58.24 218.48 -60.35Q217.57 -62.46 215.65 -63.66Q213.73 -64.85 210.56 -64.85Q207.16 -64.85 205.09 -63.69Q203.01 -62.53 202.12 -60.61Q201.23 -58.69 201.23 -56.22V-54.83H181.47Q181.32 -55.46 181.32 -56.08Q181.32 -56.7 181.32 -57.46Q181.32 -65.09 184.94 -70.31Q188.56 -75.53 195.27 -78.2Q201.98 -80.87 211.19 -80.87Q219.62 -80.87 226.14 -78.51Q232.66 -76.15 236.39 -70.71Q240.12 -65.27 240.12 -55.91V-19.71Q240.12 -17.3 241.3 -15.97Q242.48 -14.63 244.61 -14.63H248.43V-0.9Q246.26 0.15 243.04 0.93Q239.81 1.71 235.98 1.71Q231.87 1.71 228.82 0.46Q225.77 -0.79 223.91 -3.06Q222.05 -5.32 221.4 -8.31H220.6Q218.59 -5.49 215.73 -3.19Q212.88 -0.89 208.97 0.46Q205.07 1.8 199.78 1.8ZM207.77 -14.3Q210.36 -14.3 212.5 -15.36Q214.63 -16.42 216.17 -18.32Q217.71 -20.21 218.55 -22.89Q219.39 -25.56 219.39 -28.8V-35.5Q212.37 -35.5 208 -34.01Q203.63 -32.53 201.64 -29.79Q199.66 -27.05 199.66 -23.21Q199.66 -20.33 200.6 -18.33Q201.55 -16.32 203.36 -15.31Q205.17 -14.3 207.77 -14.3ZM257.8 0V-108.62H278.53V0Z";
export const WORD_BOX = [1.37, -108.62, 278.53, 1.80] as const;

export function Mark({ size = 28 }: { size?: number }) {
  return (
    <svg className="mark" width={size} height={size} viewBox="0 0 256 256" aria-hidden="true" focusable="false">
      <path className="mark-ink" d={LINKS} />
      <path className="mark-hot" d={SEED} />
      <path className="mark-hot" d={LEFT} />
      <path className="mark-ink" fillRule="evenodd" d={RIGHT} />
    </svg>
  );
}

export function Wordmark({ height = 22 }: { height?: number }) {
  const [x0, y0, x1, y1] = WORD_BOX;
  const w = x1 - x0, h = y1 - y0;
  return (
    <svg className="wordmark" height={height} width={(height * w) / h} viewBox={`${x0} ${y0} ${w} ${h}`} aria-hidden="true" focusable="false">
      <path d={WORD} />
    </svg>
  );
}
