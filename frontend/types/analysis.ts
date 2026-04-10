/**
 * Re-export analysis types from database.ts for convenience.
 * Additional frontend-specific analysis types.
 */
export type { AnalysisData, RoadbookEvent, StageStats, Waypoint } from "./database";

export interface PlotlyFigure {
  data: Record<string, unknown>[];
  layout: Record<string, unknown>;
}

export interface SSEEvent {
  type: "job_update" | "analysis_ready" | "error" | "keepalive";
  job?: { msg: string; progress: number };
  error?: string;
  stage_id?: string;
}
