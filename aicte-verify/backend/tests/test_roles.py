"""Unit tests for Role-Based Access Control (RBAC) and security safeguards."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token, mask_pii
from app.models.user import User


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        # Seed test users for each role
        admin_user = User(
            id=1,
            username="admin_test",
            email="admin@test.gov.in",
            hashed_password=hash_password("admin123"),
            full_name="Admin Test",
            role="admin",
            region="All",
            is_active=True,
        )
        officer_user = User(
            id=2,
            username="officer_test",
            email="officer@test.gov.in",
            hashed_password=hash_password("officer123"),
            full_name="Officer Test",
            role="officer",
            region="West",
            is_active=True,
        )
        college_user = User(
            id=3,
            username="college_test",
            email="college@test.edu",
            hashed_password=hash_password("college123"),
            full_name="College Test",
            role="college_user",
            region="West",
            is_active=True,
        )
        session.add_all([admin_user, officer_user, college_user])
        await session.commit()
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_role_access_control(client: AsyncClient):
    """Test role isolation: College users and officers cannot access admin routes."""
    # Generate tokens
    admin_token = create_access_token({"sub": "admin_test", "role": "admin"})
    officer_token = create_access_token({"sub": "officer_test", "role": "officer"})
    college_token = create_access_token({"sub": "college_test", "role": "college_user"})

    # 1. College user trying to access admin audit route -> 403 Forbidden
    resp = await client.get(
        "/api/v1/audit/",
        headers={"Authorization": f"Bearer {college_token}"}
    )
    assert resp.status_code == 403

    # 2. Officer trying to access admin users route -> 403 Forbidden
    resp = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert resp.status_code == 403

    # 3. Admin accessing admin users route -> 200 OK
    resp = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200

    # 4. Unauthenticated request -> 401 Unauthorized
    resp = await client.get("/api/v1/audit/")
    assert resp.status_code == 401


def test_pii_masking():
    """Test masking of sensitive Aadhaar and phone numbers."""
    raw_text = "Principal Aadhaar: 9876 5432 1098, Phone: 9876543210, Alternate: +91 9123456789"
    masked = mask_pii(raw_text)

    # Aadhaar should be masked showing only last 4 digits
    assert "XXXX-XXXX-1098" in masked
    assert "9876 5432 1098" not in masked

    # Phone should be masked showing only last 4 digits
    assert "XXXXXX3210" in masked
    assert "9876543210" not in masked
