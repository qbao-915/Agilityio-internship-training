# Day 7: Simple Database Schema Design & Practice

An introductory laboratory exercise focused on relational database modeling, schema integrity, constraints mapping, and automation scripting using SQL and Python.

## 🛠️ Project Structure
```text
Day-7-Simple-Schema/
├── Sample.sql      # Handwritten DDL & DML script containing table blueprints and seed data
├── main.py         # Automation script leveraging SQLite to initialize schemas and query records
└── README.md       # Implementation notes and execution documentation
```

## 📋 Objectives & Core Learnings
* **Relational Schema Modeling:** Designed a standard 1-to-Many ($1 
ightarrow N$) parent-child architecture linking project groups (`teams`) directly to individual practitioners (`members`).
* **Operational Constraint Control:** Handcrafted strict table field properties utilizing primary indicators (`PRIMARY KEY`), database-driven sequential counters (`AUTOINCREMENT`), null-value exclusions (`NOT NULL`), uniqueness enforcements (`UNIQUE`), and default fallback hooks (`DEFAULT CURRENT_DATE`).
* **Referential Data Integrity:** Implemented foreign key constraints (`FOREIGN KEY REFERENCES`) to ensure structural consistency and prevent orphaned data strings across connected rows.
* **Driver Automation:** Automated environment setup, table construction, and validation rendering pipelines natively via Python's embedded `sqlite3` API wrapper.

## 🚀 Execution & Verification
To initialize the physical database, seed validation metrics, and query logs onto your local workstation, go to the folder `exercises/Day-7-Simple-Schema` and run the orchestrator script:

```bash
python main.py
```