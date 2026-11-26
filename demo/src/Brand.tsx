// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Brand mark and wordmark as inline SVG paths (same geometry as public/brand/*.svg).
// The mark is a cascade in its first round: a seed (bottom) has passed the
// content to one neighbour (filled) and not yet to the other (ring); the two
// links draw a V. Wordmark: "Viral" in Familjen Grotesk (OFL 1.1, weight 700),
// converted to outlines.
export const LINKS = "M121.12 144.09L87.65 86.11L63.4 100.11L96.88 158.09ZM159.12 158.09L192.6 100.11L168.35 86.11L134.88 144.09Z";
export const SEED = "M86 184A42 42 0 1 0 170 184A42 42 0 1 0 86 184Z";
export const LEFT = "M28.03 68A33 33 0 1 0 94.03 68A33 33 0 1 0 28.03 68Z";
export const RIGHT = "M161.97 68A33 33 0 1 0 227.97 68A33 33 0 1 0 161.97 68ZM175.97 68A19 19 0 1 0 213.97 68A19 19 0 1 0 175.97 68Z";
export const WORD = "M30.38 0 1 -96.75V-97.5H22.25L46 -18H49L72.5 -97.5H92.75V-96.75L63.38 0ZM102.4 0V-75H122.65V0ZM112.53 -83.62Q107.15 -83.62 104.4 -86.44Q101.65 -89.25 101.65 -93.75Q101.65 -98.25 104.4 -101.06Q107.15 -103.88 112.53 -103.88Q117.9 -103.88 120.65 -101.06Q123.4 -98.25 123.4 -93.75Q123.4 -89.25 120.65 -86.44Q117.9 -83.62 112.53 -83.62ZM140.3 0V-75H158.8V-61.25H161.8Q162.55 -65 164.61 -68.31Q166.68 -71.62 170.93 -73.69Q175.18 -75.75 182.3 -75.75H186.3V-57.5H180.8Q170.18 -57.5 165.36 -52.12Q160.55 -46.75 160.55 -36V0ZM224.2 1.5Q213.7 1.5 206.95 -3.56Q200.2 -8.62 196.95 -17.5Q193.7 -26.38 193.7 -37.62Q193.7 -49.25 197.01 -58Q200.33 -66.75 207.08 -71.62Q213.83 -76.5 224.08 -76.5Q231.95 -76.5 237.01 -73.44Q242.08 -70.38 244.7 -65.25H247.7V-75H266.45V0H247.7V-9.75H244.7Q242.08 -5 237.08 -1.75Q232.08 1.5 224.2 1.5ZM229.45 -12.75Q237.08 -12.75 241.64 -19.44Q246.2 -26.12 246.2 -37.5Q246.2 -49 241.64 -55.62Q237.08 -62.25 229.45 -62.25Q222.58 -62.25 218.64 -56.06Q214.7 -49.88 214.7 -37.5Q214.7 -25.12 218.64 -18.94Q222.58 -12.75 229.45 -12.75ZM290.48 0Q286.98 -4 285.54 -9.06Q284.1 -14.12 284.1 -22.38V-100H304.35V-24.5Q304.35 -15 306.48 -9.69Q308.6 -4.38 312.1 -0.75V0Z";
export const WORD_BOX = [1.00, -103.88, 312.10, 1.50] as const;

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
