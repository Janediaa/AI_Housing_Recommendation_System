function getScoreBadgeClasses(score) {
  if (score >= 7)
    return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  if (score >= 4)
    return "bg-amber-500/20 text-amber-400 border-amber-500/30";
  return "bg-red-500/20 text-red-400 border-red-500/30";
}

function formatMonthlyPrice(price) {
  // price from backend is annual; convert to monthly
  const monthly = price / 12;
  if (monthly >= 100000) return `₹${(monthly / 100000).toFixed(1)}L`;
  if (monthly >= 1000) return `₹${Math.round(monthly).toLocaleString("en-IN")}`;
  return `₹${Math.round(monthly).toLocaleString("en-IN")}`;
}

const amenityIcons = {
  airport: "✈️",
  school: "🏫",
  hospital: "🏥",
  mall: "🛍️",
  metro: "🚇",
};

export default function RecommendationCard({ rec, index }) {
  return (
    <div
      className="group relative rounded-2xl overflow-hidden
                 bg-white/[0.03] backdrop-blur-md
                 border border-white/[0.08]
                 hover:border-violet-500/30 hover:bg-white/[0.06]
                 transition-all duration-500 hover:-translate-y-1
                 hover:shadow-xl hover:shadow-violet-500/10"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Top bar with score */}
      <div className="flex items-center justify-between p-4 pb-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            #{index + 1}
          </span>
          <h3 className="text-base font-bold text-white truncate max-w-[160px]">
            {rec.location}
          </h3>
        </div>
        <div
          className={`px-3 py-1.5 rounded-full border text-sm font-extrabold
                      ${getScoreBadgeClasses(rec.score)}`}
        >
          {rec.score}/10
        </div>
      </div>

      <div className="text-xs text-slate-500 px-4 pt-1 capitalize">
        {rec.city}
      </div>

      {/* Price & Key Stats */}
      <div className="p-4 pt-3">
        <div className="text-2xl font-extrabold text-transparent bg-clip-text
                        bg-gradient-to-r from-violet-400 to-fuchsia-400 mb-1">
          {formatMonthlyPrice(rec.price)}
        </div>
        <div className="text-[11px] text-slate-500 mb-3">per month (est.)</div>

        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="rounded-xl bg-white/5 px-3 py-2 text-center">
            <div className="text-xs text-slate-500">BHK</div>
            <div className="text-sm font-bold text-white">{rec.bhk}</div>
          </div>
          <div className="rounded-xl bg-white/5 px-3 py-2 text-center">
            <div className="text-xs text-slate-500">Area</div>
            <div className="text-sm font-bold text-white">{rec.area} <span className="text-xs text-slate-500">sqft</span></div>
          </div>
          <div className="rounded-xl bg-white/5 px-3 py-2 text-center">
            <div className="text-xs text-slate-500">Dist</div>
            <div className="text-sm font-bold text-white">{rec.distance} <span className="text-xs text-slate-500">km</span></div>
          </div>
        </div>

        {/* Amenities */}
        {rec.amenities && (
          <div className="flex flex-wrap gap-2 mb-3">
            {Object.entries(rec.amenities).map(([key, val]) => (
              <div
                key={key}
                className="flex items-center gap-1 px-2 py-1 rounded-lg
                           bg-white/5 text-xs"
                title={`${key}: ${val}/5`}
              >
                <span>{amenityIcons[key] || "📍"}</span>
                <span className="text-slate-400 capitalize">{key}</span>
                <span className={`font-bold ${val >= 3 ? "text-emerald-400" : val >= 1 ? "text-amber-400" : "text-red-400"}`}>
                  {val}/5
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Highlights */}
        {rec.highlights && rec.highlights.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {rec.highlights.map((h) => (
              <span
                key={h}
                className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase
                           tracking-wider border
                           bg-violet-500/10 text-violet-300 border-violet-500/20"
              >
                {h}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
