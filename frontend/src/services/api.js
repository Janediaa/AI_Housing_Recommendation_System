import axios from "axios";

const API_BASE = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Get housing recommendations from the backend.
 * @param {Object} params
 * @param {string} params.location - Location name (e.g., "Saket, Delhi")
 * @param {number} params.budget - Budget in INR
 * @param {number} params.radius - Search radius in km
 * @param {string[]} params.facilities - Preferred facility names
 * @returns {Promise<{recommendations: Array, message: string}>}
 */
export async function getRecommendations({ location, budget, radius, facilities }) {
  try {
    const response = await api.post("/recommend", {
      location,
      budget,
      radius,
      facilities,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      const detail = error.response.data?.detail || "Server error";
      throw new Error(detail);
    } else if (error.request) {
      throw new Error(
        "Cannot reach the backend server. Make sure it's running on http://localhost:8000"
      );
    } else {
      throw new Error(error.message || "Unknown error occurred");
    }
  }
}

export default api;
