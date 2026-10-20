# PulseIQ Star Schema

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
