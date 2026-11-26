## PROJECTS

### End-to-End E-Commerce Data Engineering Pipeline
**Project Type:** Independent Portfolio Project  
**Technologies:** Python, AWS S3, Databricks, PySpark, SQL, Streamlit, Plotly, GitHub

**Project Description:**

Designed and developed an end-to-end e-commerce data engineering pipeline to ingest, store, process, transform, and analyze business data. Implemented a Medallion Architecture using Databricks and PySpark and developed an interactive dashboard to visualize sales performance.

**Responsibilities & Implementation:**

- **Data Ingestion:** Developed Python scripts to ingest data from CSV files and REST APIs. Implemented API pagination to retrieve records across multiple pages.
- **Incremental Loading:** Implemented incremental data ingestion using watermark-based logic to identify and process newly updated records.
- **Cloud Storage:** Configured Amazon S3 to store raw and incremental source data.
- **Bronze Layer:** Loaded raw CSV and JSON data into Databricks Bronze tables.
- **Silver Layer:** Used PySpark for data cleaning, data type conversion, null handling, deduplication, and transformations.
- **Gold Layer:** Created analytical fact and dimension tables to support business reporting.
- **Data Modeling:** Designed fact and dimension tables for customers, products, dates, and sales analysis.
- **SQL Analytics:** Developed SQL queries and an enriched orders view by joining fact and dimension tables.
- **Dashboard Development:** Built an interactive Streamlit dashboard using Plotly with KPI cards, sales trends, category analysis, market comparisons, and interactive filters.
- **Deployment:** Published the dashboard using Streamlit Community Cloud and maintained project source code in GitHub.

**Project Links:**

GitHub: https://github.com/srihari978/ecommerce-data-engineering-

Live Dashboard: https://atliqondata.streamlit.app/
