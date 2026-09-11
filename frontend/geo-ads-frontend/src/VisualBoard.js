import React, { useEffect, useState } from "react";
import "./App.css";

/** Base URL of the FastAPI backend */
const BACKEND_BASE_URL =
  process.env.REACT_APP_BACKEND_BASE_URL || "http://127.0.0.1:8000";
const WS_BASE_URL = BACKEND_BASE_URL.replace(/^http/, "ws");

/**
 * Local map: advertisement name -> image URL under backend/static.
 * Full URLs, so the images also load inside Electron.
 */
const AD_IMAGE_MAP = {
  "Apple iPhone 14 Promo": `${BACKEND_BASE_URL}/static/galaxy_s25_ultra.jpg`,
  "Samsung Galaxy S21": `${BACKEND_BASE_URL}/static/galaxy_s25_ultra.jpg`,
  "Sony TV Sale": `${BACKEND_BASE_URL}/static/sony_headphones.jpg`,
  "Coca Cola Banner": `${BACKEND_BASE_URL}/static/cocacola_lineup.jpg`,
  "Pepsi Banner": `${BACKEND_BASE_URL}/static/cocacola_lineup.jpg`,
  "Nike Air Max 2023": `${BACKEND_BASE_URL}/static/nike_airmax_red.jpg`,
};

/**
 * Pick the final image URL for an advertisement.
 */
function resolveAdImageUrl(ad) {
  if (!ad) return null;

  // 1) Source of truth: DB image_url
  if (ad.image_url) {
    if (ad.image_url.startsWith("http://") || ad.image_url.startsWith("https://")) {
      return ad.image_url;
    }
    return `${BACKEND_BASE_URL}${ad.image_url}`;
  }

  // 2) Fallback: the hardcoded map (only when image_url is missing)
  if (AD_IMAGE_MAP[ad.name]) {
    return AD_IMAGE_MAP[ad.name];
  }

  return null;
}

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Compute the CSS for each tile of the mosaic.
 */
function computeMosaicBackgroundStyle(config, screen) {
  if (!config || !screen) return {};

  const totalRows = config.maxRow - config.minRow + 1;
  const totalCols = config.maxCol - config.minCol + 1;

  const rowIndex = screen.row - config.minRow;
  const colIndex = screen.col - config.minCol;

  const rowPercent =
    totalRows === 1 ? 50 : (rowIndex / (totalRows - 1)) * 100;
  const colPercent =
    totalCols === 1 ? 50 : (colIndex / (totalCols - 1)) * 100;

  return {
    backgroundImage: `url(${config.imageUrl})`,
    backgroundSize: `${totalCols * 100}% ${totalRows * 100}%`,
    backgroundPosition: `${colPercent}% ${rowPercent}%`,
    backgroundRepeat: "no-repeat",
  };
}

function VisualBoard({ token: authToken, onLogout }) {

  // -----------------------------
  //  Layout / zones
  // -----------------------------
  const [zones, setZones] = useState([]);
  const [selectedZoneId, setSelectedZoneId] = useState(null);
  const [loadingLayout, setLoadingLayout] = useState(true);
  const [layoutError, setLayoutError] = useState(null);

  // -----------------------------
  //  Advertisements per zone
  // -----------------------------
  const [zoneAds, setZoneAds] = useState([]);
  const [adsLoading, setAdsLoading] = useState(false);
  const [adsError, setAdsError] = useState(null);

  // -----------------------------
  //  WebSocket status (ads)
  // -----------------------------
  const [wsStatus, setWsStatus] = useState("disconnected"); // eslint-disable-line no-unused-vars

  // -----------------------------
  //  Screen selection and placements
  // -----------------------------
  const [selectionMode, setSelectionMode] = useState("single"); // "single" | "multi"
  const [selectedScreen, setSelectedScreen] = useState(null); // single selection
  const [selectedScreens, setSelectedScreens] = useState([]); // multi / mosaic selection
  const [placements, setPlacements] = useState({}); // placements[screenId] = ad

  // -----------------------------
  //  Mosaic state
  // -----------------------------
  const [mosaicMode, setMosaicMode] = useState(false);
  const [mosaicSelectedAdId, setMosaicSelectedAdId] = useState(null);
  const [mosaicConfigs, setMosaicConfigs] = useState({}); // zoneId -> config

  // -----------------------------
  //  HTTP Recommendation state
  // -----------------------------
  const [recX, setRecX] = useState(1);
  const [recY, setRecY] = useState(1);
  const [recRadius, setRecRadius] = useState(10);
  const [recScreenType, setRecScreenType] = useState("");
  const [recAdCategory, setRecAdCategory] = useState("");
  const [recTimeWindow, setRecTimeWindow] = useState("");
  const [recAdId, setRecAdId] = useState(null);

  const [recLoading, setRecLoading] = useState(false);
  const [recError, setRecError] = useState(null);
  const [recommendationInfo, setRecommendationInfo] = useState(null);
  const [recommendedScreenId, setRecommendedScreenId] = useState(null);

  // -----------------------------
  //  WebSocket Recommendation
  // -----------------------------
  const [wsRecEnabled, setWsRecEnabled] = useState(false);
  const [wsRecStatus, setWsRecStatus] = useState("disconnected"); // eslint-disable-line no-unused-vars

  // -----------------------------
  //  Near query state (/layout/query/near)
  // -----------------------------
  const [nearX, setNearX] = useState(1);
  const [nearY, setNearY] = useState(1);
  const [nearRadius, setNearRadius] = useState(2);
  const [nearResults, setNearResults] = useState([]);
  const [nearLoading, setNearLoading] = useState(false);
  const [nearError, setNearError] = useState(null);

  // -----------------------------
  //  MultiIndex inspector state
  // -----------------------------
  const [miAdCategory, setMiAdCategory] = useState("");
  const [miTimeWindow, setMiTimeWindow] = useState("");
  const [multiIndexKeys, setMultiIndexKeys] = useState([]);
  const [miLoading, setMiLoading] = useState(false);
  const [miError, setMiError] = useState(null);

  // -----------------------------
  //  PostGIS near query state
  // -----------------------------
  const [gisLat, setGisLat] = useState(38.2466);
  const [gisLon, setGisLon] = useState(21.7346);
  const [gisRadiusM, setGisRadiusM] = useState(15);
  const [gisResults, setGisResults] = useState([]);
  const [gisLoading, setGisLoading] = useState(false);
  const [gisError, setGisError] = useState(null);

  // -----------------------------
  //  Distributed Index state
  // -----------------------------
  const [distX, setDistX] = useState(2);
  const [distY, setDistY] = useState(2);
  const [distRadius, setDistRadius] = useState(3);
  const [distResults, setDistResults] = useState([]);
  const [distLoading, setDistLoading] = useState(false);
  const [distError, setDistError] = useState(null);

  // Benchmark state
  const [benchRepeats, setBenchRepeats] = useState(20);
  const [benchResults, setBenchResults] = useState(null);
  const [benchLoading, setBenchLoading] = useState(false);
  const [benchError, setBenchError] = useState(null);

  // Right panel active tab
  const [activeTab, setActiveTab] = useState("rec");

  // Live clock
  const [clockTime, setClockTime] = useState(() => new Date().toLocaleTimeString("en-GB", { hour12: false })); // eslint-disable-line no-unused-vars
  useEffect(() => {
    const id = setInterval(() => {
      setClockTime(new Date().toLocaleTimeString("en-GB", { hour12: false }));
    }, 1000);
    return () => clearInterval(id);
  }, []);


  // =====================
  //  Load LAYOUT
  //  Waits for the token (authToken dependency) and sends the Bearer header
  // =====================
  useEffect(() => {
    if (!authToken) return; // wait for the token before loading

    async function fetchLayout() {
      try {
        setLoadingLayout(true);
        setLayoutError(null);

        const res = await fetch(`${BACKEND_BASE_URL}/layout`, {
          headers: authHeaders(authToken),
        });
        if (!res.ok) {
          throw new Error("HTTP " + res.status);
        }
        const data = await res.json();
        setZones(data);

        if (data.length > 0) {
          setSelectedZoneId(data[0].id);
        }
      } catch (err) {
        console.error("Error fetching layout:", err);
        setLayoutError("Could not load the layout from the backend.");
      } finally {
        setLoadingLayout(false);
      }
    }

    fetchLayout();
  }, [authToken]);

  // =====================
  //  Load ADS per ZONE
  // =====================
  useEffect(() => {
    if (!selectedZoneId) return;

    async function fetchZoneAds() {
      try {
        setAdsLoading(true);
        setAdsError(null);

        const res = await fetch(
          `${BACKEND_BASE_URL}/advertisements/zone/${selectedZoneId}`,
          {
            headers: authHeaders(authToken),
          }
        );

        if (!res.ok) {
          throw new Error("HTTP " + res.status);
        }
        const data = await res.json();
        setZoneAds(data);
      } catch (err) {
        console.error("Error fetching ads:", err);
        setAdsError("Could not load the advertisements for this zone.");
        setZoneAds([]);
      } finally {
        setAdsLoading(false);
      }
    }

    fetchZoneAds();
  }, [selectedZoneId, authToken]);

  // =====================
  //  WebSocket for /ws/ads (status)
  // =====================
  useEffect(() => {
    if (!authToken) return;
    const ws = new WebSocket(`${WS_BASE_URL}/ws/ads?token=${authToken}`);


    ws.onopen = () => {
      setWsStatus("connected");
    };

    ws.onclose = () => {
      setWsStatus("disconnected");
    };

    ws.onerror = () => {
      setWsStatus("error");
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log("WS /ads message:", msg);
      } catch (e) {
        console.log("WS /ads raw:", event.data);
      }
    };

    return () => {
      ws.close();
    };
  }, [authToken]);

  // =====================
  //  WebSocket Recommendation (/ws/recommendation-simple)
  // =====================
  useEffect(() => {
    if (!wsRecEnabled) {
      setWsRecStatus("disconnected");
      return;
    }

    if (!authToken) return;
    const ws = new WebSocket(`${WS_BASE_URL}/ws/recommendation-simple?token=${authToken}`);

    let timerId = null;

    ws.onopen = () => {
      setWsRecStatus("connected");

      // Send the parameters periodically
      timerId = setInterval(() => {
        const currentAdId =
          recAdId || (zoneAds.length > 0 ? zoneAds[0].id : null);

        if (!currentAdId) {
          setWsRecStatus("no-ad");
          return;
        }

        const payload = {
          ad_id: currentAdId,
          x: recX,
          y: recY,
          radius: recRadius,
          screen_type: recScreenType || null,
          ad_category: recAdCategory || null,
          time_window: recTimeWindow || null,
        };

        ws.send(JSON.stringify(payload));
      }, 3000);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.error) {
          setRecError(msg.error);
          return;
        }

        if (msg.type === "screen_recommendation" && msg.data) {
          const data = msg.data;
          setRecommendationInfo(data);
          setRecommendedScreenId(data.screen_id);
          setRecError(null);
        }
      } catch (err) {
        console.error("WS recommendation parse error:", err);
      }
    };

    ws.onerror = () => {
      setWsRecStatus("error");
    };

    ws.onclose = () => {
      setWsRecStatus("disconnected");
      if (timerId) clearInterval(timerId);
    };

    return () => {
      if (timerId) clearInterval(timerId);
      ws.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsRecEnabled, authToken, recX, recY, recRadius, recScreenType, recAdCategory, recTimeWindow, recAdId, zoneAds]);

  // =====================
  //  Selection helpers
  // =====================
  function isScreenSelected(screen) {
    if (!screen) return false;

    if (mosaicMode) {
      return selectedScreens.includes(screen.id);
    }

    if (selectionMode === "single") {
      return selectedScreen && selectedScreen.id === screen.id;
    }
    return selectedScreens.includes(screen.id);
  }

  // default ad when the operator has not chosen one
  function getAdForScreen(index, screen) {
    if (placements[screen.id]) {
      return placements[screen.id];
    }
    if (!zoneAds || zoneAds.length === 0) return null;
    const adIndex = index % zoneAds.length;
    return zoneAds[adIndex];
  }

  function handleScreenClick(screen) {
    if (!screen) return;

    if (mosaicMode) {
      setSelectedScreens((prev) => {
        if (prev.includes(screen.id)) {
          return prev.filter((id) => id !== screen.id);
        }
        return [...prev, screen.id];
      });
      return;
    }

    if (selectionMode === "single") {
      setSelectedScreen(screen);
      return;
    }

    setSelectedScreens((prev) => {
      if (prev.includes(screen.id)) {
        return prev.filter((id) => id !== screen.id);
      }
      return [...prev, screen.id];
    });
  }

  function handleAdChoice(ad) {
    if (!ad) return;

    if (selectionMode === "single") {
      if (!selectedScreen) return;

      setPlacements((prev) => ({
        ...prev,
        [selectedScreen.id]: ad,
      }));
      setSelectedScreen(null);
      return;
    }

    if (selectedScreens.length === 0) return;

    setPlacements((prev) => {
      const next = { ...prev };
      selectedScreens.forEach((id) => {
        next[id] = ad;
      });
      return next;
    });
    setSelectedScreens([]);
  }

  function handleClearAd() {
    if (selectionMode === "single") {
      if (!selectedScreen) return;
      setPlacements((prev) => {
        const copy = { ...prev };
        delete copy[selectedScreen.id];
        return copy;
      });
      setSelectedScreen(null);
      return;
    }

    if (selectedScreens.length === 0) return;

    setPlacements((prev) => {
      const copy = { ...prev };
      selectedScreens.forEach((id) => {
        delete copy[id];
      });
      return copy;
    });
    setSelectedScreens([]);
  }

  // =====================
  //  Mosaic handlers
  // =====================
  function handleApplyMosaic() {
    const currentZone = zones.find((z) => z.id === selectedZoneId);
    if (!currentZone) return;

    if (!mosaicMode) {
      alert("Enable Mosaic mode first.");
      return;
    }

    if (!mosaicSelectedAdId) {
      alert("Pick an advertisement for the mosaic first.");
      return;
    }

    if (selectedScreens.length === 0) {
      alert("Pick screens for the mosaic first.");
      return;
    }

    const screensInZone = currentZone.screens.filter((s) =>
      selectedScreens.includes(s.id)
    );
    if (screensInZone.length === 0) {
      alert("No screens found for the mosaic.");
      return;
    }

    const rows = screensInZone.map((s) => s.row);
    const cols = screensInZone.map((s) => s.col);
    const minRow = Math.min(...rows);
    const maxRow = Math.max(...rows);
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);

    const expectedCount = (maxRow - minRow + 1) * (maxCol - minCol + 1);
    if (expectedCount !== screensInZone.length) {
      alert(
        "For a mosaic the screens must form one solid rectangle, with no gaps."
      );
      return;
    }

    const ad = zoneAds.find((a) => a.id === mosaicSelectedAdId);
    if (!ad) {
      alert("Advertisement for the mosaic not found.");
      return;
    }

    const imageUrl = resolveAdImageUrl(ad);
    if (!imageUrl) {
      alert("This advertisement has no image available for a mosaic.");
      return;
    }

    const config = {
      adId: ad.id,
      adName: ad.name,
      imageUrl,
      minRow,
      maxRow,
      minCol,
      maxCol,
    };

    setMosaicConfigs((prev) => ({
      ...prev,
      [currentZone.id]: config,
    }));

    setPlacements((prev) => {
      const copy = { ...prev };
      screensInZone.forEach((s) => {
        copy[s.id] = ad;
      });
      return copy;
    });

    setSelectedScreens([]);
  }

  function handleClearMosaic() {
    if (!selectedZoneId) return;
    setMosaicConfigs((prev) => {
      const copy = { ...prev };
      delete copy[selectedZoneId];
      return copy;
    });
  }

  // =====================
  //  HTTP Recommendation handlers
  // =====================

  function clearRecommendation() {
    setRecommendationInfo(null);
    setRecommendedScreenId(null);
    setRecError(null);
  }

  async function handleRecommendGeneric() {
    if (!selectedZoneId) return;
    setRecLoading(true);
    setRecError(null);
    try {
      const params = new URLSearchParams();
      params.append("x", String(recX));
      params.append("y", String(recY));
      params.append("radius", String(recRadius));
      params.append("zone_id", selectedZoneId);
      if (recScreenType.trim()) params.append("screen_type", recScreenType);
      if (recAdCategory.trim()) params.append("ad_category", recAdCategory);
      if (recTimeWindow.trim()) params.append("time_window", recTimeWindow);

      const res = await fetch(
        `${BACKEND_BASE_URL}/layout/recommendation/screen?${params.toString()}`,
        {
          headers: authHeaders(authToken),
        }
      );

      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setRecommendationInfo(data);
      setRecommendedScreenId(data.screen_id);
    } catch (err) {
      console.error("Recommendation error (generic):", err);
      setRecError("Recommendation request failed.");
      clearRecommendation();
    } finally {
      setRecLoading(false);
    }
  }

  async function handleRecommendForAd() {
    if (!recAdId) {
      alert("Pick an advertisement for the recommendation first.");
      return;
    }
    setRecLoading(true);
    setRecError(null);
    try {
      const params = new URLSearchParams();
      params.append("x", String(recX));
      params.append("y", String(recY));
      params.append("radius", String(recRadius));
      if (recScreenType.trim()) params.append("screen_type", recScreenType);
      if (recAdCategory.trim()) params.append("ad_category", recAdCategory);
      if (recTimeWindow.trim()) params.append("time_window", recTimeWindow);

      const res = await fetch(
        `${BACKEND_BASE_URL}/recommendation/advertisements/${recAdId}/screen?${params.toString()}`,
        {
          headers: authHeaders(authToken),
        }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setRecommendationInfo(data);
      setRecommendedScreenId(data.screen_id);
    } catch (err) {
      console.error("Recommendation error (ad):", err);
      setRecError("Recommendation for this advertisement failed.");
      clearRecommendation();
    } finally {
      setRecLoading(false);
    }
  }

  // =====================
  //  Near query handlers (/layout/query/near)
  //  Sends the Bearer header
  // =====================
  async function handleNearQuery() {
    if (!selectedZoneId) return;
    setNearLoading(true);
    setNearError(null);
    try {
      const params = new URLSearchParams();
      params.append("x", String(nearX));
      params.append("y", String(nearY));
      params.append("radius", String(nearRadius));
      params.append("zone_id", selectedZoneId);

      const res = await fetch(
        `${BACKEND_BASE_URL}/layout/query/near?${params.toString()}`,
        { headers: authHeaders(authToken) }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setNearResults(data);
    } catch (err) {
      console.error("Near query error:", err);
      setNearError("Near query failed.");
      setNearResults([]);
    } finally {
      setNearLoading(false);
    }
  }

  // =====================
  //  MultiIndex inspector handlers
  //  Sends the Bearer header
  // =====================
  async function handleLoadMultiIndex() {
    setMiLoading(true);
    setMiError(null);
    try {
      const params = new URLSearchParams();
      if (miAdCategory.trim()) params.append("ad_category", miAdCategory);
      if (miTimeWindow.trim()) params.append("time_window", miTimeWindow);

      const res = await fetch(
        `${BACKEND_BASE_URL}/layout/multiindex?${params.toString()}`,
        { headers: authHeaders(authToken) }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setMultiIndexKeys(data);
    } catch (err) {
      console.error("MultiIndex error:", err);
      setMiError("Could not load the MultiIndex keys.");
      setMultiIndexKeys([]);
    } finally {
      setMiLoading(false);
    }
  }

  // =====================
  //  PostGIS near query handler
  // =====================
  async function handleGisQuery() {
    setGisLoading(true);
    setGisError(null);
    try {
      const params = new URLSearchParams();
      params.append("lat", String(gisLat));
      params.append("lon", String(gisLon));
      params.append("radius_m", String(gisRadiusM));

      const res = await fetch(
        `${BACKEND_BASE_URL}/layout/postgis/near?${params.toString()}`,
        { headers: authHeaders(authToken) }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setGisResults(data);
    } catch (err) {
      console.error("PostGIS query error:", err);
      setGisError("PostGIS query failed.");
      setGisResults([]);
    } finally {
      setGisLoading(false);
    }
  }

  // =====================
  //  Distributed near query handler
  // =====================
  async function handleDistQuery() {
    setDistLoading(true);
    setDistError(null);
    try {
      const params = new URLSearchParams();
      params.append("x", String(distX));
      params.append("y", String(distY));
      params.append("radius", String(distRadius));

      const res = await fetch(
        `${BACKEND_BASE_URL}/layout/distributed/near?${params.toString()}`,
        { headers: authHeaders(authToken) }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setDistResults(data);
    } catch (err) {
      console.error("Distributed query error:", err);
      setDistError("Distributed query failed.");
      setDistResults([]);
    } finally {
      setDistLoading(false);
    }
  }

  async function handleBenchmark() {
    setBenchLoading(true);
    setBenchError(null);
    setBenchResults(null);
    try {
      const params = new URLSearchParams({ repeats: String(benchRepeats) });
      const res = await fetch(
        `${BACKEND_BASE_URL}/benchmark/spatial?${params.toString()}`,
        { headers: authHeaders(authToken) }
      );
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setBenchResults(data);
    } catch (err) {
      console.error("Benchmark error:", err);
      setBenchError("Benchmark failed.");
    } finally {
      setBenchLoading(false);
    }
  }

  const selectedZone =
    zones.find((z) => z.id === selectedZoneId) || null;

  // Computed: highlighted IDs from PostGIS results (cyan outline)
  const gisHighlightedIds = new Set(gisResults.map((s) => s.id));

  // Computed: screen_id -> node_id from Distributed results (per-node color)
  const distNodeMap = new Map(distResults.map((r) => [r.screen.id, r.node]));

  const currentMosaicConfig = selectedZone
    ? mosaicConfigs[selectedZone.id] || null
    : null;

  const activeSelectionCount =
    selectionMode === "single"
      ? selectedScreen
        ? 1
        : 0
      : selectedScreens.length;

  const showAssignmentPanel = !mosaicMode && activeSelectionCount > 0;

  return (
    <div className="app-layout">

        {/* ── LEFT NAV ── */}
        <aside className="left-nav">
          <p className="left-nav-heading">Zones</p>

          {loadingLayout && <p className="text-xs text-muted">Loading...</p>}
          {layoutError  && <p className="error-text text-xs">{layoutError}</p>}

          {zones.map((zone) => {
            const dotCls =
              zone.id === "glassfloor"  ? "zone-dot-glassfloor"  :
              zone.id === "surrounding" ? "zone-dot-surrounding" :
              "zone-dot-megatron";
            return (
              <button
                key={zone.id}
                className={"zone-nav-btn" + (zone.id === selectedZoneId ? " zone-nav-btn-active" : "")}
                onClick={() => {
                  setSelectedZoneId(zone.id);
                  setSelectedScreen(null);
                  setSelectedScreens([]);
                  clearRecommendation();
                }}
              >
                <span className={`zone-dot ${dotCls}`} />
                {zone.name}
                <span className="zone-badge">{zone.screens?.length ?? 0}</span>
              </button>
            );
          })}

          {/* MultiIndex collapsible */}
          <details className="mi-details">
            <summary>MultiIndex Inspector</summary>
            <div className="mi-body">
              <input
                type="text"
                placeholder="ad_category"
                value={miAdCategory}
                onChange={(e) => setMiAdCategory(e.target.value)}
              />
              <input
                type="text"
                placeholder="time_window"
                value={miTimeWindow}
                onChange={(e) => setMiTimeWindow(e.target.value)}
              />
              <button
                className="btn btn-ghost"
                style={{ width: "100%" }}
                onClick={handleLoadMultiIndex}
                disabled={miLoading}
              >
                {miLoading ? "Loading..." : "Load Keys"}
              </button>
              {miError && <p className="error-text text-xs">{miError}</p>}
              {multiIndexKeys.length > 0 && (
                <div>
                  <p className="text-xs text-muted">{multiIndexKeys.length} keys total</p>
                  <table className="mi-keys-table">
                    <thead>
                      <tr><th>id</th><th>zone</th><th>x</th><th>y</th></tr>
                    </thead>
                    <tbody>
                      {multiIndexKeys.slice(0, 5).map((k) => (
                        <tr key={k.screen_id}>
                          <td>{k.screen_id}</td>
                          <td>{k.zone_id}</td>
                          <td>{k.x}</td>
                          <td>{k.y}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {multiIndexKeys.length > 5 && (
                    <p className="text-xs text-muted" style={{ marginTop: "4px" }}>
                      +{multiIndexKeys.length - 5} more
                    </p>
                  )}
                </div>
              )}
            </div>
          </details>
        </aside>

        {/* ── CENTER BOARD ── */}
        <main className="center-board">
          {selectedZone ? (
            <>
              {/* Zone header */}
              <div className="board-zone-header">
                <h2 className="board-zone-name">{selectedZone.name}</h2>
                <span className="board-zone-desc">
                  {selectedZone.description} · {selectedZone.rows}×{selectedZone.cols}
                </span>
              </div>

              {/* Compact toolbar */}
              <div className="board-toolbar">
                <span className="toolbar-label">Selection</span>
                <div className="seg-control">
                  <button
                    className={"seg-btn" + (selectionMode === "single" ? " seg-btn-active" : "")}
                    onClick={() => { setSelectionMode("single"); setSelectedScreens([]); }}
                  >Single</button>
                  <button
                    className={"seg-btn" + (selectionMode === "multi" ? " seg-btn-active" : "")}
                    onClick={() => { setSelectionMode("multi"); setSelectedScreen(null); }}
                  >Multi</button>
                </div>
                <div className="toolbar-divider" />
                <span className="toolbar-label">Mode</span>
                <div className="seg-control">
                  <button
                    className={"seg-btn" + (!mosaicMode ? " seg-btn-active" : "")}
                    onClick={() => { setMosaicMode(false); setSelectedScreens([]); }}
                  >Normal</button>
                  <button
                    className={"seg-btn" + (mosaicMode ? " seg-btn-active" : "")}
                    onClick={() => { setMosaicMode(true); setSelectionMode("multi"); setSelectedScreen(null); }}
                  >Mosaic</button>
                </div>
                {mosaicMode && (
                  <>
                    <div className="toolbar-divider" />
                    {zoneAds.map((ad) => (
                      <button
                        key={ad.id}
                        className={"ad-picker-btn" + (mosaicSelectedAdId === ad.id ? " ad-picker-btn-active" : "")}
                        onClick={() => setMosaicSelectedAdId(ad.id)}
                      >{ad.name}</button>
                    ))}
                    <button
                      className="mosaic-apply-btn"
                      onClick={handleApplyMosaic}
                      disabled={!mosaicMode || !mosaicSelectedAdId || selectedScreens.length === 0}
                    >Apply</button>
                    <button
                      className="mosaic-clear-btn"
                      onClick={handleClearMosaic}
                      disabled={!currentMosaicConfig}
                    >Clear</button>
                  </>
                )}
              </div>

              {adsLoading && <p className="text-xs text-muted">Loading ads...</p>}
              {adsError   && <p className="error-text text-xs">{adsError}</p>}

              {/* Screen grid */}
              <div
                className="stadium-layout-grid"
                style={{ gridTemplateColumns: `repeat(${selectedZone.cols}, 1fr)` }}
              >
                {selectedZone.screens.map((screen, index) => {
                  const ad       = getAdForScreen(index, screen);
                  const selected = isScreenSelected(screen);
                  const imgSrc   = resolveAdImageUrl(ad);
                  const isInMosaic =
                    !!currentMosaicConfig &&
                    screen.row >= currentMosaicConfig.minRow &&
                    screen.row <= currentMosaicConfig.maxRow &&
                    screen.col >= currentMosaicConfig.minCol &&
                    screen.col <= currentMosaicConfig.maxCol;
                  const isRecommended = recommendedScreenId === screen.id;

                  return (
                    <div
                      key={screen.id}
                      className={
                        "screen-tile zone-" + selectedZone.id +
                        (ad            ? " screen-tile-has-ad"     : "") +
                        (selected      ? " screen-tile-selected"   : "") +
                        (isInMosaic    ? " screen-tile-mosaic"     : "") +
                        (isRecommended ? " screen-tile-recommended": "") +
                        (gisHighlightedIds.has(screen.id) ? " screen-tile-gis" : "") +
                        (distNodeMap.has(screen.id) ? ` screen-tile-dist-${distNodeMap.get(screen.id)}` : "")
                      }
                      onClick={() => handleScreenClick(screen)}
                    >
                      {ad ? (
                        <>
                          {isInMosaic ? (
                            <div
                              className="mosaic-img-wrapper"
                              style={computeMosaicBackgroundStyle(currentMosaicConfig, screen)}
                            />
                          ) : (
                            imgSrc && <img src={imgSrc} alt={ad.name} className="screen-img" />
                          )}
                          <div className="screen-meta">
                            <div className="screen-ad-name">{ad.name}</div>
                            <div className="screen-pos">({screen.row},{screen.col})</div>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="screen-id">{screen.id}</div>
                          <div className="screen-pos">({screen.row},{screen.col})</div>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Ad assignment panel */}
              {showAssignmentPanel && (
                <div className="ad-picker-panel">
                  <p className="ad-picker-title">
                    Assign ad to{" "}
                    {selectionMode === "single"
                      ? `screen ${selectedScreen?.id}`
                      : `${activeSelectionCount} screens`}
                  </p>
                  {zoneAds.length === 0 ? (
                    <p className="text-xs text-muted">No ads available for this zone.</p>
                  ) : (
                    <div className="ad-picker-grid">
                      {zoneAds.map((ad) => {
                        const imgSrc = resolveAdImageUrl(ad);
                        return (
                          <button
                            key={ad.id}
                            className="ad-picker-item"
                            onClick={() => handleAdChoice(ad)}
                          >
                            {imgSrc && <img src={imgSrc} alt={ad.name} className="ad-picker-thumb" />}
                            <span className="ad-picker-name">{ad.name}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                  <div className="ad-picker-actions">
                    <button onClick={handleClearAd} className="ad-picker-clear">
                      No Ad{selectionMode === "multi" && activeSelectionCount > 1 ? " (all selected)" : ""}
                    </button>
                    <button
                      onClick={() => { setSelectedScreen(null); setSelectedScreens([]); }}
                      className="ad-picker-cancel"
                    >Cancel</button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="board-empty">
              <div className="board-empty-icon">▦</div>
              <p className="board-empty-text">Select a zone from the left panel</p>
            </div>
          )}
        </main>

        {/* ── RIGHT PANELS ── */}
        <aside className="right-panels">

          {/* Tab bar */}
          <div className="tabs-bar">
            {[
              { id: "rec",     label: "Rec Engine" },
              { id: "near",    label: "R-Tree"     },
              { id: "postgis", label: "PostGIS"    },
              { id: "dist",    label: "Distributed"},
              { id: "bench",   label: "Benchmark"  },
            ].map(({ id, label }) => (
              <button
                key={id}
                className={"tab-btn" + (activeTab === id ? " tab-btn-active" : "")}
                onClick={() => setActiveTab(id)}
              >{label}</button>
            ))}
          </div>

          <div className="tab-content">

            {/* ── TAB: Recommendation ── */}
            {activeTab === "rec" && (
              <div className="panel-card">
                <div className="panel-card-header">Recommendation Engine</div>
                <p className="text-xs text-muted" style={{ marginBottom: "8px" }}>
                  Grid coordinates (x=col, y=row). Try (1.5, 1.5).
                </p>
                <div className="param-grid param-grid-3">
                  <label className="param-label">X (col)
                    <input type="number" value={recX} onChange={(e) => setRecX(parseFloat(e.target.value) || 0)} />
                  </label>
                  <label className="param-label">Y (row)
                    <input type="number" value={recY} onChange={(e) => setRecY(parseFloat(e.target.value) || 0)} />
                  </label>
                  <label className="param-label">Radius
                    <input type="number" value={recRadius} onChange={(e) => setRecRadius(parseFloat(e.target.value) || 0)} />
                  </label>
                  <label className="param-label">Screen type
                    <input type="text" value={recScreenType} onChange={(e) => setRecScreenType(e.target.value)} placeholder="glassfloor_tile" />
                  </label>
                  <label className="param-label">Ad category
                    <input type="text" value={recAdCategory} onChange={(e) => setRecAdCategory(e.target.value)} placeholder="tech" />
                  </label>
                  <label className="param-label">Time window
                    <input type="text" value={recTimeWindow} onChange={(e) => setRecTimeWindow(e.target.value)} placeholder="prime_time" />
                  </label>
                </div>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "8px" }}>
                  <button className="btn btn-primary" onClick={handleRecommendGeneric} disabled={recLoading}>
                    {recLoading ? "..." : "Find Screen"}
                  </button>
                  <select
                    value={recAdId || ""}
                    onChange={(e) => setRecAdId(e.target.value ? Number(e.target.value) : null)}
                    style={{ flex: 1 }}
                  >
                    <option value="">-- select ad --</option>
                    {zoneAds.map((ad) => <option key={ad.id} value={ad.id}>{ad.name}</option>)}
                  </select>
                  <button className="btn btn-blue" onClick={handleRecommendForAd} disabled={recLoading || !recAdId}>
                    For Ad
                  </button>
                </div>
                <label className="ws-toggle-chip" style={{ marginBottom: "8px" }}>
                  <input
                    type="checkbox"
                    checked={wsRecEnabled}
                    onChange={(e) => setWsRecEnabled(e.target.checked)}
                  />
                  Live WebSocket recommendations
                </label>
                {recLoading && <p className="text-xs text-muted">Computing...</p>}
                {recError   && <p className="error-text">{recError}</p>}
                {recommendationInfo && (
                  <>
                    <div className="result-box">
                      <div>Screen <span className="result-highlight">{recommendationInfo.screen_id}</span></div>
                      <div className="text-xs text-muted">
                        zone: {recommendationInfo.zone_id} · x:{recommendationInfo.x} y:{recommendationInfo.y}
                      </div>
                      <div className="text-xs" style={{ marginTop: "4px" }}>
                        Distance: <span className="result-highlight">{recommendationInfo.distance?.toFixed(2)}</span>
                      </div>
                    </div>
                    <button
                      className="btn btn-ghost"
                      style={{ width: "100%", marginTop: "6px" }}
                      onClick={clearRecommendation}
                    >Clear result</button>
                  </>
                )}
              </div>
            )}

            {/* ── TAB: Near (R-Tree) ── */}
            {activeTab === "near" && (
              <div className="panel-card">
                <div className="panel-card-header">Near Query — R-Tree</div>
                <div className="param-grid param-grid-3">
                  <label className="param-label">X
                    <input type="number" value={nearX} onChange={(e) => setNearX(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Y
                    <input type="number" value={nearY} onChange={(e) => setNearY(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Radius
                    <input type="number" value={nearRadius} onChange={(e) => setNearRadius(parseFloat(e.target.value))} />
                  </label>
                </div>
                <button className="btn btn-primary" onClick={handleNearQuery} disabled={nearLoading}>
                  {nearLoading ? "..." : "Query"}
                </button>
                {nearError && <p className="error-text" style={{ marginTop: "6px" }}>{nearError}</p>}
                {nearResults.length > 0 && (
                  <div className="result-box" style={{ marginTop: "8px" }}>
                    <span className="result-highlight">{nearResults.length}</span> screens found within radius
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: PostGIS ── */}
            {activeTab === "postgis" && (
              <div className="panel-card">
                <div className="panel-card-header">PostGIS — ST_DWithin</div>
                <p className="text-xs text-muted" style={{ marginBottom: "8px" }}>
                  WGS-84 coordinates. Venue center: 38.2466, 21.7346.
                </p>
                <div className="param-grid param-grid-3">
                  <label className="param-label">Lat
                    <input type="number" step="0.0001" value={gisLat} onChange={(e) => setGisLat(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Lon
                    <input type="number" step="0.0001" value={gisLon} onChange={(e) => setGisLon(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Radius (m)
                    <input type="number" value={gisRadiusM} onChange={(e) => setGisRadiusM(parseFloat(e.target.value))} />
                  </label>
                </div>
                <button className="btn btn-cyan" onClick={handleGisQuery} disabled={gisLoading}>
                  {gisLoading ? "..." : "ST_DWithin"}
                </button>
                {gisError && <p className="error-text" style={{ marginTop: "6px" }}>{gisError}</p>}
                {gisResults.length > 0 && (
                  <div style={{ marginTop: "8px" }}>
                    <div className="result-box">
                      <span className="result-highlight">{gisResults.length}</span> screens (cyan outline on grid)
                    </div>
                    <table className="mi-keys-table" style={{ marginTop: "8px" }}>
                      <thead><tr><th>id</th><th>zone</th><th>row</th><th>col</th></tr></thead>
                      <tbody>
                        {gisResults.map((s) => (
                          <tr key={s.id}>
                            <td>{s.id}</td><td>{s.zone_id}</td><td>{s.row}</td><td>{s.col}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Distributed ── */}
            {activeTab === "dist" && (
              <div className="panel-card">
                <div className="panel-card-header">Distributed Index — Fan-out</div>
                <p className="text-xs text-muted" style={{ marginBottom: "8px" }}>
                  MapReduce: 3 shards (GlassFloor / Surrounding / Megatron) in parallel threads.
                </p>
                <div className="param-grid param-grid-3">
                  <label className="param-label">X
                    <input type="number" value={distX} onChange={(e) => setDistX(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Y
                    <input type="number" value={distY} onChange={(e) => setDistY(parseFloat(e.target.value))} />
                  </label>
                  <label className="param-label">Radius
                    <input type="number" value={distRadius} onChange={(e) => setDistRadius(parseFloat(e.target.value))} />
                  </label>
                </div>
                <button className="btn btn-purple" onClick={handleDistQuery} disabled={distLoading}>
                  {distLoading ? "..." : "Fan-out Query"}
                </button>
                {distError && <p className="error-text" style={{ marginTop: "6px" }}>{distError}</p>}
                {distResults.length > 0 && (
                  <div style={{ marginTop: "8px" }}>
                    <div className="result-box">
                      <span className="result-highlight">{distResults.length}</span> screens across{" "}
                      <span className="result-highlight">{new Set(distResults.map((r) => r.node)).size}</span> nodes
                    </div>
                    <div className="dist-chip-list">
                      {distResults.map((r) => {
                        const ns = r.node === "node_glassfloor" ? "gf"
                          : r.node === "node_surrounding" ? "sur" : "meg";
                        return (
                          <span key={r.screen.id} className="dist-chip">
                            {r.screen.id} <span className={`node-badge ${ns}`}>{ns}</span>
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Benchmark ── */}
            {activeTab === "bench" && (
              <div className="panel-card">
                <div className="panel-card-header">Spatial Algorithm Benchmark</div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                  <label className="param-label" style={{ flexDirection: "row", alignItems: "center", gap: "6px", margin: 0, whiteSpace: "nowrap" }}>
                    Repeats
                    <input
                      type="number"
                      min={1}
                      max={100}
                      value={benchRepeats}
                      onChange={(e) => setBenchRepeats(Number(e.target.value))}
                      style={{ width: "60px" }}
                    />
                  </label>
                  <button className="btn btn-orange" onClick={handleBenchmark} disabled={benchLoading}>
                    {benchLoading ? "Running..." : "Run Benchmark"}
                  </button>
                </div>
                {benchError && <p className="error-text">{benchError}</p>}
                {benchResults && (() => {
                  const r    = benchResults.results;
                  const vals = [r.rtree_ms, r.kdtree_ms, r.grid_ms, r.distributed_ms, r.postgis_ms ?? 0].filter(Boolean);
                  const maxMs = Math.max(...vals) || 1;
                  const rows = [
                    { label: "R-Tree",      ms: r.rtree_ms,       count: benchResults.counts.rtree,       cls: "bar-rtree"   },
                    { label: "KD-Tree",     ms: r.kdtree_ms,      count: benchResults.counts.kdtree,      cls: "bar-kdtree"  },
                    { label: "Grid Index",  ms: r.grid_ms,        count: benchResults.counts.grid,        cls: "bar-grid"    },
                    { label: "Distributed", ms: r.distributed_ms, count: benchResults.counts.distributed, cls: "bar-dist"    },
                    { label: "PostGIS",     ms: r.postgis_ms,     count: benchResults.counts.postgis,     cls: "bar-postgis" },
                  ];
                  return (
                    <div className="bench-results">
                      <p className="bench-subtitle">avg ms/query · {benchResults.params.repeats} repeats</p>
                      {rows.map(({ label, ms, count, cls }) => (
                        <div key={label} className="bench-row">
                          <span className="bench-label">{label}</span>
                          <div className="bench-bar-wrap">
                            <div className={`bench-bar ${cls}`} style={{ width: ms != null ? `${(ms / maxMs) * 100}%` : "0%" }} />
                          </div>
                          <span className="bench-ms">
                            {ms != null ? `${ms.toFixed(3)} ms` : "—"}
                            {count > 0 && <span className="bench-count"> ({count})</span>}
                          </span>
                        </div>
                      ))}
                      {benchResults.postgis_error && (
                        <p className="error-text text-xs" style={{ marginTop: "6px" }}>
                          PostGIS: {benchResults.postgis_error}
                        </p>
                      )}
                    </div>
                  );
                })()}
              </div>
            )}

          </div>
        </aside>

    </div>
  );
}

export default VisualBoard;