import React from "react";

export function TACard({ name }) {
//   const cleanName = name
//     .replace(/\s*\(.*?\)\s*/g, "") // remove anything in parentheses like (TA)
//     .trim()
//     .replace(/\s+/g, "_"); // replace spaces with underscores

  const photoPath = `/photos/${name}.png`; // e.g. "Aidan_Nguyen.jpg"

  return (
    <div className="ta-card">
      <img
        src={photoPath}
        alt={name}
        className="ta-photo"
        onError={(e) => {
          e.target.onerror = null;
          e.target.src = "/photos/default.png"; // fallback if no photo found
        }}
      />
      <p className="ta-name">{name}</p>
    </div>
  );
}
