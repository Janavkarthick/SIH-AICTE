"""
AICTE-Verify Database Seeder
=============================
Idempotently wipes and re-seeds database with 18 synthetic applications across
6 institutions and 3 academic years (2024-2025, 2025-2026, 2026-2027).
Runs generate_synthetic.py if synthetic data doesn't exist.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

async def seed_async():
    print("=" * 60)
    print("AICTE-Verify Database Seeder (Idempotent Wipe & Re-seed)")
    print("=" * 60)

    # Step 1: Generate synthetic data if not exists
    synthetic_dir = PROJECT_ROOT / "data" / "synthetic"
    ground_truth_path = synthetic_dir / "ground_truth.json"

    if not ground_truth_path.exists():
        print("\nSynthetic data not found. Generating...")
        sys.path.insert(0, str(SCRIPT_DIR))
        from generate_synthetic import main as generate_main
        generate_main()
    else:
        print("\nSynthetic data verified.")

    # Step 2: Initialize DB and run idempotent seed
    print("\nInitializing database schema...")
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'data' / 'aicte_verify.db'}")
    os.environ.setdefault("JWT_SECRET_KEY", "aicte-verify-development-super-secret-jwt-key-2024")

    from app.core.database import init_db, AsyncSessionLocal
    from app.seed.seed_db import seed_database

    await init_db(drop=True)
    print("Tables re-created fresh.")

    async with AsyncSessionLocal() as session:
        await seed_database(session, wipe=False)

    print("\nDatabase seeded successfully!")
    print("  - Total Institutions: 6")
    print("  - Total Applications: 18 (across 6 institutions and 3 academic years: 2024-2025, 2025-2026, 2026-2027)")
    print("  - Discrepancy Flags: Active and fresh (zero resolved flags)")
    print("\nDemo Credentials:")
    print("  admin / admin123       - System Admin (Central)")
    print("  officer1 / officer123  - Regional Officer (South)")
    print("  officer2 / officer123  - Regional Officer (North)")
    print("  college1 / college123  - College User (Apex Tech)")
    print("  college2 / college123  - College User (Zenith Engg)")


def main():
    asyncio.run(seed_async())


if __name__ == "__main__":
    main()
