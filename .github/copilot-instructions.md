# Copilot Instructions for srw-chx

## Project Overview

This is a **Synchrotron Radiation Workshop (SRW)** beamline simulation for the NSLS-II CHX (Coherent Hard X-ray) beamline at Brookhaven National Laboratory. The project uses [SRWpy](https://github.com/ochubar/SRW) to simulate X-ray propagation through a complex beamline with multiple optical elements.

## Environment Management

This project uses **Pixi** (not conda/pip directly) for package management:
```bash
# Run the beamline simulation
pixi run run-sim

# Plot simulation results
pixi run plot-data
```

Dependencies are managed in `pixi.toml`. Python 3.12 is required.

## Architecture

### Beamline Simulation Flow

1. **Optical elements definition** (`set_optics()` function):
   - Creates a sequence of beamline elements in order: apertures (S0, S1, S2, S3), mirrors (HDM), compound refractive lenses (CRL1, CRL2), Kirkpatrick-Baez mirrors (KLA, KL), and drift spaces between them
   - Each element is positioned at specific distances from the source (e.g., S0 at 20.5m, HDM at 27.4m, Sample at 48.7m)
   - Elements are built using SRWlib classes: `SRWLOptA` (apertures), `SRWLOptD` (drifts), `srwl_opt_setup_surf_height_1d` (mirrors), `srwl_opt_setup_CRL` (lenses)
   - Each element has associated propagation parameters (pp) stored in the `v` parameter object

2. **Parameter management**:
   - All beamline parameters are stored in a `varParam` dictionary structure (defined in the main simulation file)
   - Parameters use a naming convention: `op_<ElementName>_<property>` (e.g., `op_S0_Dx` for S0 aperture horizontal size)
   - Parameters are parsed via `srwpy.srwl_bl.srwl_uti_parse_options()`

3. **Simulation execution** (`main()` function):
   - Parses parameters, sets up optics, configures wavefront output (`v.ws`, `v.ws_pl`), and runs full beamline calculation via `SRWLBeamline.calc_all()`
   - Results are written to `NSLS-II_CHX_beamline/res_int_pr_se.dat` by default

### Data Files

- **Input**: `NSLS-II_CHX_beamline/mirror_1d.dat` - 1D mirror surface height profile (tab-separated)
- **Output**: `NSLS-II_CHX_beamline/res_int_pr_se.dat` - 2D intensity distribution at sample plane (SRW binary format)

### Visualization

The `plot-data.py` script:
- Uses custom `read_srw_file()` function to parse SRW's custom binary format via `srwpy.uti_plot_com.file_load()`
- Extracts 2D intensity arrays and metadata (photon energy, spatial extents, labels, units)
- Displays results with matplotlib

## Key Conventions

### SRW-Specific Patterns

1. **Element naming**: Follow the convention `<Name>` for optical elements and `<Name1>_<Name2>` for drift spaces between them
2. **Mirror files**: Mirror surface errors must be tab-separated files with two columns (position, height). Always verify file existence before passing to `srwl_opt_setup_surf_height_1d()`
3. **Parameter structure**: The `v` object contains all parameters with underscore-prefixed names (e.g., `_L`, `_shape`, `_Dx`)
4. **Propagation parameters**: Each optical element requires a corresponding `pp` entry defining how wavefront propagates

### IPython Compatibility

The simulation script includes IPython detection logic at the top:
```python
try:
    __IPYTHON__
    import sys
    del sys.argv[1:]
except:
    pass
```
This allows running the script both as a standalone program and in IPython/Jupyter environments.

## Element Positioning

Optical element distances from the source are configured through:

1. **Initial position** - `op_r` parameter sets distance from source to the **first** optical element:
   ```python
   ['op_r', 'f', 20.5, 'longitudinal position of the first optical element [m]']
   ```
   This means S0 is at 20.5m from the undulator source.

2. **Subsequent positions** - Drift space lengths between elements (cumulative):
   - S0 at 20.5m (from `op_r`)
   - S0_HDM drift: 6.9m → HDM at 27.4m (20.5 + 6.9)
   - HDM_S1 drift: 2.5m → S1 at 29.9m (27.4 + 2.5)
   - S1_S2 drift: 4.4m → S2 at 34.3m (29.9 + 4.4)
   - ...continuing to Sample at 48.7m

Each drift length is configured in `varParam` as `['op_<Name1>_<Name2>_L', 'f', distance, 'length']`.

**To change element positions:**
- Modify `op_r` to move the entire beamline relative to the source
- Adjust individual drift `_L` values to change spacing between elements (affects all downstream positions)

## Modifying the Beamline

To add, remove, or reorder optical elements:

1. Update the `names` list in `set_optics()` with element names
2. Add corresponding `elif el_name == 'NewElement':` blocks following existing patterns
3. Ensure each element has matching parameters in `varParam` dictionary
4. Update drift distances (`_L` parameter) if element positions change
5. Pass the updated `names` list to `set_optics()` in `main()`

## Common Tasks

- **Change simulation energy**: Modify photon energy parameters in `varParam` (search for energy-related variables)
- **Adjust aperture sizes**: Modify `op_<ApertureName>_Dx` and `op_<ApertureName>_Dy` parameters
- **Change lens focus**: Adjust CRL parameters (`op_CRL1_foc_plane`, `op_CRL1_delta`, etc.)
- **Modify output location**: The sample position is determined by `op_r` plus all cumulative drift distances
