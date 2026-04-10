"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";
import { useAnalysisStore } from "@/lib/stores/analysis-store";
import type { SSEEvent } from "@/types/analysis";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function AnalysisParams() {
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [hour, setHour] = useState(11);
  const [weight, setWeight] = useState(70);
  const [ftp, setFtp] = useState(4.5);
  const fileRef = useRef<HTMLInputElement>(null);
  const {
    selectedLibStage,
    setStageId,
    setData,
    setFigJson,
    setLoading,
    setSelectedLibStage,
  } = useAnalysisStore();

  async function runAnalysis() {
    const file = fileRef.current?.files?.[0];
    if (!file && !selectedLibStage) return;

    setLoading(true, "Iniciando...", 3);

    try {
      if (selectedLibStage) {
        // Analyze from library
        const fd = new FormData();
        fd.append("analysis_date", date);
        fd.append("start_hour", String(hour));
        fd.append("rider_weight", String(weight));
        fd.append("ftp_wkg", String(ftp));

        const { stage_id } = await api.post<{ stage_id: string }>(
          `/api/stages/${selectedLibStage}/analyze`,
          fd
        );
        setStageId(stage_id);
        subscribeSSE(stage_id);
      } else if (file) {
        // Upload and analyze new GPX
        const fd = new FormData();
        fd.append("file", file);
        fd.append("analysis_date", date);
        fd.append("start_hour", String(hour));
        fd.append("rider_weight", String(weight));
        fd.append("ftp_wkg", String(ftp));

        const { stage_id } = await api.post<{ stage_id: string }>(
          "/api/analysis/upload",
          fd
        );
        setStageId(stage_id);
        subscribeSSE(stage_id);
      }
    } catch (e) {
      setLoading(false);
      alert(e instanceof Error ? e.message : "Error");
    }
  }

  function subscribeSSE(stageId: string) {
    const es = new EventSource(`${API_URL}/api/analysis/sse/${stageId}`);

    es.onmessage = async (e) => {
      const event: SSEEvent = JSON.parse(e.data);

      if (event.type === "job_update" && event.job) {
        setLoading(true, event.job.msg, event.job.progress);
      } else if (event.type === "analysis_ready") {
        es.close();
        await loadAnalysisData(stageId);
      } else if (event.type === "error") {
        es.close();
        setLoading(false);
        alert("Error: " + (event.error || "Unknown"));
      }
    };

    es.onerror = () => {
      es.close();
      // Retry: check if analysis completed
      setTimeout(async () => {
        try {
          await loadAnalysisData(stageId);
        } catch {
          setLoading(false);
        }
      }, 3000);
    };
  }

  async function loadAnalysisData(stageId: string) {
    try {
      const [data, fig] = await Promise.all([
        api.get(`/api/analysis/data/${stageId}`),
        api.get(`/api/analysis/fig/${stageId}`),
      ]);
      setData(data as any);
      setFigJson(fig as any);
      setLoading(false);
    } catch {
      setLoading(false);
    }
  }

  function onFileSelected() {
    setSelectedLibStage(null);
  }

  return (
    <div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="mb-1 block text-[11px] uppercase tracking-widest text-muted">
            Fecha
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="h-[34px] w-full rounded-md border border-line bg-background px-2.5 font-mono text-xs text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-[11px] uppercase tracking-widest text-muted">
            Hora
          </label>
          <input
            type="number"
            value={hour}
            onChange={(e) => setHour(Number(e.target.value))}
            min={0}
            max={23}
            className="h-[34px] w-full rounded-md border border-line bg-background px-2.5 font-mono text-xs text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-[11px] uppercase tracking-widest text-muted">
            Peso (kg)
          </label>
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(Number(e.target.value))}
            className="h-[34px] w-full rounded-md border border-line bg-background px-2.5 font-mono text-xs text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-[11px] uppercase tracking-widest text-muted">
            FTP W/kg
          </label>
          <input
            type="number"
            value={ftp}
            onChange={(e) => setFtp(Number(e.target.value))}
            step={0.1}
            className="h-[34px] w-full rounded-md border border-line bg-background px-2.5 font-mono text-xs text-white"
          />
        </div>
      </div>

      <button
        onClick={runAnalysis}
        className="mt-3 w-full rounded-lg bg-accent py-2.5 text-sm font-bold text-white transition hover:bg-accent-hover"
      >
        ANALIZAR ETAPA
      </button>

      <div className="mt-4">
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-muted">
          Cargar GPX
        </label>
        <input
          ref={fileRef}
          type="file"
          accept=".gpx"
          onChange={onFileSelected}
          className="hidden"
        />
        <button
          onClick={() => fileRef.current?.click()}
          className="w-full rounded-lg border border-line bg-panel py-2 text-xs font-semibold text-muted transition hover:border-accent hover:text-accent"
        >
          Seleccionar archivo GPX
        </button>
      </div>
    </div>
  );
}
