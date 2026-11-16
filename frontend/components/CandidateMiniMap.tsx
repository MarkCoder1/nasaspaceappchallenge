"use client";

import { useEffect, useRef } from "react";

export default function CandidateMiniMap({ latitude, longitude, name }: { latitude: number; longitude: number; name: string }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    let mapInstance: { remove: () => void } | null = null;
    import("leaflet").then((mod) => {
      if (cancelled || !containerRef.current) return;
      const L = mod.default ?? mod;
      const map = L.map(containerRef.current, {
        center: [latitude, longitude],
        zoom: 6,
        minZoom: 1,
        maxZoom: 12,
        attributionControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        boxZoom: false,
        keyboard: false,
        zoomControl: false,
      });
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap",
      }).addTo(map);
      const marker = L.circleMarker([latitude, longitude], {
        radius: 10,
        color: "#0b0f0c",
        weight: 2,
        fillColor: "#b7d36b",
        fillOpacity: 0.9,
      });
      marker.addTo(map);
      marker.bindTooltip(name, { permanent: false, direction: "top" });
      mapInstance = map;
    }).catch(() => {
      // Leaflet unavailable; mini-map omitted silently (terrain preview & table remain)
    });
    return () => {
      cancelled = true;
      mapInstance?.remove?.();
      mapInstance = null;
    };
  }, [latitude, longitude, name]);

  return (
    <div className="candidate-mini-map-wrap">
      <div ref={containerRef} className="candidate-mini-map" role="img" aria-label={`Mini map showing location of ${name}`} />
      <p className="candidate-mini-map-caption">Location: {latitude.toFixed(2)}°, {longitude.toFixed(2)}° (WGS84)</p>
    </div>
  );
}
