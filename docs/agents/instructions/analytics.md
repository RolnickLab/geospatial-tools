# Analytics Skill Instructions

\<primary_directive>
Your primary objective is to extract truth from experimental data without fooling yourself or others.
**MANDATE:** Apply the project-specific rules outlined below for all analytics and EDA tasks.
\</primary_directive>

<context>
In a geospatial research setting, data analysis must account for spatial dimensions, non-standard projections, and highly skewed physical measurements (e.g., radar reflectivity, atmospheric depth).
</context>

<standards>
You MUST adhere to the following project-specific standards when performing or reviewing data analysis:

### 1. Geospatial Exploratory Data Analysis (EDA)

- **Tool Selection:** Use `geopandas` for vector data exploration, `xarray` for multidimensional raster data, and `leafmap` for interactive mapping within notebooks.
- **Profile First:** ALWAYS check for missing values (`NaN`), nodata values (which may be encoded as extreme values like `-9999`), and data types before doing any analysis.
- **Coordinate Reference Systems:** ALWAYS verify and harmonize the CRS of all datasets involved in a spatial analysis before calculating areas, distances, or intersections.

### 2. Visualization Best Practices

- **Spatial Context:** When plotting maps, ensure coastlines, borders, or a basemap are included to provide geographic context.
- **Visual Integrity:** Use perceptually uniform colormaps (e.g., `viridis`, `plasma`) for continuous geospatial data. Avoid rainbow colormaps (like `jet`) which create false boundaries.
- **Distribution Focus:** Do not just plot maps. MUST generate histograms/boxplots to understand the statistical distribution of the spatial phenomena.

### 3. Notebook Hygiene

- **Top-Down Execution:** Notebooks MUST NOT rely on hidden state. They must execute sequentially from top to bottom.
- **Narrative:** Use Markdown to explain the *why* and the *implications* of the result, especially noting any spatial anomalies.

### 4. Statistical Rigor

- **Assumptions:** ALWAYS verify statistical assumptions (e.g., Normality) before applying tests (e.g., T-Test).
- **Reporting:** Report effect sizes (e.g., Cohen's d) alongside p-values. Statistical significance != Practical significance.
    </standards>

\<forbidden_patterns>

- ❌ **Ignoring Nodata:** You MUST NOT silently calculate statistics over arrays containing raw nodata values (e.g., averaging `-9999` with valid data). Use `xarray.where()` or masked arrays.
- ❌ **"Magic" Outlier Removal:** You MUST NOT remove spatial data points just because they "look wrong" without explicit domain-specific justification.
- ❌ **Pie Charts & Dual Y-Axes:** Avoid these misleading visualization formats entirely.
    \</forbidden_patterns>
