// RocCurve.jsx
// Draws the ROC curve from the (fpr, tpr) points the backend returned, using a
// plain SVG. No charting library needed, so it is easy to read and explain.
//
// The ROC curve plots the True Positive Rate (y) against the False Positive
// Rate (x). A curve that hugs the top-left corner means a better detector.

export default function RocCurve({ points }) {
  const size = 260; // width and height of the drawing area in pixels
  const pad = 30; // space for the axes

  // Convert a value in [0,1] into a pixel position inside the padded box.
  const px = (fpr) => pad + fpr * (size - 2 * pad);
  const py = (tpr) => size - pad - tpr * (size - 2 * pad); // y grows downward

  // Turn the list of points into an SVG polyline "x,y x,y ..." string.
  const path = points.map((p) => `${px(p.fpr)},${py(p.tpr)}`).join(" ");

  return (
    <svg width={size} height={size} className="border rounded bg-white">
      {/* Diagonal reference line = random guessing (AUC 0.5). */}
      <line x1={px(0)} y1={py(0)} x2={px(1)} y2={py(1)}
            stroke="#ccc" strokeDasharray="4" />

      {/* Axes. */}
      <line x1={pad} y1={size - pad} x2={size - pad} y2={size - pad} stroke="#333" />
      <line x1={pad} y1={pad} x2={pad} y2={size - pad} stroke="#333" />

      {/* The ROC curve itself. */}
      <polyline points={path} fill="none" stroke="#f26522" strokeWidth="2" />

      {/* Axis labels. */}
      <text x={size / 2} y={size - 5} fontSize="11" textAnchor="middle">
        False Positive Rate
      </text>
      <text x={12} y={size / 2} fontSize="11" textAnchor="middle"
            transform={`rotate(-90 12 ${size / 2})`}>
        True Positive Rate
      </text>
    </svg>
  );
}
