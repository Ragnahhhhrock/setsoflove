-- Optional lift stats. Always stored in kilograms (one decimal place); weight_unit is the member's display choice.
ALTER TABLE profiles ADD COLUMN bench_kg REAL;
ALTER TABLE profiles ADD COLUMN squat_kg REAL;
ALTER TABLE profiles ADD COLUMN deadlift_kg REAL;
ALTER TABLE profiles ADD COLUMN ohp_kg REAL;
ALTER TABLE profiles ADD COLUMN weight_unit TEXT NOT NULL DEFAULT 'kg' CHECK (weight_unit IN ('kg','lb'));
