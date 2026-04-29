import { useState, useMemo } from "react";
import InputPanel from "./components/InputPanel";
import MapView from "./components/MapView";
import RecommendationCard from "./components/RecommendationCard";
import { getRecommendations } from "./services/api";
import "./App.css";

const SORT_OPTIONS = [
  { value: "score", label: "Best Match" },
  { value: "price_asc", label: "Price (Low → High)" },
  { value: "price_desc", label: "Price (High → Low)" },
  { value: "distance", label: "Distance (Nearest)" },
  { value: "amenities", label: "Amenities (Highest)" },
];

export default function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [sortBy, setSortBy] = useState("score");

  const handleSubmit = async (params) => {
    setLoading(true);
    setError("");
    setMessage("");
    setRecommendations([]);

    try {
      const data = await getRecommendations(params);
      setRecommendations(data.recommendations || []);
      setMessage(data.message || "");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Sort recommendations based on selected criteria (frontend-only)
  const sortedRecommendations = useMemo(() => {
    if (!recommendations || recommendations.length === 0) return [];
    const sorted = [...recommendations];
    switch (sortBy) {
      case "price_asc":
        sorted.sort((a, b) => a.price - b.price);
        break;
      case "price_desc":
        sorted.sort((a, b) => b.price - a.price);
        break;
      case "distance":
        sorted.sort((a, b) => a.distance - b.distance);
        break;
      case "amenities":
        sorted.sort((a, b) => b.facility_score - a.facility_score);
        break;
      case "score":
      default:
        sorted.sort((a, b) => b.score - a.score);
        break;
    }
    return sorted;
  }, [recommendations, sortBy]);

  return (
    <div className="h-screen w-screen bg-mesh flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 px-6 py-4 border-b border-white/5
                         bg-slate-900/50 backdrop-blur-xl z-10">
        <div className="flex items-center justify-between max-w-[1600px] mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600
                            flex items-center justify-center text-xl shadow-lg shadow-violet-500/30">
              🏠
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-transparent bg-clip-text
                             bg-gradient-to-r from-violet-400 via-fuchsia-400 to-pink-400">
                AI Housing Recommender
              </h1>
              <p className="text-[11px] text-slate-500 font-medium tracking-wider uppercase">
                ML-Powered Property Search · 6 Cities
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            System Online
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-[380px] flex-shrink-0 border-r border-white/5
                          bg-slate-900/30 backdrop-blur-sm overflow-y-auto p-6">
          <div className="mb-6">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-1">
              Search Properties
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              Enter location, workplace, or landmark (e.g., "Saket, Delhi" or "IIT Delhi")
            </p>
          </div>

          <InputPanel onSubmit={handleSubmit} loading={loading} />

          {/* Error */}
          {error && (
            <div className="mt-5 p-4 rounded-xl bg-red-500/10 border border-red-500/20
                            text-red-400 text-sm animate-fade-in-up">
              <span className="font-semibold">Error: </span>{error}
            </div>
          )}

          {/* Message */}
          {message && !error && (
            <div className="mt-5 p-4 rounded-xl bg-violet-500/10 border border-violet-500/20
                            text-violet-300 text-sm animate-fade-in-up">
              {message}
            </div>
          )}

          {/* Supported Cities */}
          <div className="mt-8 p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Supported Cities
            </h3>
            <div className="flex flex-wrap gap-2">
              {["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"].map((c) => (
                <span key={c} className="px-2.5 py-1 rounded-full text-[10px] font-medium
                                         bg-white/5 text-slate-400 border border-white/5">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </aside>

        {/* Map + Cards */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Map */}
          <div className="flex-1 p-4 pb-2 min-h-0">
            <MapView recommendations={sortedRecommendations} />
          </div>

          {/* Recommendation Cards */}
          {sortedRecommendations.length > 0 && (
            <div className="flex-shrink-0 h-[280px] border-t border-white/5
                            bg-slate-900/30 backdrop-blur-sm">
              <div className="p-4 pb-0 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                    Recommendations
                  </h2>
                  <span className="text-xs text-slate-500">
                    {sortedRecommendations.length} properties found
                  </span>
                </div>

                {/* Sort Dropdown */}
                <div className="flex items-center gap-2">
                  <label htmlFor="sort-select" className="text-xs text-slate-500 font-medium">
                    Sort by
                  </label>
                  <select
                    id="sort-select"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10
                               text-sm text-slate-300 outline-none cursor-pointer
                               hover:border-violet-500/50 focus:border-violet-500
                               transition-all duration-200 appearance-none
                               bg-no-repeat bg-[length:12px] bg-[center_right_8px]"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394a3b8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E")`,
                      paddingRight: "28px"
                    }}
                  >
                    {SORT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="p-4 pt-3 flex gap-4 overflow-x-auto h-[230px]">
                {sortedRecommendations.map((rec, idx) => (
                  <div key={idx} className="min-w-[300px] max-w-[300px] animate-fade-in-up"
                       style={{ animationDelay: `${idx * 80}ms` }}>
                    <RecommendationCard rec={rec} index={idx} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
