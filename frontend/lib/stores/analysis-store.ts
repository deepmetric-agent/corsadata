import { create } from "zustand";
import type { AnalysisData, RoadbookEvent, Waypoint } from "@/types/database";

type TabView = "principal" | "rampas" | "viento" | "lluvia" | "energia" | "pav";

interface AnalysisStore {
  // State
  stageId: string | null;
  data: AnalysisData | null;
  figJson: Record<string, unknown> | null;
  wpList: Waypoint[];
  activeTab: TabView;
  isLoading: boolean;
  loadingMessage: string;
  loadingProgress: number;
  selectedLibStage: string | null;

  // Actions
  setStageId: (id: string | null) => void;
  setData: (data: AnalysisData | null) => void;
  setFigJson: (fig: Record<string, unknown> | null) => void;
  setActiveTab: (tab: TabView) => void;
  setLoading: (loading: boolean, message?: string, progress?: number) => void;
  setSelectedLibStage: (id: string | null) => void;
  addWaypoint: (wp: Waypoint) => void;
  removeWaypoint: (idx: number) => void;
  setWaypoints: (wps: Waypoint[]) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  stageId: null,
  data: null,
  figJson: null,
  wpList: [],
  activeTab: "principal",
  isLoading: false,
  loadingMessage: "",
  loadingProgress: 0,
  selectedLibStage: null,

  setStageId: (id) => set({ stageId: id }),
  setData: (data) => set({ data }),
  setFigJson: (fig) => set({ figJson: fig }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setLoading: (loading, message = "", progress = 0) =>
    set({ isLoading: loading, loadingMessage: message, loadingProgress: progress }),
  setSelectedLibStage: (id) => set({ selectedLibStage: id }),
  addWaypoint: (wp) => set((s) => ({ wpList: [...s.wpList, wp] })),
  removeWaypoint: (idx) =>
    set((s) => ({ wpList: s.wpList.filter((_, i) => i !== idx) })),
  setWaypoints: (wps) => set({ wpList: wps }),
  reset: () =>
    set({
      stageId: null,
      data: null,
      figJson: null,
      wpList: [],
      activeTab: "principal",
      isLoading: false,
      loadingMessage: "",
      loadingProgress: 0,
    }),
}));
