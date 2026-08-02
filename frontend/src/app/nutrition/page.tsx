"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function NutritionPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [form, setForm] = useState({
    age: 30,
    gender: "female",
    height_cm: 162,
    weight_kg: 58,
    activity_level: "moderate",
    goals: "general wellness",
  });
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.nutrition(token, form));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Nutrition Plan</h1>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {Object.entries(form).map(([key, value]) => (
            <label key={key} className="block text-sm capitalize">
              {key.replaceAll("_", " ")}
              <input
                className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
                value={value}
                onChange={(e) =>
                  setForm({
                    ...form,
                    [key]: ["age", "height_cm", "weight_kg"].includes(key)
                      ? Number(e.target.value)
                      : e.target.value,
                  })
                }
              />
            </label>
          ))}
        </div>
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Generate</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Plan</h2>
        {result ? (
          <div className="mt-4 space-y-2">
            <p>BMI {result.bmi} ({result.bmi_category})</p>
            <p>Calories: {result.daily_calories}</p>
            <p>Water: {result.water_intake_liters} L</p>
            <pre className="overflow-auto rounded-2xl bg-white/50 p-3 dark:bg-white/5">
              {JSON.stringify(result.diet_plan, null, 2)}
            </pre>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Generate a general wellness plan.</p>
        )}
      </div>
    </div>
  );
}
