from database import Database

tables = [
    ("nodes","""
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        id VARCHAR(36),
        PRIMARY KEY (timestamp, id),
        hostname VARCHAR(255),
        os_name VARCHAR(40),
        os_version VARCHAR(40),
        softwares int,
        software_updates int,
        software_security_updates int,
        critical_cves int,
        high_cves int,
        compliance INT,
        success_already_ok FLOAT,     
        success_repaired FLOAT,
        success_not_applicable FLOAT,
        audit_compliant FLOAT,
        audit_non_compliant FLOAT,
        audit_not_applicable FLOAT,
        error FLOAT,
        no_report FLOAT
    """),
    ("campaigns","""
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        campaign_type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        frequency VARCHAR(50) NOT NULL
    """),
    ("campaignEvents","""
        id VARCHAR(36) PRIMARY KEY,
        campaign_id VARCHAR(255) NOT NULL,
        name VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        start_date VARCHAR(255) NOT NULL,
        end_date VARCHAR(255) NOT NULL,
        updated_nodes INT,
        failed_nodes INT,
        updated_pkg INT,
        failed_pkg INT
    """),
    ("globalCompliance","""
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
        global_compliance INT NOT NULL,
        success_already_ok FLOAT,
        success_not_applicable FLOAT,
        audit_compliant FLOAT,
        audit_non_compliant FLOAT,
        error FLOAT,
        success_repaired FLOAT,
        audit_not_applicable FLOAT
    """),
    ("cves","""
        cve_id VARCHAR(36) PRIMARY KEY,
        severity VARCHAR(50),
        first_appearance TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_presence_check TIMESTAMP
     """),
    ("rules","""
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        id VARCHAR(36),
        PRIMARY KEY (timestamp, id),
        name VARCHAR(255),
        compliance INT NOT NULL,
        success_already_ok FLOAT,
        success_not_applicable FLOAT,
        audit_compliant FLOAT,
        audit_non_compliant FLOAT,
        error FLOAT,
        success_repaired FLOAT,
        audit_not_applicable FLOAT
     """),
    ("nodesInRules","""
        id VARCHAR(36),
        rule_id VARCHAR(36),
        PRIMARY KEY (id, rule_id),
        hostname VARCHAR(255),
        compliance INT NOT NULL,
        success_already_ok FLOAT,
        success_not_applicable FLOAT,
        audit_compliant FLOAT,
        audit_non_compliant FLOAT,
        error FLOAT,
        success_repaired FLOAT,
        audit_not_applicable FLOAT
     """),
    ("directives","""
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        id VARCHAR(255),
        PRIMARY KEY (timestamp, id),
        name TEXT,
        compliance INT NOT NULL,
        success_already_ok FLOAT,
        success_not_applicable FLOAT,
        success_repaired FLOAT,
        audit_compliant FLOAT,
        audit_non_compliant FLOAT,
        audit_not_applicable FLOAT,
        error FLOAT,
        no_report FLOAT
    """)
    ]

d = Database(create_db=True)

for table_name, table_schema in tables:
    d.create_table(table_name, table_schema)