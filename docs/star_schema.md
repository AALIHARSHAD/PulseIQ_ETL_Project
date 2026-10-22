# PulseIQ Star Schema

## Dimension tables

- `dim_date` — Date and calendar attributes.
- `dim_employee` — Employee details and employment history.
- `dim_department` — Department details.
- `dim_role` — Role and grade details.
- `dim_location` — Work location details.
- `dim_leave_type` — Leave type and policy details.

## Fact tables and dimension relationships

```mermaid
flowchart TD
    DATE[dim_date]
    EMP[dim_employee]
    DEPT[dim_department]
    ROLE[dim_role]
    LOC[dim_location]
    LEAVE_TYPE[dim_leave_type]

    PAY[fact_payroll]
    ATT[fact_attendance_monthly]
    LEAVE[fact_leave]
    HC[fact_headcount_monthly]

    DATE -->|date_key| PAY
    EMP -->|employee_key| PAY
    DEPT -->|department_id| PAY
    ROLE -->|role_id| PAY

    DATE -->|date_key| ATT
    EMP -->|employee_key| ATT
    DEPT -->|department_id| ATT

    EMP -->|employee_key| LEAVE
    LEAVE_TYPE -->|leave_type_code| LEAVE

    DATE -->|date_key| HC
    DEPT -->|department_id| HC

    DEPT -->|department_id| EMP
    ROLE -->|role_id| EMP
    LOC -->|work_location| EMP
    DEPT -->|department_id| ROLE
```

## Validation summary

- All 6 dimension tables and 4 fact tables are loaded.
- Primary key uniqueness and null checks passed for all 10 tables.
- Employee orphan checks returned zero orphan records.
- All 14 additional dimension reference checks passed.
- Fact row counts reconcile with the ETL-cleaned Parquet files.
