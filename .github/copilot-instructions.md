# Copilot Instructions: bond-heatmap

## Project Overview
**bond-heatmap** is a Streamlit-based interactive dashboard for analyzing investment-grade (IG) credit spreads using treemap visualization. It displays bond portfolio data with configurable color (price/yield signals) and size (notional/duration/DV01) modes, enabling traders to identify relative value across sectors and credit quality.

**Tech Stack:** Python 3 · Streamlit · Plotly · Pandas · NumPy

---

## Architecture & Key Components

### Single-File Application Structure
All logic resides in `ig_spread_treemap.py` (533 lines). This is intentional—it's a dashboard, not a multi-module service. Modifications should preserve this structure unless adding significant new features.

### Data Model
1. **Data Source:** Mock hardcoded bond dataset in `load_data()` (lines ~125-150). Real integration would replace this.
2. **Key Columns:**
   - Financial: `oas` (spread), `coupon`, `maturity`, `rating`
   - Portfolio: `notional` (position size in $mm), `sdur` (spread duration in years)
   - Calculated: `dv01` (dollar value of 1bp movement), `pct52w` (where current OAS sits in 52W range as 0-100%)
   - Signal Logic: `signal` (Rich/Fair/Cheap/Wide) derived from `pct52w` thresholds (lines ~147-149)

### UI/Visualization Patterns

**Color Encoding (3 modes):**
- **52W Percentile:** Green (rich, low %) → Red (cheap, high %) using `pct_to_color()` function
- **Spread Delta:** Green (tightening) → Gray (unchanged) → Red (widening)
- **OAS Level:** Green (tight spreads) → Red (wide spreads)

**Size Encoding (3 modes):**
- Notional ($mm) | Spread Duration (years) | DV01 ($k)

**Styling:** Dark theme (IBM Plex Mono font, #0a0c0f background) with custom CSS injected via `st.markdown()`. All color values use RGB strings, not hex (e.g., `rgb(0,196,140)`).

### Treemap Hierarchy
Portfolio → Sector → Individual Bond. Built dynamically in lines 350–380 using Plotly's `go.Treemap()` with custom hover templates and breadcrumb navigation.

---

## Developer Workflows

### Running the Dashboard
```bash
streamlit run ig_spread_treemap.py
```
Launches on http://localhost:8501. Streamlit auto-reloads on file changes.

### Adding New Bonds
Modify the `bonds` list in `load_data()` (lines 125–150). Fields are self-documenting dicts. No database—purely in-memory.

### Adding New Metrics
1. Add calculated column in `load_data()` after DataFrame creation (lines 168–171 show examples: `pct52w`, `dv01`)
2. Update sidebar selectbox or summary metrics section as needed
3. Add to hover template if display-relevant

### Adding New Filters or Modes
Follow the existing pattern:
- Add `st.selectbox()` or `st.radio()` to sidebar (lines 190–210)
- Use filter condition on `fdf` (lines 231–235)
- Add logic block for new color/size mapping (lines 277–310 or equivalent)
- Update legend documentation in sidebar

---

## Code Conventions & Patterns

### Streamlit-Specific
- **Caching:** Use `@st.cache_data` on `load_data()` to avoid recomputation on reruns
- **Reactive State:** Sidebar controls drive filtering and visualization regeneration automatically
- **HTML Injection:** Heavy use of `st.markdown(..., unsafe_allow_html=True)` for styling. Verify HTML is safe before adding.

### Data Pipeline
1. Load raw data via `load_data()`
2. Filter via sidebar selections → `fdf`
3. Calculate derived columns (percentiles, signals, colors)
4. Build treemap hierarchy
5. Render via Plotly

### Color Logic
Three helper functions convert values to RGB strings:
- `pct_to_color(p)`: Percentile (0-100) → RGB (green/red)
- `chg_to_color(c)`: Spread change in bps → RGB (green/gray/red)
- `oas_to_color(oas, lo=30, hi=200)`: Absolute OAS → RGB with lo/hi bounds

All use RGB tuples for Plotly compatibility. Update bounds (e.g., `hi=200`) if OAS range changes.

### Formatting Utilities
Formatting functions (lines 480–495) return HTML strings for tables:
- `signal_badge(sig)` → HTML badge with CSS class
- `fmt_chg(c)` → colored bps change
- `fmt_pct(p)` → colored percentile
- `fmt_oas(oas, pct)` → colored OAS

---

## Integration Points & Dependencies

### External Data
Currently hardcoded mock data. To integrate real data:
1. Replace `bonds` list in `load_data()` with API call or database query
2. Ensure DataFrame has same columns (issuer, ticker, isin, rating, sector, maturity, coupon, oas, lo52, hi52, chg, notional, sdur)
3. Calculate `pct52w`, `dv01`, `signal` in same function

### Plotly Configuration
Treemap uses:
- `colorscale` for gradient (currently 5-point scale, lines ~300–320)
- `zmid` for midpoint in color scale (handles asymmetric data)
- `tiling=dict(squarifyratio=1.618)` for layout optimization

Adjust `colorbar` positioning (lines 406–414) if layout changes.

---

## Testing & Validation

No automated tests exist. Manual validation:
1. **UI Responsive:** Filters change treemap instantly
2. **Hover Info:** All 10 columns display correctly in tooltips
3. **Calculations:** Spot-check `pct52w` (should be 0-100), `dv01` matches spread duration
4. **Color Consistency:** Rich signals appear green, cheap appear red

---

## Common Tasks & Patterns

| Task | Location | Pattern |
|------|----------|---------|
| Add bond to dataset | `load_data()` dict in `bonds` list | Copy existing row, update fields |
| Change color mapping | `pct_to_color()`, `chg_to_color()`, `oas_to_color()` | Adjust RGB tuple logic |
| Update signal thresholds | Line 148-149 lambda in `df["signal"] = ...` | Change percentile boundaries |
| Add sidebar filter | Lines 190–210 | Use `st.selectbox()` or `st.radio()`, filter `fdf` on line 231+ |
| Modify treemap hierarchy | Lines 350–380 build hierarchy | Add new parent level or reorganize |
| Adjust dark theme colors | CSS block (lines 25–115) | Update hex values (note: CSS uses hex, Python uses RGB) |

---

## Known Limitations & Future Work

- **No Data Persistence:** Bonds are hardcoded; no database backend
- **No User Authentication:** Designed for internal use
- **No Real-Time Feeds:** Requires manual data updates
- **Single Sector Multi-Tier:** Could support regional or sub-sector grouping (extend hierarchy in treemap)
