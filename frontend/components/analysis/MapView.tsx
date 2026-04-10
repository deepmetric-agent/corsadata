"use client";

import { useCallback, useEffect, useRef } from "react";
import { useAnalysisStore } from "@/lib/stores/analysis-store";

interface MapViewProps {
  hoverKm: number | null;
}

export function MapView({ hoverKm }: MapViewProps) {
  const { data } = useAnalysisStore();
  const mapRef = useRef<HTMLDivElement>(null);
  const panoRef = useRef<HTMLDivElement>(null);
  const gmapRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.Marker | null>(null);
  const panoObjRef = useRef<google.maps.StreetViewPanorama | null>(null);

  // Initialize map when data loads
  useEffect(() => {
    if (!data?.lats || !mapRef.current || !window.google?.maps) return;

    const lats = data.lats;
    const lons = data.lons;

    if (!gmapRef.current) {
      gmapRef.current = new google.maps.Map(mapRef.current, {
        zoom: 10,
        mapTypeId: "terrain",
        styles: [
          { featureType: "poi", stylers: [{ visibility: "off" }] },
          { featureType: "transit", stylers: [{ visibility: "off" }] },
        ],
      });
    }

    const path: google.maps.LatLngLiteral[] = [];
    const bounds = new google.maps.LatLngBounds();
    const step = Math.max(1, Math.floor(lats.length / 500));

    for (let i = 0; i < lats.length; i += step) {
      const p = { lat: lats[i], lng: lons[i] };
      path.push(p);
      bounds.extend(p);
    }

    new google.maps.Polyline({
      path,
      map: gmapRef.current,
      strokeColor: "#ff3e3e",
      strokeWeight: 4,
      strokeOpacity: 0.9,
    });

    if (!markerRef.current) {
      markerRef.current = new google.maps.Marker({
        map: gmapRef.current,
        position: path[0],
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: "#ff3e3e",
          fillOpacity: 1,
          strokeColor: "#fff",
          strokeWeight: 2,
        },
      });
    }

    gmapRef.current.fitBounds(bounds);

    // Street View
    if (panoRef.current) {
      try {
        panoObjRef.current = new google.maps.StreetViewPanorama(panoRef.current, {
          position: path[0],
          pov: { heading: 0, pitch: 0 },
          zoom: 1,
          addressControl: false,
          showRoadLabels: false,
        });
      } catch {}
    }
  }, [data]);

  // Move marker on hover
  const kmToCoords = useCallback(
    (km: number) => {
      if (!data?.dists || !data?.lats) return null;
      const dists = data.dists;
      let idx = 0;
      for (let i = 1; i < dists.length; i++) {
        if (Math.abs(dists[i] - km) < Math.abs(dists[idx] - km)) idx = i;
      }
      const r = data.lats.length / dists.length;
      const mi = Math.min(Math.floor(idx * r), data.lats.length - 1);
      return {
        lat: data.lats[mi],
        lng: data.lons[mi],
        bearing: data.bearings?.[idx] || 0,
      };
    },
    [data]
  );

  useEffect(() => {
    if (hoverKm === null) return;
    const coords = kmToCoords(hoverKm);
    if (!coords) return;

    if (markerRef.current) {
      markerRef.current.setPosition(coords);
    }
    if (panoObjRef.current) {
      panoObjRef.current.setPosition(coords);
      panoObjRef.current.setPov({ heading: coords.bearing, pitch: -5 });
    }
  }, [hoverKm, kmToCoords]);

  if (!data?.lats) return null;

  return (
    <div className="relative h-full border-t border-line">
      <div ref={mapRef} className="h-full w-full bg-background" />
      <div className="absolute bottom-3 right-3 z-10 h-[185px] w-[300px] overflow-hidden rounded-xl border-2 border-accent bg-black shadow-2xl">
        <div ref={panoRef} className="h-full w-full" />
      </div>
    </div>
  );
}
