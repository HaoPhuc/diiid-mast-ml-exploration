# FAIR-MAST level 2 shot table: column classification

One row per shot, about 290 columns. Most columns are scalar summaries from the MAST Central Physics File (CPF).

**Source of names and descriptions.** The column names are the `alias` fields in `src/api/models.py` of [ukaea/fair-mast](https://github.com/ukaea/fair-mast) at commit `35ddac3`. That is the last version before the API was removed on 2026-10-26 (commit `4025f70`, "Docs Without API"). Each entry lists the original CPF code in brackets. These have **not yet been checked against a downloaded `l2_shots.parquet`**. Confirm column presence, units and missing-value fractions when the file is loaded.

**Data location changed.** `https://mastapp.site/parquet/level2/shots` no longer exists. The table is now at `https://s3.echo.stfc.ac.uk/mast/fairmast-meta/l2_shots.parquet` (sources: `l2_sources.parquet`; signals: `l2_signals/signals_<shot_id>.parquet`).

**Time-slice suffixes** (used throughout section 8):

- `_max_current`: value at the time of peak plasma current (CPF `_ipmax`)
- `_max` / `max_`: maximum (or `min_`: minimum) over the shot, each at its own time
- `_ruby_time`: value at the Ruby Thomson-scattering laser time (CPF `_truby`, MAST only)
- For physically consistent features and targets, take all quantities from the **same** slice. `_max_current` is the most complete family.

Role tags: **IGNORE** (not for modelling), **FILTER** (selects shots, not a feature), **GROUP** (cross-validation split key), **FEATURE**, **TARGET**, **LEAKAGE** (derived from the target; never a feature for that target).

---

## 1. Shot identification: IGNORE

shot_id: unique numeric identifier for the shot (shot index)
uuid: alphanumeric ID used internally by the database to track records
url: S3 location of this shot's Zarr file
endpoint_url: S3 endpoint for `url` (https://s3.echo.stfc.ac.uk)
timestamp: time the shot was fired (ISO 8601)
shot_creation_date: creation date of the CPF data-dictionary entry, not the shot date (CPF `creation`)
shot_experiment_date: date the shot was run (CPF `exp_date`)
shot_experiment_time: time of day the shot was run (CPF `exp_time`)
shot_experiment_number: experiment pulse number (CPF `exp_number`)
shot_pulse_number: MAST experiment pulse number (CPF `pulno`); should equal shot_id, useful as a consistency check
facility: tokamak that produced the shot (MAST)
reference_shot: reference shot used as the basis for setting up this shot (from the shot database)
shot_reference: the same reference shot as recorded in the CPF (CPF `reference`); the two should agree, check on load
shot_experiment_tags: experiment tags (CPF `experiments`)
shot_physicist: physicist in charge (CPF `pic`)
title: dataset title (catalogue metadata)
type_: DCAT record type, always `dcat:Dataset` (catalogue metadata, no physics content)
context_: JSON-LD context mapping vocabulary to IRIs (catalogue metadata, no physics content)

---

## 2. Shot descriptions (free text): IGNORE

Free text could be mined later (for example keyword flags such as "disruption" or "H-mode"), but it is not used in the numeric baseline.

shot_objective: scientific objective (CPF `objective`)
shot_summary: session summary (CPF `summary`)
shot_preshot_comment: session leader's pre-shot comment (CPF `preshot`)
shot_postshot_comment: session leader's post-shot comment (CPF `postshot`)
preshot_description: investigator's description before the shot (shot database)
postshot_description: investigator's description after the shot (shot database)
shot_program: scientific programme (CPF `programme`)
shot_scenario: scenario tags, text (CPF `scenario`); not the same as the integer `scenario` in section 4

---

## 3. Quality and outcome flags: FILTER

Moved out of section 2: these are not features, but they decide which shots enter the dataset. `shot_end_code` is also a candidate label for a later classification task (termination or disruption type).

shot_useful: flag marking the shot as useful (CPF `useful`); keep `== 1`
shot_abort: flag marking the shot as aborted (CPF `abort`); keep `== 0`
shot_end_code: plasma termination reason code (CPF `term_code`); code meanings are not documented in the schema

---

## 4. Shot configuration (categorical, set before the shot): FEATURE / GROUP

campaign: experimental campaign, e.g. `M9`. **GROUP**: split train/test by campaign so similar shots don't end up in both sets
scenario: scenario ID (integer)
heating: type of heating used (e.g. ohmic, NBI)
pellets: whether pellet injection was used
rmp_coil: whether resonant magnetic perturbation (RMP) coils were used
current_range: plasma current range category, e.g. '750 kA'
divertor_config: divertor configuration
plasma_shape: plasma shape, e.g. 'Connected Double Null'
commissioner: organisation that commissioned the shot, e.g. 'UKAEA'

---

## 5. Pre-shot vessel conditioning: optional FEATURE

Wall conditioning and base pressure affect impurity content and density control. Worth trying after the baseline.

shot_glow_discharge_duration: Shot glow discharge duration (CPF `gdc_duration`)
shot_glow_discharge_time: Shot glow discharge time (CPF `gdc_time`)
gas_inboard_pressure_pre_pulse: Inboard gas pressure prior to pulse (CPF `ibgas_pressure`)
gas_tg1_pressure_ps: TG1 Base Pressure prior to Shot (CPF `log_base_pressure`)
gas_col_temp_in: centre column inlet temperature (CPF `column_temp_in`)
gas_col_temp_out: centre column outlet temperature (CPF `column_temp_out`)

---

## 6. Machine control system (MCS) setup, MAST only: IGNORE for the baseline

Power-supply selections, bank voltages and enable windows. Most are hardware switches with little direct physics content. Times are offset by 5 s, as the descriptions note. Pre-shot setpoints that could be useful features later: `mcs_tf_flat_top_value` (toroidal field setpoint in tesla at R = 0.7 m), `mcs_plasma_direction`, `mcs_gas_puff_pressure`, `mcs_plenum_gas_pressure`, and the NBI gas species `mcs_ss_nbi_gas` / `mcs_sw_nbi_gas_mcs`.

mcs_gdc_pre_shot: GDC completed prior to shot (CPF `p03249`)
mcs_select_gas_group_pv1: select gas group 1 (CPF `p04673`)
mcs_select_gas_group_pv2: select gas group 2 (CPF `p04674`)
mcs_select_gas_group_pv3: select gas group 3 (CPF `p04675`)
mcs_select_gas_group_pv4: select gas group 4 (CPF `p04676`)
mcs_select_gas_group_pv5: select gas group 5 (CPF `p04677`)
mcs_select_gas_group_pv6: select gas group 6 (CPF `p04678`)
mcs_select_gas_group_pv7: select gas group 7 (CPF `p04679`)
mcs_select_gas_group_pv8: select gas group 8 (CPF `p04680`)
mcs_select_gas_group_pv9: select gas group 9 (CPF `p04681`)
mcs_select_lvps_tf_power_supply: select TF power supply (CPF `p04833`)
mcs_select_cp3s_start_bank: select P3 start bank (CPF `p04993`)
mcs_select_fa1: Select FA1 (CPF `p05007`)
mcs_select_fa2: Select FA2 (CPF `p05008`)
mcs_select_mfps: Select MFPS (CPF `p05009`)
mcs_select_efps: Select EFPS (CPF `p05010`)
mcs_select_sfps: Select SFPS (CPF `p05011`)
mcs_select_scs4: Select SCS4 (CPF `p05015`)
mcs_select_fa3: Select FA3 (CPF `p05016`)
mcs_select_fa4: Select FA4 (CPF `p05017`)
mcs_select_p1ps: Select P1Ps (CPF `p05025`)
mcs_select_cp3c_counterpulse_bank: select P3 counterpulse bank (CPF `p05027`)
mcs_select_cp4_start_bank: select P4 start bank (CPF `p05028`)
mcs_select_cp5_start_bank: select P3 start bank (CPF `p05029`)
mcs_select_p3p: select Siemens & GEC switches for P3 plasma Initiation (CPF `p05030`)
mcs_select_p4: select P4 Ignitron and Thyristor circuit (CPF `p05032`)
mcs_select_p5: select P5 Ignitron and Thyristor circuit (CPF `p05033`)
mcs_select_ecrh: Select ECRH (CPF `p05153`)
mcs_select_xmm_os9: Select XMM OS9 (Flags a Critical DATACQ System, causes shot to Abort if not ready) (CPF `p06000`)
mcs_select_xpc_os9: Select XPC OS9 (CPF `p06001`)
mcs_select_xcm_os9: Select XCM OS9 (CPF `p06002`)
mcs_select_xmw_os9: Select XMW OS9 (CPF `p06003`)
mcs_select_xma_os9: Select XMA OS9 (CPF `p06004`)
mcs_ss_nbi_gas: MCS_SS_NBI_gas_species (CPF `p10963`)
mcs_sw_nbi_gas_mcs: MCS_SW_NBI_gas_species (CPF `p10964`)
mcs_cp3s_volt: CP3 set volts (CPF `p12441`)
mcs_cp3c_volt: CP3c Set Volts (CPF `p12450`)
mcs_cp4s_volt: CP4 set volts (CPF `p12451`)
mcs_cp5s_volt: CP5 set volts (CPF `p12452`)
mcs_additive_gas_pressure: Additive gas pressure of main fueling plenum (CPF `p15202`)
mcs_plenum_gas_pressure: Latest gas pressure of main fueling plenum (CPF `p15203`)
mcs_tg1_base_pressure: TG1 Base Pressure (CPF `p15209`)
mcs_p3_direction: P3 Direction Monitored state of Polarity-reversing/isolation switches (CPF `p15659`)
mcs_p4_direction: P4 direction: 1= Normal Direction (Positive Ip), 3= Open Circuit (CPF `p15660`)
mcs_p5_direction: P5 direction: 2= Reverse Direction (Positive Ip) (CPF `p15661`)
mcs_ss_number: Shot sequence number (CPF `p20000`)
mcs_pshot_gdc_time: Pre-Shot GDC duration (CPF `p20204`)
mcs_gdc_start_time: Last GDC start time (CPF `p20205`)
mcs_gas_puff_pressure: Inboard Gas Puff Pressure (CPF `p20206`)
mcs_gas_puff_start_time: Inboard Gas Puff Start Time Relative to 10s (CPF `p20207`)
mcs_gas_puff_duration: Inboard Gas Puff Duration (CPF `p20208`)
mcs_p2xo: Param mim430 - P2XO Mode (P2 Reversing Switch Mode: 0= +ve only, 1= -ve only, 2= +ve => -ve, 3= -ve => +ve) (CPF `p21010`)
mcs_p2xo_start_forward: Param mim430 - P2XO Start Forward (Offset by 5s: enable +ve polarity at time-5s) (CPF `p21011`)
mcs_p2xo_start_reverse: Param mim430 - P2XO Start Reverse (Enable -ve polarity at 5s + time) (CPF `p21012`)
mcs_tf_flat_top_value: Param mim421 - TF Flat Top set value (Tesla @ R=0.7m) (CPF `p21021`)
mcs_tf_flat_top_time: Param mim421 - TF Flat Top set time (CPF `p21022`)
mcs_tf_rise_time_value: Param mim421 - TF Rise Time set value (CPF `p21029`)
mcs_plasma_direction: Plasma Direction (1.0 => Positive: Dervived from P3/P4/P5 switch settings (P15659-P15661)) (CPF `p21035`)
mcs_p2_config: Required P2 Linkboard config number (must match setting in PLC) (CPF `p21037`)
mcs_cp3s_start_time: CP3s start time (Offset by 5s) (CPF `p21041`)
mcs_cp3c_start_time: CP3c start time (Offset by 5s) (CPF `p21042`)
mcs_cp4_start_time: CP4 start time (Offset by 5s) (CPF `p21043`)
mcs_p4_ignitron_start_time: Close P4 circuit ignitron start time (Offset by 5s) (CPF `p21044`)
mcs_p4_thyristor_start_time: P4 Circuit thyristor start time (Offset by 5s) (CPF `p21045`)
mcs_cp5_start_time: CP5 Start time (Offset by 5s) (CPF `p21046`)
mcs_p5_ignitron_start_time: P5 ignitron start time (Offset by 5s) (CPF `p21047`)
mcs_p5_thyristor_start_time: P5 thyristor start time (Offset by 5s) (CPF `p21048`)
mcs_mfps_current_limit: MFPS Power supply current limit (CPF `p21051`)
mcs_mfps_start_time: MFPS set enable start time (Offset by 5s) (CPF `p21052`)
mcs_efps_current_limit: EFPS Power supply current limit (CPF `p21053`)
mcs_efps_start_time: EFPS set enable start time (Offset by 5s) (CPF `p21054`)
mcs_sfps_current_limit: SFPS power supply current limit (CPF `p21055`)
mcs_sfps_start_time: SFPS set enable start time (Offset by 5s) (CPF `p21056`)
mcs_mfps_duration: MFPS enable duration (CPF `p21075`)
mcs_efps_duration: EFPS enable duration (CPF `p21076`)
mcs_sfps_duration: SFPS enable duration (CPF `p21077`)
mcs_p1ps_pos_current_limit: P1PS maximum positive current limit (CPF `p21078`)
mcs_p1ps_negative_current_limit: P1PS maximum negative current limit (CPF `p21079`)
mcs_p1ps_start_time: P1PS enable start time (offset by 5s) (CPF `p21080`)
mcs_p1ps_duration: P1PS enable duration (CPF `p21081`)
mcs_fa1_start_time: FA1 enable start time (offset by 5s) (CPF `p21082`)
mcs_fa1_duration: FA1 enable duration (CPF `p21083`)
mcs_fa2_start_time: FA2 enable start time (offset by 5s) (CPF `p21084`)
mcs_fa2_duration: FA2 enable duration (CPF `p21085`)
mcs_fa3_start_time: FA3 enable start time (offset by 5s) (CPF `p21086`)
mcs_fa3_duration: FA3 enable duration (CPF `p21087`)
mcs_fa4_start_time: FA4 enable start time (offset by 5s) (CPF `p21088`)
mcs_fa4_duration: FA4 enable duration (CPF `p21089`)
mcs_scs4_start_time: SCS4 enabled start time used by MBD (CPF `p21092`)
mcs_scs4_duration: SCS4 enabled duration (CPF `p21093`)

---

## 7. Event timing (seconds): use for windows and quality checks, not as raw features

Times of current flat top, NBI and gas-puff windows, and the time at which each quantity peaks. Use them to choose time windows when reading the per-shot Zarr traces, and to derive durations (e.g. NBI on-time). `shot_flat_top_duration` is a reasonable FEATURE.

generic_min_radius_max_plasma: Time of Maximum Plasma Minor Radius (CPF `tamin_max`)
generic_max_poloidal_area: Time of Maximum Poloidal Cross-Sectional Area (CPF `tarea_max`) **[DUPLICATE NAME]**
generic_max_beta_poloidal_mhd: Time of Maximum Beta Poloidal MHD (CPF `tbepmhd_max`)
generic_max_beta_mhd: Time of Maximum Beta MHD (CPF `tbetmhd_max`)
generic_max_toroidal_time: Time of Maximum Toroidal Magnetic Field Strength (CPF `tbt_max`)
generic_max_dt_mhd_energy_time: Time of Maximum Rate of Change of MHD Stored Energy (CPF `tdwmhd_max`)
plasma_end_time: current end time (CPF `tend`)
gas_puff_end_time: Inboard Gas Puff End Time (CPF `tend_ibgas`)
nbi_end_time: end time (CPF `tend_nbi`)
nbi_end_time_ss: SS NBI end time (CPF `tend_nbi_ss`) **[DUPLICATE NAME]**
nbi_end_time_ss: SW NBI end time (CPF `tend_nbi_sw`) **[DUPLICATE NAME]**
plasma_flat_top_end_time: Current Flat-Top End Time (CPF `tftend`)
plasma_flat_top_start_time: Current Flat-Top Start Time (CPF `tftstart`) **[DUPLICATE NAME]**
plasma_max_plasma_current_time: Time of Maximum Plasma Current (CPF `tipmax`)
generic_max_plasma_elongation_time: Time of Maximum Plasma Elongation (CPF `tkappa_max`)
equi_max_li2_time: time of Maximum li(2) (CPF `tli_2_max`)
equi_max_li3_time: time of Maximum li(3) (CPF `tli_3_max`)
thomson_max_density_line_time: Time of Maximum Electron Density Line Integral (CPF `tndl_co2_max`)
thomson_max_density_time: Time of Maximum Core Electron Density (from Nd.YAG TS) (CPF `tne0_max`)
thomson_max_pressure_time: Time of Maximum Core Electron Pressure (from Nd.YAG TS) (CPF `tpe0_max`)
nbi_max_power_time: Time of Maximum NB Power (CPF `tpnbi_max`)
nbi_max_ss_power_time: Time of Maximum SS NBI Power (CPF `tpnbi_max_ss`)
nbi_max_sw_power_time: Time of Maximum SW NBI Power (CPF `tpnbi_max_sw`)
ohmnic_max_heating_time: Time of Maximum Ohmic Heating (CPF `tpohm_max`)
generic_max_plasma_power_loss_time: Time of Maximum Plasma Radiated Power Loss (CPF `tprad_max`)
generic_min_q95_time: Time of Minimum q 95 (CPF `tq95_min`)
generic_max_geo_major_radius_time: Time of Maximum Geometrical Mid-plane Center Major Radius (CPF `trgeo_max`)
thomson_ruby_time: Ruby Thomson Scattering Time (CPF `truby`)
generic_max_plasma_s_area_time: Time of Maximum Plasma Surface Area (CPF `tsarea_max`)
plasma_flat_top_start_time: Current Flat-Top Start Time (CPF `tstart`) **[DUPLICATE NAME]**
gas_puff_start_time: Inboard Gas Puff Start Time (CPF `tstart_ibgas`)
nbi_start_time: Start Time (CPF `tstart_nbi`)
nbi_ss_start_time: SS NBI Start Time (CPF `tstart_nbi_ss`)
nbi_sw_start_time: SW NBI Start Time (CPF `tstart_nbi_sw`)
generic_max_total_energy_time: Time of Maximum Total Energy Confinement Time (CPF `ttautot_max`)
thomson_max_temp_time: Time of Maximum Core Electron Temperature (from Nd.YAG TS) (CPF `tte0_max`)
generic_max_plasma_vol_time: Time of Maximum Plasma Volume (CPF `tvol_max`)
generic_max_mhd_energy_time: Time of Maximum MHD Stored Energy (CPF `twmhd_max`)
generic_max_plasma_zeff_time: Time of Maximum Plasma Z-Effective (CPF `tzeff_max`)
shot_flat_top_duration: Plasma Current Flat-Top Duration (CPF `ftduration`)

---

## 8. Physics summary scalars: main FEATURES and TARGETS

### 8.1 Plasma current

Role: FEATURE. Ip is the main driver in every confinement scaling law. Use `plasma_max_current` with targets at the `_max_current` slice.

plasma_time_avg_current: Time averaged plasma current during flat-top (CPF `ip_av`)
plasma_time_all_avg_current: Time averaged plasma current for the whole time (CPF `ip_av_all_time`)
plasma_max_current: Maximum value of plasma current (CPF `ip_max`)

### 8.2 Toroidal field

Role: FEATURE (B_T).

generic_toroidal_max_current: Toroidal field strength at time of peak plasma current (CPF `bt_ipmax`)
generic_max_toroidal: Maximum Toroidal field strength (CPF `bt_max`)
generic_toroidal_ruby_time: Toroidal field strength at time of ruby TS (CPF `bt_truby`)

### 8.3 Geometry and shape (EFIT)

Role: FEATURE: minor radius a, major radius R_geo, elongation κ, volume and area. Volume and surface area overlap with a, R and κ, so pick one set.

generic_minor_radius_max_current: Minor radius at time of peak plasma current (CPF `amin_ipmax`)
generic_minor_radius: Maximum value of minor radius (CPF `amin_max`)
generic_minor_radius_ruby_time: Minor radius at time of Ruby TS (CPF `amin_truby`)
generic_poloidal_area_max_current: poloidal cross-sectional area at time of peak plasma current (CPF `area_ipmax`)
generic_max_poloidal_area: Maximum Poloidal Cross-Sectional Area (CPF `area_max`) **[DUPLICATE NAME]**
generic_poloidal_area_ruby_time: Poloidal Cross-Sectional Area at time of Ruby TS (CPF `area_truby`)
generic_plasma_elongation_max_current: Plasma Elongation at time of Peak Plasma Current (CPF `kappa_ipmax`)
generic_plasma_elongation_max: Maximum value of Plasma Elongation (CPF `kappa_max`)
generic_plasma_elongation_ruby_time: Plasma Elongation at time of Ruby TS (CPF `kappa_truby`)
generic_geo_radius_max_current: geometrical center major radius at time of peak plasma current (CPF `rgeo_ipmax`)
generic_max_geo_radius: Maximum value of Geometrical Center Major Radius (CPF `rgeo_max`)
generic_geo_radius_ruby_time: geometrical Center Major Radius at time of Ruby TS (CPF `rgeo_truby`)
radii_rinner_radius_d_alpha: rinner major Radius from Visible D_Alpha Light (CPF `rinner_da`)
radii_rinner_radius_efit: rinner major Radius from EFIT Equilibrium (CPF `rinner_efit`)
radii_magnetic__radius_efit: magnetic Axis major Radius from EFIT Equilibrium (CPF `rmag_efit`)
radii_router_radius_d_alpha: router major Radius from Visible D_Alpha Light (CPF `router_da`)
radii_router_radius_efit: router major Radius from EFIT Equilibrium (CPF `router_efit`)
radii_s_area_max_current: Total Surface Area at time of Peak Plasma Current (CPF `sarea_ipmax`)
generic_s_area_max: maximum Total Surface Area (CPF `sarea_max`)
generic_s_area_ruby_time: total Surface Area at time of Ruby TS (CPF `sarea_truby`)
generic_plasma_vol_max_current: Plasma Volume at time of Peak Plasma Current (CPF `vol_ipmax`)
generic_max_plasma_vol: Maximum Plasma Volume (CPF `vol_max`)
generic_plasma_vol_ruby_time: Plasma Volume at time of Ruby TS (CPF `vol_truby`)
rad_magnetic_height_efit: Magnetic Axis height above Mid-Plane from EFIT Equilibrium (CPF `zmag_efit`)

### 8.4 Equilibrium / MHD (EFIT)

Role: Mostly **LEAKAGE** when the target is stored energy or τ_E: β and β_p are proportional to stored energy by definition, and li and q95 come from the same EFIT reconstruction. q95 is mostly a function of Ip, B_T and the shape, so it is redundant with those features.

generic_beta_poloidal_max_current: Beta poloidal at time of Peak Plasma Current (CPF `bepmhd_ipmax`)
generic_max_beta_poloidal: Maximum Beta poloidal (CPF `bepmhd_max`)
generic_beta_poloidal_ruby_time: Beta poloidal at time of Ruby TS (CPF `bepmhd_truby`)
generic_beta_time_max_current: Beta at time of peak plasma current (CPF `betmhd_ipmax`)
generic_max_beta_max_current: Maximum beta at time of peak plasma current (CPF `betmhd_max`)
generic_beta_ruby_time: Beta at time of ruby TS (CPF `betmhd_truby`)
equi_li2_max_current: li(2) at time of Peak Current (CPF `li_2_ipmax`)
equi_max_li2: li(2) Maximum value (CPF `li_2_max`)
equi_li2_ruby_time: li(2) Maximum value (CPF `li_2_truby`)
equi_li3_max_current: li(3) at time of Peak Current (CPF `li_3_ipmax`)
equi_max_li3: li(3) Maximum value (CPF `li_3_max`)
equi_li3_ruby_time: li(3) at time of Ruby TS (CPF `li_3_truby`)
generic_q95_max_current: q-95 at time of Peak Plasma Current (CPF `q95_ipmax`)
generic_min_q95: Minimum value of q-95 (CPF `q95_min`)
generic_q95_ruby_time: q-95 at time of Ruby TS (CPF `q95_truby`)

### 8.5 Stored energy and confinement (EFIT)

Role: **TARGET** candidates: `generic_energy_current_max` (W_MHD at peak Ip) or `generic_energy_time_max_current` (τ_E at peak Ip). τ_E ≈ W/P_loss, so never use W to predict τ_E, or the reverse. dW/dt is LEAKAGE for both.

generic_dt_energy_max_current: rate of change of total stored energy at time of peak plasma current (CPF `dwmhd_ipmax`)
generic_dt_total_energy: maximum rate of change of total stored energy (CPF `dwmhd_max`)
generic_dt_energy_ruby_time: rate of change of MHD stored energy at time of ruby TS (CPF `dwmhd_truby`)
generic_energy_time_max_current: Energy Confinement Time at time of Peak Plasma Current (CPF `tautot_ipmax`)
generic_max_energy_time: Maximum value of Energy Confinement Time (CPF `tautot_max`)
generic_energy_time_ruby_time: Energy Confinement Time at time of Ruby TS (CPF `tautot_truby`)
generic_energy_current_max: Stored Energy at time of Peak Plasma Current (CPF `wmhd_ipmax`)
generic_energy_max: Maximum Stored Energy (CPF `wmhd_max`)
generic_energy_ruby_time: Stored Energy at time of Ruby TS (CPF `wmhd_truby`)

### 8.6 Kinetic profiles: density, temperature, pressure (Thomson scattering + CO2 interferometer)

Role: FEATURE: density (core n_e0 from Thomson, line integral and line average from the CO2 interferometer, despite the `thomson_` prefix). T_e and p_e are partly LEAKAGE for a W target, because W ∝ ∫p dV. Density is the standard input; temperature and pressure are not.

thomson_density_line_max_current: Electron Density Line Integral at time of Peak Plasma Current (CPF `ndl_co2_ipmax`)
thomson_max_density_line: Maximum Electron Density Line Integral observed by CO2 Interferometer (CPF `ndl_co2_max`)
thomson_density_line_ruby_time: Electron Density Line Integral at time of Ruby TS (CPF `ndl_co2_truby`)
thomson_density_max_current: Core Electron Density (Nd.YAG) at time of Peak Current (CPF `ne0_ipmax`)
thomson_density_max: Peak Core Electron Density (Nd.YAG) (CPF `ne0_max`)
thomson_density_ruby_time: Core Electron Density (Nd.YAG) at time of Ruby TS (CPF `ne0_truby`) **[DUPLICATE NAME]**
thomson_ne0_rat_line_avg_ne: Ratio of ne0 to line average ne (CPF `ne0ratio_ipmax`)
thomson_density_ruby_time: Core Electron Density (Nd.YAG) at time of Ruby TS (CPF `ne0ruby`) **[DUPLICATE NAME]**
thomson_line_avg_density_co2: Mid-plane line average electron density from CO2 interferometer (CPF `ne_bar_ipmax`) **[DUPLICATE NAME]**
thomson_line_avg_density_co2: Mid-plane line average electron density from CO2 interferometer (CPF `ne_yag_bar_ipmax`) **[DUPLICATE NAME]**
thomson_greenwald_density_limit: Greenwald Density Limit (CPF `ngreenwald_ipmax`)
thomson_greenwald_rat_line_avg_density: Ratio of Greenwald density limit to mid-plane line averaged electron density (CPF `ngreenwaldratio_ipmax`)
thomson_pressure_max_current: Core Electron Pressure (Nd.YAG) at time of Peak Plasma Current (CPF `pe0_ipmax`)
thomson_pressure_max: Maximum value of Core Electron Pressure (Nd.YAG) (CPF `pe0_max`)
thomson_pressure_ruby_time: Core Electron Pressure (Nd.YAG) at time of Ruby TS (CPF `pe0_truby`)
thomson_pressure_ruby: Ruby TS Core Electron Pressure (CPF `pe0ruby`)
thomson_temp_max_current: Core Electron Temperature (Nd.YAG) at time of Peak Current (CPF `te0_ipmax`)
thomson_temp_max: Peak Core Electron Temperature (Nd.YAG) (CPF `te0_max`)
thomson_temp_ruby_time: Core Electron Temperature (Nd.YAG) at time of Ruby TS (CPF `te0_truby`)
thomson_temp_rat_line_avg_temp: ratio of Core Electron Temperature to line average Te (CPF `te0ratio_ipmax`)
thomson_temp_ruby: Ruby TS Core Electron Temperature (CPF `te0ruby`)
thomson_yag_line_avg_temp: Mid-plane line average electron temperature from YAG Thomson scattering (CPF `te_yag_bar_ipmax`)

### 8.7 Heating: NBI and ohmic

Role: FEATURE: input power. P_NBI + P_ohm is the heating power in scaling laws. SS and SW are MAST's two neutral beam lines. `_energy`/`injected_energy` columns are time-integrated energy (J); `_power` columns are instantaneous power.

nbi_energy_ss_max_power: injection energy from SS beam at time of peak power (CPF `enbi_max_ss`)
nbi_energy_sw_max_power: injection energy from SW beam at time of peak power (CPF `enbi_max_sw`)
nbi_injected_energy_max_current: injected energy from SS+SW beams at time of peak current (CPF `jnbi_ipmax`)
nbi_injected_energy_ss_max_current: injected energy from SS beams at time of peak current (CPF `jnbi_ipmax_ss`) **[DUPLICATE NAME]**
nbi_injected_energy_ss_max_current: injected energy from SW beams at time of peak current (CPF `jnbi_ipmax_sw`) **[DUPLICATE NAME]**
nbi_injected_energy_max: injected energy from SS+SW beams at time of peak power (CPF `jnbi_max`)
nbi_energy_ss_max_current: injection energy from SS beam at time of peak power (CPF `jnbi_max_ss`)
nbi_energy_sw_max_current: injection energy from SW beam at time of peak power (CPF `jnbi_max_sw`)
nbi_total_injected_energy: Total NBI injected energy from SS+SW beams (CPF `jnbi_total`)
nbi_total_injected_energy_ss: Total NBI Injected Energy from SS Beam (CPF `jnbi_total_ss`)
nbi_total_injected_energy_sw: Total NBI Injected Energy from SW Beam (CPF `jnbi_total_sw`)
nbi_injected_energy_ruby_time: Injected Energy from SS+SW Beams at time of Ruby TS (CPF `jnbi_truby`)
nbi_injected_energy_ss_ruby_time: NBI Injected Energy from SW Beam at time of Ruby TS (CPF `jnbi_truby_ss`)
nbi_injected_energy_sw_ruby_time: Injected Energy from SW Beam at time of Ruby TS (CPF `jnbi_truby_sw`)
ohmnic_energy_max_current: Ohmic Heating Energy Input at time of Peak Current (CPF `johm_ipmax`)
ohmnic_energy_max_heating: Ohmic Heating Energy Input at time of Maximum Ohmic Heating (CPF `johm_max`)
ohmnic_energy_total: Total Ohmic Heating Energy Input (CPF `johm_total`)
ohmnic_energy_ruby_time: Ohmic Heat Energy Input at time of Ruby TS (CPF `johm_truby`)
nbi_power_max_current: Power from SS+SW Beams at time of Peak Current (CPF `pnbi_ipmax`) **[DUPLICATE NAME]**
nbi_power_ss_max_current: Power from SS Beam at time of Peak Current (CPF `pnbi_ipmax_ss`)
nbi_power_max_current: Power from SW Beam at time of Peak Current (CPF `pnbi_ipmax_sw`) **[DUPLICATE NAME]**
nbi_power_max_power: Power from SS+SW Beams at time of Peak power (CPF `pnbi_max`)
nbi_power_max_ss: Peak NBI Power from SS Beam (CPF `pnbi_max_ss`)
nbi_power_max_sw: Peak NBI Power from SW Beam (CPF `pnbi_max_sw`)
nbi_power_ruby_time: Power from SS+SW Beams at time of Ruby TS (CPF `pnbi_truby`)
nbi_power_truby_ss: Power from SS Beam at time of Ruby TS (CPF `pnbi_truby_ss`)
nbi_power_truby_sw: Power from SW Beam at time of Ruby TS (CPF `pnbi_truby_sw`)
ohmnic_heating_max_current: Ohmic Heating Rate at time of Peak Current (CPF `pohm_ipmax`)
ohmnic_max_heating: Maximum Ohmic Heating Rate (CPF `pohm_max`)
ohmnic_heating_ruby_time: Ohmic Heating Rate at time of Ruby TS (CPF `pohm_truby`)

### 8.8 Radiation and impurities

Role: FEATURE (secondary): P_rad (loss channel, P_loss = P_heat − P_rad − dW/dt) and Z_eff.

radii_c2ratio: CII Line ratio averaged over Ip flat top from 150ms (CPF `c2ratio`)
rad_o2ratio: OII Line Ratio averaged over Ip flat top from 150ms (CPF `o2ratio`)
generic_rad_power_loss_max_current: Total Radiated Power Loss at time of Peak Plasma Current (CPF `prad_ipmax`)
generic_max_power_loss: Maximum Total Radiated Power Loss (CPF `prad_max`)
generic_power_loss_ruby_time: Total Radiated Power Loss at time of Ruby TS (CPF `prad_truby`)
rad_flat_top_power_rat_avg_line_density: Flat Top Ratio of Power Radiated to Line Density squared averaged over Ip flat top from 150ms (CPF `pradne2`)
generic_plasma_zeff_max_current: Plasma Z-Effective at time of Peak Plasma Current (CPF `zeff_ipmax`)
generic_plasma_zeff_max: Maximum Plasma Z-Effective (CPF `zeff_max`)
generic_plasma_zeff_ruby_time: Plasma Z-Effective at time of Ruby TS (CPF `zeff_truby`)

---

## 9. Unclear

cpf_sc: no description and no alias in the schema (CPF `sc`). Inspect its values on load; IGNORE until then.

---

## 10. Naming pitfalls in the published names

### 10.1 Duplicate names

In the API schema, two different CPF quantities map to the same column name in each of these pairs. Only one can survive in the parquet file, and which one is unknown until the file is loaded. Check each one against a related column (e.g. total NBI power ≥ SS power), or recompute it from the per-shot traces.

| Published name | Candidate 1 | Candidate 2 |
|---|---|---|
| `generic_max_poloidal_area` | Maximum Poloidal Cross-Sectional Area (`area_max`) | Time of Maximum Poloidal Cross-Sectional Area (`tarea_max`) |
| `nbi_end_time_ss` | SS NBI end time (`tend_nbi_ss`) | SW NBI end time (`tend_nbi_sw`) |
| `nbi_injected_energy_ss_max_current` | injected energy from SS beams at time of peak current (`jnbi_ipmax_ss`) | injected energy from SW beams at time of peak current (`jnbi_ipmax_sw`) |
| `nbi_power_max_current` | Power from SS+SW Beams at time of Peak Current (`pnbi_ipmax`) | Power from SW Beam at time of Peak Current (`pnbi_ipmax_sw`) |
| `plasma_flat_top_start_time` | Current Flat-Top Start Time (`tftstart`) | Current Flat-Top Start Time (`tstart`) |
| `thomson_density_ruby_time` | Core Electron Density (Nd.YAG) at time of Ruby TS (`ne0_truby`) | Core Electron Density (Nd.YAG) at time of Ruby TS (`ne0ruby`) |
| `thomson_line_avg_density_co2` | Mid-plane line average electron density from CO2 interferometer (`ne_bar_ipmax`) | Mid-plane line average electron density from CO2 interferometer (`ne_yag_bar_ipmax`) |

`nbi_power_max_current` (total vs. SW-beam power at peak Ip) and `thomson_line_avg_density_co2` (two line-average densities) are core regression inputs, so check these two first.

### 10.2 Times that look like values

These columns hold the **time** (s) at which the quantity peaks, not the quantity itself:

- `generic_min_radius_max_plasma`: Time of Maximum Plasma Minor Radius (CPF `tamin_max`)
- `generic_max_poloidal_area`: Time of Maximum Poloidal Cross-Sectional Area (CPF `tarea_max`)
- `generic_max_beta_poloidal_mhd`: Time of Maximum Beta Poloidal MHD (CPF `tbepmhd_max`)
- `generic_max_beta_mhd`: Time of Maximum Beta MHD (CPF `tbetmhd_max`)

### 10.3 Values whose names contain "time"

These hold **values**. In `energy_time`, "time" means energy confinement time τ_E. In `plasma_time_avg_current` it means a time average.

- `generic_beta_time_max_current`: Beta at time of peak plasma current (CPF `betmhd_ipmax`)
- `plasma_time_avg_current`: Time averaged plasma current during flat-top (CPF `ip_av`)
- `plasma_time_all_avg_current`: Time averaged plasma current for the whole time (CPF `ip_av_all_time`)
- `generic_energy_time_max_current`: Energy Confinement Time at time of Peak Plasma Current (CPF `tautot_ipmax`)
- `generic_max_energy_time`: Maximum value of Energy Confinement Time (CPF `tautot_max`)
- `generic_energy_time_ruby_time`: Energy Confinement Time at time of Ruby TS (CPF `tautot_truby`)

### 10.4 Other

- `generic_max_beta_max_current` (CPF `betmhd_max`): the source description says both "maximum" and "at time of peak plasma current". The CPF name (`_max`) suggests it is the maximum over the shot.
- `equi_li2_ruby_time` (CPF `li_2_truby`): the source description says "Maximum value", which looks like a copy error; the CPF name means li(2) at the Ruby TS time.
- `nbi_energy_ss_max_current` / `nbi_energy_sw_max_current` (CPF `jnbi_max_ss/sw`): the name says peak current, but the description says peak NBI power.
- The `thomson_` prefix is also used for CO2-interferometer quantities (`ndl_co2`, `ne_bar`).
- Typos in the published names: `ohmnic_*` (ohmic), `radii_magnetic__radius_efit` (double underscore), `rad_magnetic_height_efit` and `rad_o2ratio` (prefix `rad_` rather than `radii_`).
- Units are not stored in the schema. The FAIR-MAST CPF example notebook plots Ip in kA, n_e in m⁻³, T_e in eV and τ_E in s. Verify every unit on load.

---

## 11. Suggested first regression baseline

- **Target:** `generic_energy_current_max` (W_MHD at peak Ip), modelled as log W.
- **Features** (same time slice): `plasma_max_current`, `generic_toroidal_max_current`, `thomson_density_line_max_current`, `nbi_power_max_current` (after resolving 10.1) + `ohmnic_heating_max_current`, `generic_geo_radius_max_current`, `generic_minor_radius_max_current`, `generic_plasma_elongation_max_current`. Optional categoricals: `divertor_config`, `plasma_shape`, `heating`.
- **Exclude** as leakage: β, β_p, τ_E, dW/dt, T_e and p_e at the same slice.
- **Filters:** `shot_useful == 1`, `shot_abort == 0`, target > 0 and not missing.
- **Validation:** grouped by `campaign` (leave-one-campaign-out).
- **Models:** log-linear OLS, which has the form of a power-law scaling law, W ∝ Ip^a B^b n^c P^d …, compared with gradient-boosted trees.
- **Alternative target:** `generic_energy_time_max_current` (τ_E at peak Ip). Then W and β are excluded too.
