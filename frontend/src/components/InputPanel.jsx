import { useState } from "react";

const FACILITY_OPTIONS = [
  "Gymnasium", "Swimming Pool", "Car Parking", "24x7 Security",
  "Power Backup", "Club House", "Landscaped Gardens", "Indoor Games",
  "Jogging Track", "Sports Facility", "Shopping Mall", "Hospital",
  "School", "ATM", "Intercom", "Lift Available", "Wifi",
  "AC", "Rain Water Harvesting", "Cafeteria",
  "Airport Proximity", "Metro Proximity", "Mall Proximity",
  "School Proximity", "Hospital Proximity"
];

export default function InputPanel({ onSubmit, loading }) {
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState(5000000);
  const [radius, setRadius] = useState(10);
  const [facilities, setFacilities] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const formatCurrency = (val) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(1)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)} L`;
    return `₹${val.toLocaleString("en-IN")}`;
  };

  const toggleFacility = (fac) => {
    setFacilities((prev) =>
      prev.includes(fac) ? prev.filter((f) => f !== fac) : [...prev, fac]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!location.trim()) return;
    onSubmit({ location: location.trim(), budget, radius, facilities });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-5 w-full"
    >
      {/* Location Input */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Location
        </label>
        <input
          id="location-input"
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="e.g. Saket, Delhi"
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10
                     text-white placeholder-slate-500 outline-none
                     focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20
                     transition-all duration-300"
          required
        />
      </div>

      {/* Budget Slider */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Budget: <span className="text-violet-400">{formatCurrency(budget)}</span>
        </label>
        <input
          id="budget-slider"
          type="range"
          min={500000}
          max={50000000}
          step={100000}
          value={budget}
          onChange={(e) => setBudget(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer
                     bg-gradient-to-r from-violet-600/30 to-fuchsia-600/30
                     [&::-webkit-slider-thumb]:appearance-none
                     [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
                     [&::-webkit-slider-thumb]:rounded-full
                     [&::-webkit-slider-thumb]:bg-gradient-to-r
                     [&::-webkit-slider-thumb]:from-violet-500
                     [&::-webkit-slider-thumb]:to-fuchsia-500
                     [&::-webkit-slider-thumb]:shadow-lg
                     [&::-webkit-slider-thumb]:shadow-violet-500/30
                     [&::-webkit-slider-thumb]:cursor-pointer"
        />
        <div className="flex justify-between text-xs text-slate-500">
          <span>₹5L</span>
          <span>₹5 Cr</span>
        </div>
      </div>

      {/* Distance Slider */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Radius: <span className="text-emerald-400">{radius} km</span>
        </label>
        <input
          id="radius-slider"
          type="range"
          min={1}
          max={50}
          step={1}
          value={radius}
          onChange={(e) => setRadius(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer
                     bg-gradient-to-r from-emerald-600/30 to-teal-600/30
                     [&::-webkit-slider-thumb]:appearance-none
                     [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
                     [&::-webkit-slider-thumb]:rounded-full
                     [&::-webkit-slider-thumb]:bg-gradient-to-r
                     [&::-webkit-slider-thumb]:from-emerald-500
                     [&::-webkit-slider-thumb]:to-teal-500
                     [&::-webkit-slider-thumb]:shadow-lg
                     [&::-webkit-slider-thumb]:shadow-emerald-500/30
                     [&::-webkit-slider-thumb]:cursor-pointer"
        />
        <div className="flex justify-between text-xs text-slate-500">
          <span>1 km</span>
          <span>50 km</span>
        </div>
      </div>

      {/* Facilities Multi-Select */}
      <div className="flex flex-col gap-2 relative">
        <label className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Facilities {facilities.length > 0 && (
            <span className="text-violet-400">({facilities.length})</span>
          )}
        </label>
        <button
          id="facilities-dropdown"
          type="button"
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10
                     text-left text-slate-400 outline-none
                     hover:border-violet-500/50 focus:border-violet-500
                     transition-all duration-300"
        >
          {facilities.length === 0
            ? "Select preferred facilities..."
            : facilities.slice(0, 3).join(", ") +
              (facilities.length > 3 ? ` +${facilities.length - 3} more` : "")}
          <span className="float-right">{dropdownOpen ? "▲" : "▼"}</span>
        </button>

        {dropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 max-h-60 overflow-y-auto
                          rounded-xl bg-slate-800/95 backdrop-blur-xl border border-white/10
                          shadow-2xl shadow-black/50 z-50">
            {FACILITY_OPTIONS.map((fac) => (
              <label
                key={fac}
                className="flex items-center gap-3 px-4 py-2.5 cursor-pointer
                           hover:bg-white/5 transition-colors duration-150"
              >
                <input
                  type="checkbox"
                  checked={facilities.includes(fac)}
                  onChange={() => toggleFacility(fac)}
                  className="w-4 h-4 rounded accent-violet-500"
                />
                <span className="text-sm text-slate-300">{fac}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <button
        id="search-button"
        type="submit"
        disabled={loading || !location.trim()}
        className="w-full py-3.5 rounded-xl font-semibold text-white
                   bg-gradient-to-r from-violet-600 to-fuchsia-600
                   hover:from-violet-500 hover:to-fuchsia-500
                   disabled:opacity-40 disabled:cursor-not-allowed
                   shadow-lg shadow-violet-500/25
                   transition-all duration-300 hover:shadow-violet-500/40
                   hover:-translate-y-0.5 active:translate-y-0
                   flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10"
                      stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Searching...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Find Properties
          </>
        )}
      </button>
    </form>
  );
}
