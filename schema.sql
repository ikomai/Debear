-- ─────────────────────────────────────────────────────────────
-- MySQL schema for the real-estate insurance bot.
-- Run this in MySQL Workbench against your own database
-- if you prefer to create the tables manually.
-- The bot also creates these tables automatically on first run.
-- ─────────────────────────────────────────────────────────────
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id  BIGINT NOT NULL UNIQUE,
    username     VARCHAR(64),
    full_name    VARCHAR(255),
    phone        VARCHAR(32),
    email        VARCHAR(255),
    role         VARCHAR(16) DEFAULT 'client',
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS applications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    number          VARCHAR(32) NOT NULL UNIQUE,
    status          VARCHAR(32) DEFAULT 'submitted',
    property_type   VARCHAR(32),
    purpose         VARCHAR(32),
    insured_sum     DECIMAL(15,2),
    term_months     INT,
    has_mortgage    TINYINT(1) DEFAULT 0,
    bank            VARCHAR(255),
    contract_number VARCHAR(64),
    contract_date   VARCHAR(32),
    debt_balance    VARCHAR(64),
    coverage        JSON,
    risks           JSON,
    extra           JSON,
    consent         TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS property (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    application_id   INT NOT NULL,
    country          VARCHAR(128),
    region           VARCHAR(128),
    city             VARCHAR(128),
    street           VARCHAR(255),
    house            VARCHAR(32),
    building         VARCHAR(32),
    apartment        VARCHAR(32),
    postal_code      VARCHAR(32),
    year_built       VARCHAR(16),
    floors_total     VARCHAR(16),
    floor            VARCHAR(16),
    total_area       VARCHAR(32),
    living_area      VARCHAR(32),
    wall_material    VARCHAR(128),
    ceiling_material VARCHAR(128),
    renovation       VARCHAR(32),
    value            VARCHAR(64),
    cadastral_number VARCHAR(64),
    CONSTRAINT fk_prop_app FOREIGN KEY (application_id) REFERENCES applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS owners (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    application_id      INT NOT NULL,
    full_name           VARCHAR(255),
    birth_date          VARCHAR(32),
    gender              VARCHAR(16),
    phone               VARCHAR(32),
    email               VARCHAR(255),
    inn                 VARCHAR(32),
    passport_series     VARCHAR(16),
    passport_number     VARCHAR(16),
    passport_issued_by  TEXT,
    passport_issue_date VARCHAR(32),
    CONSTRAINT fk_owner_app FOREIGN KEY (application_id) REFERENCES applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS documents (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    doc_type       VARCHAR(64),
    file_id        VARCHAR(255),
    file_path      VARCHAR(512),
    uploaded_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_doc_app FOREIGN KEY (application_id) REFERENCES applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS history (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    old_status     VARCHAR(32),
    new_status     VARCHAR(32),
    changed_by     BIGINT,
    comment        TEXT,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_app FOREIGN KEY (application_id) REFERENCES applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
