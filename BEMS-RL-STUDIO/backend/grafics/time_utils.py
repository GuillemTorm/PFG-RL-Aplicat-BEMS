"""Filtrat temporal i ajuda d'eix per a figures del panell."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.grafics.style import _alpha_color


def _bounded_int_series(
    df: pd.DataFrame,
    column: str,
    lower: int,
    upper: int,
) -> pd.Series:
    """Retorna una sèrie entera anul·lable amb valors temporals impossibles eliminats."""

    values = pd.to_numeric(df[column], errors="coerce").round()
    values = values.where(values.between(lower, upper))
    return values.astype("Int64")


def _coerce_temporal_parts(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Retorna les columnes mes/dia/hora netejades per a la reconstrucció de data i hora."""

    month = _bounded_int_series(df, "month", 1, 12)
    day = _bounded_int_series(df, "day_of_month", 1, 31)
    hour = _bounded_int_series(df, "hour", 0, 23)
    return month, day, hour


def sanitize_observation_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Converteix les columnes d'observació temporal i emmascarar valors físicament impossibles."""

    result = df.copy()
    bounds = {
        "month": (1, 12),
        "day_of_month": (1, 31),
        "hour": (0, 23),
    }
    for column, (lower, upper) in bounds.items():
        if column in result.columns:
            result[column] = _bounded_int_series(result, column, lower, upper)
    return result


def _infer_timestep_hours(df: pd.DataFrame) -> float:
    """Infereix la durada del timestep en hores a partir del temps disponible."""
    if "time_elapsed(hours)" in df.columns:
        elapsed = pd.to_numeric(df["time_elapsed(hours)"], errors="coerce")
        elapsed_diffs = elapsed.diff().dropna()
        elapsed_diffs = elapsed_diffs[(elapsed_diffs > 0) & np.isfinite(elapsed_diffs)]
        if not elapsed_diffs.empty:
            return float(elapsed_diffs.median())

    time_col = None
    if "timestamp" in df.columns:
        time_col = pd.to_datetime(df["timestamp"], errors="coerce")
    elif "datetime" in df.columns:
        time_col = pd.to_datetime(df["datetime"], errors="coerce")

    if time_col is not None:
        time_diffs = time_col.diff().dropna().dt.total_seconds() / 3600.0
        time_diffs = time_diffs[(time_diffs > 0) & np.isfinite(time_diffs)]
        if not time_diffs.empty:
            return float(time_diffs.median())

    if isinstance(df.index, pd.DatetimeIndex) and len(df.index) > 1:
        diffs = pd.Series(df.index, index=df.index).diff().dropna()
        diffs_h = diffs.dt.total_seconds() / 3600.0
        diffs_h = diffs_h[(diffs_h > 0) & np.isfinite(diffs_h)]
        if not diffs_h.empty:
            return float(diffs_h.median())

    if all(col in df.columns for col in ("month", "day_of_month", "hour")):
        mdh = df[["month", "day_of_month", "hour"]].apply(pd.to_numeric, errors="coerce")
        valid = mdh.dropna()
        if not valid.empty:
            hour_blocks = valid.ne(valid.shift()).any(axis=1).cumsum()
            block_sizes = hour_blocks.value_counts().sort_index()
            block_sizes = block_sizes[block_sizes > 0]
            if not block_sizes.empty:
                return 1.0 / float(block_sizes.median())

    return 0.25


def _seasonal_marker_colors(
    x_vals: list[int],
    season: str,
    *,
    active_color: str,
    muted_color: str | None = None,
) -> list[str]:
    """Seasonal marker colors."""
    months_sel = _season_months(season)
    if not months_sel:
        return [active_color] * len(x_vals)
    dim = muted_color if muted_color is not None else _alpha_color(active_color, 0.30)
    return [active_color if month in months_sel else dim for month in x_vals]

def _season_months(name: str):
    """Season months."""
    seasons = {
        "Winter": [12, 1, 2],
        "Spring": [3, 4, 5],
        "Summer": [6, 7, 8],
        "Autumn": [9, 10, 11],
    }
    return seasons.get(name, None)  # None -> Tot


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garanteix un DatetimeIndex per reagrupar per hores/dies/mesos.
    Si no hi ha 'datetime' ni 'timestamp', reconstrueix un índex sintètic
    coherent amb els timesteps de 15 minuts del projecte.
    """
    dfc = df.copy()
    if isinstance(dfc.index, pd.DatetimeIndex):
        dfc = dfc[~dfc.index.isna()]
        return dfc.sort_index(kind="mergesort")
    if "datetime" in dfc.columns:
        dfc["datetime"] = pd.to_datetime(dfc["datetime"], errors="coerce")
        dfc = dfc.set_index("datetime").sort_index()
        dfc = dfc[~dfc.index.isna()]
        return dfc
    if "timestamp" in dfc.columns:
        dfc["datetime"] = pd.to_datetime(dfc["timestamp"], errors="coerce")
        dfc = dfc.set_index("datetime").sort_index()
        dfc = dfc[~dfc.index.isna()]
        return dfc

    if all(col in dfc.columns for col in ("month", "day_of_month", "hour")):
        month, day, hour = _coerce_temporal_parts(dfc)

        # Ancorem la sèrie en el primer registre complet: així respectem simulacions que no
        # comencen exactament a les 00:00.
        if "time_elapsed(hours)" in dfc.columns:
            elapsed = pd.to_numeric(dfc["time_elapsed(hours)"], errors="coerce")
            valid = elapsed.notna() & month.notna() & day.notna() & hour.notna()
            if valid.any():
                first_idx = valid[valid].index[0]
                first_pos = dfc.index.get_loc(first_idx)
                first_elapsed = float(elapsed.iloc[first_pos])
                base_minutes = int(round((first_elapsed % 1.0) * 60.0)) % 60
                base_ts = pd.Timestamp(
                    year=2001,
                    month=int(month.iloc[first_pos]),
                    day=int(day.iloc[first_pos]),
                    hour=int(hour.iloc[first_pos]),
                    minute=base_minutes,
                )
                offset_minutes = ((elapsed - first_elapsed) * 60.0).round()
                try:
                    dt = base_ts + pd.to_timedelta(offset_minutes, unit="m")
                    dfc.index = pd.DatetimeIndex(dt)
                    dfc = dfc[~dfc.index.isna()]
                    return dfc.sort_index(kind="mergesort")
                except (OverflowError, ValueError):
                    pass

        hour_blocks = (
            pd.DataFrame({"month": month, "day": day, "hour": hour})
            .ne(pd.DataFrame({"month": month, "day": day, "hour": hour}).shift())
            .any(axis=1)
            .cumsum()
        )
        # Quan no hi ha temps acumulat, repartim cada bloc d'una mateixa hora en quarts
        # d'hora consecutius, que és el pas habitual dels CSV de Sinergym.
        minute_slot = hour_blocks.groupby(hour_blocks).cumcount() * 15
        dt = pd.to_datetime(
            {
                "year": 2001,
                "month": month.astype("float64"),
                "day": day.astype("float64"),
                "hour": hour.astype("float64"),
                "minute": minute_slot.astype("float64"),
            },
            errors="coerce",
        )
        dfc.index = pd.DatetimeIndex(dt)
        dfc = dfc[~dfc.index.isna()]
        return dfc.sort_index(kind="mergesort")

    # Reserva defensiva: mantenim 15 minuts per pas.
    dfc.index = pd.date_range("2001-01-01", periods=len(dfc), freq="15min")
    return dfc.sort_index(kind="mergesort")

def _month_series(df: pd.DataFrame) -> pd.Series:
    """
    Sèrie 'mes' canònica 1..12:
      - Prioritza columna 'month' si existeix (normalitza possibles 0/13).
      - Si no, usa el DatetimeIndex.
    """
    if "month" in df.columns:
        s = _bounded_int_series(df, "month", 1, 12)
        if s.notna().any():
            return pd.Series(s, index=df.index)
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.Series(df.index.month, index=df.index)
    # amb índex sintètic ja és DateTimeIndex
    return pd.Series(pd.to_datetime(df.index).month, index=df.index)


def _hour_series(df: pd.DataFrame) -> pd.Series:
    """
    Sèrie 'hora' canònica 0..23:
      - Prioritza columna 'hour' si existeix (normalitza 24→0).
      - Si no, usa el DatetimeIndex.
    """
    if "hour" in df.columns:
        h = _bounded_int_series(df, "hour", 0, 23)
        if h.notna().any():
            return pd.Series(h, index=df.index)
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.Series(df.index.hour, index=df.index)
    return pd.Series(pd.to_datetime(df.index).hour, index=df.index)


def filter_by_season(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Filtra per estació amb la sèrie de mesos canònica."""
    months = _season_months(season)
    if not months:
        return df
    mon = _month_series(df)
    return df[mon.isin(months)]


def _get_outdoor_temperature_series(df: pd.DataFrame) -> pd.Series | None:
    """Retorna la columna de temperatura exterior utilitzada per les observacions generades."""
    for col in ("outdoor_temperature", "outdoor_air_temperature"):
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
    return None


def _has_mdh(df: pd.DataFrame) -> bool:
    """Té columnes month/day_of_month/hour del CSV?"""
    return all(c in df.columns for c in ("month", "day_of_month", "hour"))


def _canon_day_series(df: pd.DataFrame, col: str):
    """
    Retorna (x, y, hover) per a una sèrie agregada DIÀRIA sense anys:
      - Si hi ha columnes 'month' i 'day_of_month', fa mean per (MM,DD).
      - Si només hi ha DatetimeIndex, resample('D') i mitjana per (MM,DD) (uneix anys).
    Sempre torna UNA observació per MM-DD i X=1..365.
    """
    if _has_mdh(df):
        month, day, _ = _coerce_temporal_parts(df)
        working = df.assign(month=month, day_of_month=day)
        g = working.groupby(["month", "day_of_month"])[col].mean().reset_index()
        g = g.dropna(subset=["month", "day_of_month"])
        g["order"] = pd.to_datetime(
            {"year": 2001, "month": g["month"].astype(int), "day": g["day_of_month"].astype(int)},
            errors="coerce",
        )
        g = g.sort_values("order")
        x = g["order"].dt.dayofyear.tolist()
        y = g[col].to_list()
        hover = [f"{int(m):02d}-{int(d):02d}" for m, d in zip(g["month"], g["day_of_month"])]
        return x, y, hover

    if isinstance(df.index, pd.DatetimeIndex):
        s = df[col].resample("D").mean()
        g = s.groupby([s.index.month, s.index.day]).mean()
        months = np.array([i[0] for i in g.index], dtype=int)
        days = np.array([i[1] for i in g.index], dtype=int)
        order = pd.to_datetime({"year": 2001, "month": months, "day": days}, errors="coerce")
        ord_idx = np.argsort(order.values)
        x = order.dt.dayofyear.to_numpy()[ord_idx].tolist()
        y = g.to_numpy()[ord_idx].tolist()
        hover = [f"{int(m):02d}-{int(d):02d}" for m, d in zip(months[ord_idx], days[ord_idx])]
        return x, y, hover

    # Reserva defensiva (24 registres ~ 1 dia)
    ids = np.arange(len(df)) // 24 + 1
    g = pd.Series(df[col].to_numpy()).groupby(ids).mean()
    x = g.index.tolist()
    y = g.values.tolist()
    hover = [f"Day {i}" for i in x]
    return x, y, hover


def _canon_day_total_series(df: pd.DataFrame, col: str):
    """Retorna (x, y, hover) per a totals diaris en un eix canònic MM-DD."""
    if isinstance(df.index, pd.DatetimeIndex):
        daily = pd.to_numeric(df[col], errors="coerce").resample("D").sum(min_count=1)
        g = daily.groupby([daily.index.month, daily.index.day]).mean()
        months = np.array([idx[0] for idx in g.index], dtype=int)
        days = np.array([idx[1] for idx in g.index], dtype=int)
        order = pd.to_datetime({"year": 2001, "month": months, "day": days}, errors="coerce")
        ord_idx = np.argsort(order.values)
        x = order.dt.dayofyear.to_numpy()[ord_idx].tolist()
        y = g.to_numpy()[ord_idx].tolist()
        hover = [
            f"{int(month):02d}-{int(day):02d}"
            for month, day in zip(months[ord_idx], days[ord_idx])
        ]
        return x, y, hover

    daily_ids = np.arange(len(df)) // 24 + 1
    g = pd.to_numeric(pd.Series(df[col].to_numpy()), errors="coerce").groupby(daily_ids).sum()
    x = g.index.tolist()
    y = g.values.tolist()
    hover = [f"Day {day}" for day in x]
    return x, y, hover


def _raw_axis_data(df: pd.DataFrame, col: str):
    """X=1..N (pas), hover='MM-DD HHh' si es pot."""
    x = list(range(1, len(df) + 1))
    if _has_mdh(df):
        hover = [
            (
                f"{int(m):02d}-{int(d):02d} {int(h):02d}h"
                if pd.notna(m) and pd.notna(d) and pd.notna(h)
                else f"Step {idx}"
            )
            for idx, (m, d, h) in enumerate(
                zip(df["month"], df["day_of_month"], df["hour"]),
                start=1,
            )
        ]
    elif isinstance(df.index, pd.DatetimeIndex):
        hover = [f"{ix.month:02d}-{ix.day:02d} {ix.hour:02d}h" for ix in df.index]
    else:
        hover = [f"Step {i}" for i in x]
    y = df[col].to_list()
    return x, y, hover


def _mode_axis_config(mode: str) -> tuple[str, dict]:
    """Retorna el títol i la configuració d'eix X per al mode temporal."""
    if mode == "hour":
        return "Hour of Day", {"tickmode": "linear", "dtick": 1}
    if mode == "day":
        return "Day (1..365)", {"tickmode": "linear", "tick0": 1, "dtick": 10}
    if mode == "month":
        return "Month", {"tickmode": "linear", "dtick": 1}
    return "Time (step)", {}


def _apply_mode_xaxis(fig, mode: str, **kwargs):
    """Aplica a una figura Plotly l'eix X habitual del mode temporal."""
    title, axis_kwargs = _mode_axis_config(mode)
    axis_kwargs.update(kwargs)
    return fig.update_xaxes(title=title, **axis_kwargs)


def _series_for_mode(
    base: pd.DataFrame,
    column: str,
    mode: str,
    season: str,
    *,
    sign: float = 1.0,
) -> tuple[list, list, list | None, str] | None:
    """Retorna dades x/y/hover/trace-mode per a una sèrie mitjana segons el mode."""
    if column not in base.columns:
        return None

    if mode == "hour":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        grouped = df.groupby(_hour_series(df))[column].mean() * sign
        x_values = list(range(24))
        return x_values, [grouped.get(hour, float("nan")) for hour in x_values], None, "lines+markers"

    if mode == "day":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        x_values, y_values, hover = _canon_day_series(df, column)
        return x_values, [value * sign for value in y_values], hover, "lines"

    if mode == "month":
        df = base if season == "All" else filter_by_season(base, season)
        if df.empty:
            return None
        grouped = df.groupby(_month_series(df))[column].mean() * sign
        x_values = list(range(1, 13))
        return x_values, [grouped.get(month, float("nan")) for month in x_values], None, "lines+markers"

    if mode == "raw":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        x_values, y_values, hover = _raw_axis_data(df, column)
        return x_values, [value * sign for value in y_values], hover, "lines"

    return None


def _auto_scale_series(dfcol: pd.Series):
    """Retorna sèrie escalada i sufix ('', '×1e3', '×1e6', '×1e9')."""
    absmax = float(np.nanmax(np.abs(dfcol.to_numpy()))) if len(dfcol) else 0.0
    if absmax >= 1e9: return dfcol / 1e9, "×1e9"
    if absmax >= 1e6: return dfcol / 1e6, "×1e6"
    if absmax >= 1e3: return dfcol / 1e3, "×1e3"
    return dfcol, ""
