from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.api.types import is_categorical_dtype  # type: ignore
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)


def filter_dataframe(
    df: pd.DataFrame, label: str = "Filter dataframe on", show_histograms: bool = False
) -> pd.DataFrame:
    default_cols = st.session_state.get("filter_cols", [])
    filter_cols = st.multiselect(label, df.columns, default_cols, key="filter_cols")

    # Set the min/max bounds in advance to prevent losing downstream filter widget
    # states when an upstream filter changes.
    bounds = _get_bounds(df, filter_cols)

    for col in filter_cols:
        if show_histograms:
            try:
                _show_histogram(df, col)
            except Exception:
                pass

        # TODO: add button to reset bounds for a selected variable
        if is_bool_dtype(df[col]):
            df = _add_boolean_filter_ui(df, col)
        elif is_categorical_dtype(df[col]):
            df = _add_categorical_filter_ui(df, col, bounds)
        elif is_numeric_dtype(df[col]):
            df = _add_numeric_filter_ui(df, col, bounds)
        elif is_datetime64_any_dtype(df[col]):
            df = _add_datetime_filter_ui(df, col, bounds)
        elif is_string_dtype(df[col]):
            df = _add_regex_filter_ui(df, col)
        else:
            st.write(
                f"dtype '{df[col].dtype}' not supported for filtering (column {col})"
            )
    return df.reset_index(drop=True)


def _add_boolean_filter_ui(df: pd.DataFrame, col: str) -> pd.DataFrame:
    values = ["True", "False", "Any"]
    key = f"{col}_boolean_filter"
    user_bool_input = st.radio(f"Values for {col}", values, horizontal=True, key=key)
    if user_bool_input == "True":
        df = df[df[col]]
    elif user_bool_input == "False":
        df = df[~df[col]]
    return df


def _add_datetime_filter_ui(df: pd.DataFrame, col: str, bounds: Any) -> pd.DataFrame:
    key = f"{col}_datetime_filter"
    user_date_input = st.date_input(
        f"Values for {col}",
        value=bounds[col],
        key=key,
    )
    if len(user_date_input) == 2:  # type: ignore
        user_date_input = tuple(map(pd.to_datetime, user_date_input))  # type: ignore
        start_date, end_date = user_date_input
        df = df.loc[df[col].between(start_date, end_date)]
    return df


def _add_categorical_filter_ui(df: pd.DataFrame, col: str, bounds: Any) -> pd.DataFrame:
    key = f"{col}_categorical_filter"
    user_cat_input = st.multiselect(
        f"Values for {col}",
        bounds[col],
        key=key,
    )
    if user_cat_input:
        df = df[df[col].isin(user_cat_input)]
    return df


def _add_regex_filter_ui(df: pd.DataFrame, col: str) -> pd.DataFrame:
    key = f"{col}_regex_filter"
    user_text_input = st.text_input(f"Substring or regex in {col}", key=key)
    if user_text_input:
        df = df[df[col].astype(str).str.contains(user_text_input)]  # regex
    return df


def _add_numeric_filter_ui(df: pd.DataFrame, col: str, bounds: Any) -> pd.DataFrame:
    _min, _max = bounds[col][0], bounds[col][1]
    key = f"{col}_numeric_filter"
    user_num_input = st.slider(
        f"Values for {col}",
        min_value=_min,
        max_value=_max,
        value=(_min, _max),
        step=(_max - _min) / 500,
        key=key,
    )
    df = df[df[col].between(*user_num_input)]
    return df


def _get_bounds(df: pd.DataFrame, columns: list[str]) -> Any:
    bounds = {}
    for col in columns:
        if is_numeric_dtype(df[col]) or is_datetime64_any_dtype(df[col]):
            _min, _max = df[col].min(), df[col].max()
            bounds[col] = (_min, _max)
        elif is_categorical_dtype(df[col]):
            bounds[col] = df[col].unique()
    return bounds


def _show_histogram(df: pd.DataFrame, col: str) -> Any:
    width, height = 500, 100
    st.plotly_chart(
        px.histogram(df, col)
        .update_layout(width=width, height=height, xaxis_title_text="")
        .update_layout(margin=dict(l=0, r=0, t=0, b=0))
        .update_yaxes(visible=False),
        height=height,
        width=width,
        config=dict(displayModeBar=False),
    )
