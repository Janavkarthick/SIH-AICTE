"""Unit tests for cryptographic append-only audit trail."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.audit import AuditLogger, compute_canonical_json, compute_entry_hash, verify_chain
from app.core.database import Base


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_audit_hash_chain_integrity(test_db):
    """Test that consecutive audit entries form an unbroken cryptographic chain."""
    entry1 = await AuditLogger.log(
        db=test_db,
        action="TEST_ACTION_1",
        actor_id=1,
        actor_username="test_admin",
        details={"detail": "first"},
    )
    assert entry1.previous_hash == "0" * 64
    assert len(entry1.entry_hash) == 64

    entry2 = await AuditLogger.log(
        db=test_db,
        action="TEST_ACTION_2",
        actor_id=1,
        actor_username="test_admin",
        details={"detail": "second"},
    )
    assert entry2.previous_hash == entry1.entry_hash

    # Verify chain passes
    verification = await verify_chain(test_db)
    assert verification["valid"] is True
    assert verification["verified_count"] == 2
    assert verification["tampered_entry_id"] is None


@pytest.mark.asyncio
async def test_audit_hash_chain_tamper_detection(test_db):
    """Test that tampering with an audit entry invalidates the chain."""
    entry1 = await AuditLogger.log(
        db=test_db,
        action="CREATION",
        actor_id=1,
        actor_username="admin",
        details={"payload": "original"},
    )
    entry2 = await AuditLogger.log(
        db=test_db,
        action="APPROVAL",
        actor_id=2,
        actor_username="officer1",
        details={"payload": "approved"},
    )

    # Tamper with entry1's action
    entry1.action = "TAMPERED_ACTION"
    await test_db.commit()

    # Verification must fail and identify the tampered entry
    verification = await verify_chain(test_db)
    assert verification["valid"] is False
    assert verification["tampered_entry_id"] == entry1.id

