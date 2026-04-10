/**
 * Database types for Director Hub PRO.
 * In production, generate these with: supabase gen types typescript
 * These are manual placeholders matching the schema.
 */

export type Role = "director" | "coach" | "analyst" | "rider";
export type RiderStatus = "active" | "injured" | "inactive";
export type RaceStatus = "upcoming" | "ongoing" | "completed" | "cancelled";
export type Plan = "free" | "pro" | "enterprise";

export interface Team {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  plan: Plan;
  created_at: string;
}

export interface Profile {
  id: string;
  team_id: string;
  full_name: string | null;
  role: Role;
  avatar_url: string | null;
  created_at: string;
}

export interface Rider {
  id: string;
  team_id: string;
  full_name: string;
  birth_date: string | null;
  nationality: string | null;
  weight_kg: number | null;
  height_cm: number | null;
  ftp_w: number | null;
  ftp_wkg: number | null;
  vo2max: number | null;
  contract_end: string | null;
  status: RiderStatus;
  notes: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface Stage {
  id: string;
  team_id: string;
  name: string;
  race_name: string | null;
  stage_number: number | null;
  distance_km: number | null;
  d_pos_m: number | null;
  points: number | null;
  gpx_url: string | null;
  thumbnail_url: string | null;
  race_id: string | null;
  created_by: string | null;
  created_at: string;
}

export interface StageAnalysis {
  id: string;
  stage_id: string;
  team_id: string;
  rider_id: string | null;
  analysis_date: string | null;
  start_hour: number | null;
  rider_weight_kg: number | null;
  ftp_wkg: number | null;
  analysis_json: Record<string, unknown> | null;
  fig_json: Record<string, unknown> | null;
  roadbook: RoadbookEvent[] | null;
  stats: StageStats | null;
  created_at: string;
}

export interface Waypoint {
  id: string;
  analysis_id: string;
  team_id: string;
  name: string;
  type: string | null;
  km: number;
  lat: number;
  lon: number;
  alt: number | null;
  created_at: string;
}

export interface Race {
  id: string;
  team_id: string;
  name: string;
  start_date: string | null;
  end_date: string | null;
  category: string | null;
  country: string | null;
  status: RaceStatus;
  created_at: string;
  updated_at: string;
}

export interface RaceEntry {
  id: string;
  race_id: string;
  rider_id: string;
  team_id: string;
  role: string | null;
  result: string | null;
  created_at: string;
}

export interface PerformanceEntry {
  id: string;
  rider_id: string;
  team_id: string;
  date: string;
  type: string | null;
  distance_km: number | null;
  duration_min: number | null;
  avg_power_w: number | null;
  normalized_power_w: number | null;
  tss: number | null;
  ftp_tested: number | null;
  notes: string | null;
  created_at: string;
}

export interface FTPHistoryEntry {
  id: string;
  rider_id: string;
  team_id: string;
  date: string;
  ftp_w: number;
  ftp_wkg: number | null;
  created_at: string;
}

// Analysis-specific types
export interface RoadbookEvent {
  type: string;
  km: number;
  km_end?: number;
  label: string;
  severity?: "high" | "medium" | "low";
}

export interface StageStats {
  d_pos?: number;
  d_neg?: number;
  total_kj?: number;
  est_time_min?: number;
  wind?: {
    speed?: number;
    direction?: number;
  };
}

export interface AnalysisData {
  dists: number[];
  alts: number[];
  lats: number[];
  lons: number[];
  bearings: number[];
  pends: number[];
  colors_grade: string[];
  colors_wind: string[];
  colors_rain: string[];
  colors_danger: string[];
  colors_surf: string[];
  wind_dirs: string[];
  rain_km: number[];
  surf_map: string[];
  roadbook: RoadbookEvent[];
  tactical_summary: { summary: string };
  stats: StageStats;
  idx_staff: number;
  idx_cursor: number;
}
