import React, { useEffect } from "react";

export function TACard({ name }) {
  const encodedName = encodeURIComponent(name);
  const photoPath = `/photos/${encodedName}.png`;

  useEffect(() => {
    console.log("Looking for photo:", photoPath);
  }, [photoPath]);

  return (
    <div className="ta-card">
      <img
        src={photoPath}
        alt={name}
        className="ta-photo"
        onError={(e) => {
          console.warn("Photo not found:", photoPath);
          e.target.onerror = null;
          e.target.src = "/photos/default.png";
        }}
      />
      <p className="ta-name">{name}</p>
    </div>
  );
}
