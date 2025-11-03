import React from "react";

export function TACard({ name }) {
  const encodedName = encodeURIComponent(name); // safely encode spaces/parentheses
  const photoPath = `/photos/${encodedName}.png`;

  return (
    <div className="ta-card">
      <img
        src={photoPath}
        alt={name}
        className="ta-photo"
        onError={(e) => {
          e.target.onerror = null;
          e.target.src = "/photos/default.png"; // fallback
        }}
      />
      <p className="ta-name">{name}</p>
    </div>
  );
}
