
import { useEffect, useState } from "react";
import {
  evaluateLocationAutomation,
  fetchLocations,
  setLocationAutomationStrategy,
  type AutomationRecommendationDto,
  type AutomationStrategyKey,
  type LocationDto,
} from "../services/api";

export default function StrategyPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [strategy, setStrategy] =
    useState<AutomationStrategyKey>("conservative");
  const [savedStrategy, setSavedStrategy] =
    useState<AutomationStrategyKey | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [result, setResult] =
    useState<AutomationRecommendationDto | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadLocations() {
      try {
        const data = await fetchLocations();

        if (!cancelled) {
          setLocations(data);
          setLocationId(data[0]?.id ?? "");
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load locations.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadLocations();

    return () => {
      cancelled = true;
    };
  }, []);

  function clearFeedback() {
    setError("");
    setMessage("");
    setResult(null);
  }

  async function handleSave() {
    if (!locationId) {
      setError("Select a location first.");
      return;
    }

    try {
      setSaving(true);
      clearFeedback();

      await setLocationAutomationStrategy(locationId, strategy);
      setSavedStrategy(strategy);
      setMessage(`${strategy} strategy saved.`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to save strategy.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleEvaluate() {
    if (!locationId) {
      setError("Select a location first.");
      return;
    }

    if (savedStrategy !== strategy) {
      setError("Save the selected strategy before evaluating.");
      return;
    }

    try {
      setEvaluating(true);
      clearFeedback();

      const recommendation =
        await evaluateLocationAutomation(locationId);

      setResult(recommendation);
      setSavedStrategy(recommendation.strategy_key);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to evaluate automation.",
      );
    } finally {
      setEvaluating(false);
    }
  }

  const strategyDescription =
    strategy === "conservative"
      ? "Cautious decisions. Irrigate when moisture falls below the low threshold."
      : "More responsive decisions. Irrigate sooner as moisture approaches the low threshold.";

  return (
    <section
      id="automation"
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm md:col-span-2 lg:col-span-3"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-emerald-700">
            Automation Strategy
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Choose, save and evaluate a location's strategy.
          </p>
        </div>

        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
          {savedStrategy === strategy ? "Saved" : "Unsaved changes"}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <div>
          <label
            htmlFor="automation-location"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Location
          </label>
          <select
            id="automation-location"
            value={locationId}
            onChange={(event) => {
              setLocationId(event.target.value);
              setSavedStrategy(null);
              clearFeedback();
            }}
            disabled={loading || locations.length === 0}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          >
            <option value="">
              {loading ? "Loading locations..." : "Select location"}
            </option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="automation-strategy"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Strategy
          </label>
          <select
            id="automation-strategy"
            value={strategy}
            onChange={(event) => {
              setStrategy(event.target.value as AutomationStrategyKey);
              clearFeedback();
            }}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          >
            <option value="conservative">Conservative</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </div>

        <div className="flex items-end gap-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={!locationId || saving || evaluating || loading}
            className="flex-1 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            type="button"
            onClick={handleEvaluate}
            disabled={
              !locationId ||
              saving ||
              evaluating ||
              loading ||
              savedStrategy !== strategy
            }
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {evaluating ? "Checking..." : "Evaluate"}
          </button>
        </div>
      </div>

      <p className="mt-3 text-sm text-slate-500">
        {strategyDescription}
      </p>

      {locations.length === 0 && !loading && (
        <p className="mt-3 text-sm text-amber-700">
          Create a location in Configuration to use automation.
        </p>
      )}

      {error && (
        <p role="alert" className="mt-4 text-sm text-red-600">
          {error}
        </p>
      )}

      {message && (
        <p role="status" className="mt-4 text-sm text-emerald-700">
          {message}
        </p>
      )}

      {result && (
        <div className="mt-5 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-sm font-medium text-slate-600">
              Recommendation
            </span>
            <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium capitalize text-emerald-700">
              {result.strategy_key}
            </span>
          </div>

          <p className="mt-2 text-xl font-semibold capitalize text-slate-900">
            {result.action.replace(/[_-]/g, " ")}
          </p>
          <p className="mt-1 text-sm leading-5 text-slate-600">
            {result.reason}
          </p>
        </div>
      )}
    </section>
  );
}
