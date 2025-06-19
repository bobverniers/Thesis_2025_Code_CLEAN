#!/usr/bin/env python3
"""
evaluation/utils.py

Common helpers for loading restaurant CSVs and filtering by ground-truth tag counts.
"""
import pandas as pd
import random


def load_restaurants_csv(path):
    """Load a restaurants CSV into a DataFrame."""
    return pd.read_csv(path)

def filter_by_min_tags(df, min_tags=4, ignore_cols=None):
    """
    Return only those rows in df having ≥ min_tags non-null tag columns,
    excluding any in ignore_cols.
    """
    if ignore_cols is None:
        ignore_cols = {'name', 'amenity', 'osm_id', 'osm_type'}
    tag_cols = [c for c in df.columns if c not in ignore_cols]
    df = df.copy()
    df['__tag_count'] = df[tag_cols].notna().sum(axis=1)
    out = df[df['__tag_count'] >= min_tags].drop(columns='__tag_count')
    return out

def extract_first_tag_hint(df, ignore_cols=None):
    """
    For each row, take the first non-null tag column name (excluding ignore_cols)
    and return a Series of those keys (e.g. "cuisine", "opening_hours", etc.).
    """
    import pandas as pd

    if ignore_cols is None:
        ignore_cols = {'name', 'amenity', 'osm_id', 'osm_type'}
    tag_cols = [c for c in df.columns if c not in ignore_cols]

    def _first_tag_key(row):
        for c in tag_cols:
            if pd.notna(row[c]):
                return c
        return None

    return df.apply(_first_tag_key, axis=1)

def extract_random_tag_hint(df, ignore_cols=None, seed=42):
    """
    For each row, pick a random GT tag as the hint_tag.

    Returns a Series of keys 

    Arguments:
    - df: dataframe
    - ignore_cols: columns to ignore (default = {'name', 'amenity', 'osm_id', 'osm_type'})
    - seed: random seed (default = 42)
    """
    random.seed(seed)

    if ignore_cols is None:
        ignore_cols = {'name', 'amenity', 'osm_id', 'osm_type'}
    tag_cols = [c for c in df.columns if c not in ignore_cols]

    def _random_tag(row):
        present_tags = [c for c in tag_cols if pd.notna(row[c])]
        return random.choice(present_tags) if present_tags else ''

    return df.apply(_random_tag, axis=1)