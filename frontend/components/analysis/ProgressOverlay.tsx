"use client";

import { useAnalysisStore } from "@/lib/stores/analysis-store";

export function ProgressOverlay() {
  const { isLoading, loadingMessage, loadingProgress } = useAnalysisStore();

  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 z-[300] flex flex-col items-center justify-center gap-4 bg-background/90 backdrop-blur-sm">
      <div className="text-xl font-extrabold uppercase tracking-[3px]">
        ANALIZANDO ETAPA
      </div>
      <div className="text-sm text-muted">{loadingMessage}</div>
      <div className="h-1 w-[300px] overflow-hidden rounded-full bg-panel-2">
        <div
          className="h-full bg-accent transition-all duration-300"
          style={{ width: `${loadingProgress}%` }}
        />
      </div>
    </div>
  );
}
