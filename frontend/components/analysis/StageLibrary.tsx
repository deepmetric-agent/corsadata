"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAnalysisStore } from "@/lib/stores/analysis-store";
import type { Stage } from "@/types/database";

export function StageLibrary() {
  const [stages, setStages] = useState<Stage[]>([]);
  const { selectedLibStage, setSelectedLibStage } = useAnalysisStore();

  useEffect(() => {
    loadStages();
  }, []);

  async function loadStages() {
    try {
      const data = await api.get<Stage[]>("/api/stages");
      setStages(data);
    } catch {
      setStages([]);
    }
  }

  if (!stages.length) {
    return (
      <div className="py-5 text-center text-xs text-muted">
        Sin etapas guardadas
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      {stages.map((stage) => (
        <button
          key={stage.id}
          onClick={() => setSelectedLibStage(stage.id === selectedLibStage ? null : stage.id)}
          className={`w-full rounded-lg border p-2.5 text-left transition ${
            selectedLibStage === stage.id
              ? "border-accent bg-accent/10"
              : "border-line bg-panel-2 hover:border-accent"
          }`}
        >
          <div className="text-[13px] font-bold">{stage.name}</div>
          <div className="mt-0.5 font-mono text-[11px] text-muted">
            {stage.distance_km ?? "?"}km · D+{stage.d_pos_m ?? "?"}m · {stage.points ?? "?"} pts
          </div>
        </button>
      ))}
    </div>
  );
}
