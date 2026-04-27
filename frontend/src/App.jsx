import { useState } from "react";
import InputPanel from "./components/InputPanel";
import MapView from "./components/MapView";
import RecommendationCard from "./components/RecommendationCard";
import { getRecommendations } from "./services/api";
import "./App.css";

export default function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

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
        <aside className="w-[360px] flex-shrink-0 border-r border-white/5
                          bg-slate-900/30 backdrop-blur-sm overflow-y-auto p-5">
          <div className="mb-5">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-1">
              Search Properties
            </h2>
            <p className="text-xs text-slate-500">
              Enter location as "Area, City" (e.g., Saket, Delhi)
            </p>
          </div>

          <InputPanel onSubmit={handleSubmit} loading={loading} />

          {/* Error */}
          {error && (
            <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20
                            text-red-400 text-sm animate-fade-in-up">
              <span className="font-semibold">Error: </span>{error}
            </div>
          )}

          {/* Message */}
          {message && !error && (
            <div className="mt-4 p-3 rounded-xl bg-violet-500/10 border border-violet-500/20
                            text-violet-300 text-sm animate-fade-in-up">
              {message}
            </div>
          )}

          {/* Supported Cities */}
          <div className="mt-6 p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
              Supported Cities
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"].map((c) => (
                <span key={c} className="px-2 py-0.5 rounded-full text-[10px] font-medium
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
            <MapView recommendations={recommendations} />
          </div>

          {/* Recommendation Cards */}
          {recommendations.length > 0 && (
            <div className="flex-shrink-0 h-[280px] border-t border-white/5
                            bg-slate-900/30 backdrop-blur-sm">
              <div className="p-4 pb-0 flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                  Recommendations
                </h2>
                <span className="text-xs text-slate-500">
                  {recommendations.length} properties found
                </span>
              </div>
              <div className="p-4 pt-3 flex gap-4 overflow-x-auto h-[230px]">
                {recommendations.map((rec, idx) => (
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
