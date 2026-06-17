import streamlit as st
import numpy as np
import pandas as pd
import os


@st.cache_resource
def _load_raw_shap_array():
    """Loads the raw .npy file once into global memory for the entire app lifetime."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    shap_file_path = os.path.join(
        project_root, "data", "shap_values", "shap_values.npy")

    try:
        # Utilizing memory-mapping to prevent RAM bloat when reading massive 3D tensor files
        return np.load(shap_file_path, mmap_mode='r')
    except FileNotFoundError:
        st.error(f"SHAP file not found at {shap_file_path}")
        return None


@st.cache_data
def load_engine_data(engine_id: int):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    base_data_path = os.path.join(project_root, "data")
    test_file_path = os.path.join(base_data_path, "test_FD004.txt")

    attention_file = os.path.join(
        base_data_path, "predictions", "predicted_rul_attention.npy")
    advanced_file = os.path.join(
        base_data_path, "predictions", "predicted_rul_advanced.npy")

    try:
        cmapss_columns = ['unit_nr', 'time_cycles', 'setting_1', 'setting_2', 'setting_3',
                          's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10',
                          's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21']

        # Parsing raw text telemetry and stripping redundant constant-value sensor columns
        df_test = pd.read_csv(test_file_path, sep=r'\s+',
                              header=None, names=cmapss_columns)
        columns_to_drop = ['s1', 's5', 's6', 's10', 's16', 's18', 's19']
        df_test = df_test.drop(columns=columns_to_drop)

        df_engine_telemetry = df_test[df_test['unit_nr'] == engine_id].copy()

        all_attention_predictions = np.load(attention_file).flatten()
        all_advanced_predictions = np.load(advanced_file).flatten()

        final_attention_pred = all_attention_predictions[engine_id - 1]
        final_advanced_pred = all_advanced_predictions[engine_id - 1]

        total_recorded_cycles = df_engine_telemetry['time_cycles'].max()

        est_life_attention = total_recorded_cycles + final_attention_pred
        est_life_advanced = total_recorded_cycles + final_advanced_pred

        # Fusing live cycle counts with baseline predictions to generate real-time Remaining Useful Life
        df_engine_telemetry['AeroGlass_XAI_RUL'] = est_life_attention - \
            df_engine_telemetry['time_cycles']
        df_engine_telemetry['Baseline_Advanced_RUL'] = est_life_advanced - \
            df_engine_telemetry['time_cycles']

        return df_engine_telemetry

    except FileNotFoundError as error:
        st.error(
            f"Data loading failed: {error}. Verify files in data/predictions/.")
        return None
    except IndexError:
        st.error(f"Engine {engine_id} prediction not found.")
        return None


@st.cache_data
def load_shap_values(engine_id: int, target_cycle: int):
    try:
        ordered_feature_names = [
            'S11 (HPC Static Pressure)', 'S12 (Ratio of Fuel Flow)',
            'S13 (Corrected Fan Speed)', 'S14 (Corrected Core Speed)',
            'S15 (Bypass Ratio)', 'S17 (Bleed Enthalpy)',
            'S2 (LPC Outlet Temp)', 'S20 (HPT Coolant Bleed)',
            'S21 (LPT Coolant Bleed)', 'S3 (HPC Outlet Temp)',
            'S4 (LPT Outlet Temp)', 'S7 (HPC Outlet Pressure)',
            'S8 (Physical Fan Speed)', 'S9 (Core Speed)',
            'Setting 1 (Altitude)', 'Setting 2 (Mach Number)',
            'Setting 3 (Throttle Resolver Angle)'
        ]

        shap_values = _load_raw_shap_array()
        if shap_values is None:
            return None

        sequence_length = 30

        if target_cycle < sequence_length:
            st.warning(
                f"No SHAP values available before cycle {sequence_length}.")
            return None

        cycle_index = target_cycle - sequence_length

        try:
            # Slicing the 3D SHAP tensor to isolate cycle-specific feature impacts
            engine_shap_data = shap_values[engine_id - 1]
            max_available_index = len(engine_shap_data) - 1
            if cycle_index > max_available_index:
                cycle_index = max_available_index
            raw_shap_matrix = engine_shap_data[cycle_index]

        except IndexError:
            st.warning(
                f"Engine {engine_id} SHAP data structure unavailable. Falling back to fleet constraints.")
            return None

        # Flattening sequence dimensions if the explainer outputs a 2D time-series matrix
        if raw_shap_matrix.ndim == 2:
            shap_impact_values = np.sum(raw_shap_matrix, axis=0)
        else:
            shap_impact_values = raw_shap_matrix

        return dict(zip(ordered_feature_names, shap_impact_values))

    except Exception as error:
        st.error(f"SHAP extraction failed: {error}.")
        return None


@st.cache_data(ttl=300)
def load_fleet_summary():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    base_data_path = os.path.join(project_root, "data")
    test_file_path = os.path.join(base_data_path, "test_FD004.txt")
    predictions_file_path = os.path.join(
        base_data_path, "predictions", "predicted_rul_attention.npy")

    try:
        cmapss_columns = ['unit_nr', 'time_cycles', 'setting_1', 'setting_2', 'setting_3',
                          's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10',
                          's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21']

        df_test = pd.read_csv(test_file_path, sep=r'\s+',
                              header=None, names=cmapss_columns)

        # Aggregating maximum recorded flight cycles to determine current fleet age
        fleet_stats = df_test.groupby(
            'unit_nr')['time_cycles'].max().reset_index()
        fleet_stats.columns = ['Engine ID', 'Current Flight Cycles']

        all_predictions = np.load(predictions_file_path).flatten()

        if len(all_predictions) < len(fleet_stats):
            st.error(
                f"Prediction file has {len(all_predictions)} entries but fleet has {len(fleet_stats)} engines. Data is misaligned.")
            return None

        fleet_stats['Predicted Remaining Cycles (RUL)'] = all_predictions[:len(
            fleet_stats)]

        # Applying deterministic safety thresholds to classify operational readiness
        fleet_stats['Status'] = fleet_stats['Predicted Remaining Cycles (RUL)'].apply(
            lambda x: 'CRITICAL' if x < 30 else (
                'WARNING' if x < 75 else 'HEALTHY')
        )

        return fleet_stats

    except FileNotFoundError as error:
        st.error(f"Fleet data loading failed: {error}")
        return None
