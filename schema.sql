CREATE TABLE donations_raw (
    payment_id        BIGINT PRIMARY KEY,
    school_id         BIGINT,
    school_name       TEXT,
    school_location   TEXT,

    donor_name        TEXT,
    donor_email       TEXT,
    donor_phone       TEXT,
    donor_type        TEXT,
    donor_gender      TEXT,
    donor_location    TEXT,

    donation_type     TEXT,
    campaign_name     TEXT,

    payment_mode      TEXT,
    payment_status    TEXT,

    amount            INTEGER,

    payment_date      TIMESTAMP,
    transaction_id    TEXT,
    notes             TEXT,

    created_at        TIMESTAMP DEFAULT NOW()
);
