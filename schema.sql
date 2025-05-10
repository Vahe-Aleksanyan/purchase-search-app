CREATE TABLE IF NOT EXISTS purchases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code  TEXT NOT NULL,
    product_name  TEXT NOT NULL,
    supplier      TEXT NOT NULL,
    date          TEXT NOT NULL,
    qty           REAL NOT NULL,
    unit          TEXT,
    price         REAL,
    total_price   REAL,
    source_file   TEXT,
    UNIQUE(product_code, date, supplier)
);


CREATE VIRTUAL TABLE IF NOT EXISTS purchases_fts
USING fts5(product_name, content='purchases', content_rowid='id');
