import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default marker icons in Leaflet + bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function getScoreColor(score) {
  if (score >= 7) return "#22c55e";      // green
  if (score >= 4) return "#eab308";      // yellow
  return "#ef4444";                       // red
}

export default function MapView({ recommendations }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  // Initialize map
  useEffect(() => {
    if (mapInstanceRef.current) return;

    mapInstanceRef.current = L.map(mapRef.current, {
      center: [20.5937, 78.9629], // India center
      zoom: 5,
      zoomControl: true,
      scrollWheelZoom: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(mapInstanceRef.current);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when recommendations change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    if (!recommendations || recommendations.length === 0) return;

    const bounds = [];

    recommendations.forEach((rec, idx) => {
      const color = getScoreColor(rec.score);

      // Custom colored icon
      const icon = L.divIcon({
        className: "custom-marker",
        html: `
          <div style="
            width: 36px; height: 36px;
            background: ${color};
            border: 3px solid white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 13px; color: white;
            box-shadow: 0 4px 12px ${color}80;
            font-family: system-ui;
          ">${rec.score}</div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      // Format price as monthly
      const formatMonthlyPrice = (p) => {
        const monthly = p / 12;
        if (monthly >= 100000) return `₹${(monthly / 100000).toFixed(1)}L/mo`;
        return `₹${Math.round(monthly).toLocaleString("en-IN")}/mo`;
      };

      const popup = L.popup().setContent(`
        <div style="font-family: system-ui; min-width: 180px;">
          <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px; color: #1e293b;">
            ${rec.location}
          </div>
          <div style="font-size: 13px; color: #475569; line-height: 1.7;">
            <strong>Price:</strong> ${formatMonthlyPrice(rec.price)}<br/>
            <strong>BHK:</strong> ${rec.bhk}<br/>
            <strong>Area:</strong> ${rec.area} sqft<br/>
            <strong>Distance:</strong> ${rec.distance} km<br/>
            <strong>Score:</strong> <span style="color: ${color}; font-weight: 700;">${rec.score}/10</span>
          </div>
        </div>
      `);

      const marker = L.marker([rec.lat, rec.lng], { icon })
        .addTo(map)
        .bindPopup(popup);

      markersRef.current.push(marker);
      bounds.push([rec.lat, rec.lng]);
    });

    // Fit map to markers
    if (bounds.length > 0) {
      const latLngBounds = L.latLngBounds(bounds);
      map.fitBounds(latLngBounds, { padding: [50, 50], maxZoom: 14 });
    }
  }, [recommendations]);

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden
                    border border-white/10 shadow-2xl shadow-black/30">
      <div ref={mapRef} className="w-full h-full" style={{ minHeight: "400px" }} />

      {/* Map legend */}
      <div className="absolute bottom-4 left-4 z-[1000]
                      bg-slate-900/90 backdrop-blur-sm rounded-lg
                      px-3 py-2 border border-white/10">
        <div className="text-xs text-slate-400 font-semibold mb-1">Score</div>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500 inline-block"></span>
            ≥7
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-yellow-500 inline-block"></span>
            4–6
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500 inline-block"></span>
            &lt;4
          </span>
        </div>
      </div>
    </div>
  );
}
