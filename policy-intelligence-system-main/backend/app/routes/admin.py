from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.auth import require_admin, log_activity, hash_password
from app.database import get_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────
class RoleUpdate(BaseModel):
    role: str


class CreateAdminUser(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = "Admin User"


class CreateTrustedSource(BaseModel):
    name: str
    url: str
    source_type: Optional[str] = "web_scraper"
    description: Optional[str] = ""
    country: Optional[str] = "Global"
    sector: Optional[str] = "All"


class UpdateSourceStatus(BaseModel):
    status: str


class CreateCustomSector(BaseModel):
    name: str
    description: Optional[str] = ""
    color: Optional[str] = "#64748b"
    keywords: Optional[str] = ""


class UpdateCustomSector(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[str] = None


# Built-in sectors that cannot be deleted
BUILTIN_SECTORS = [
    "AI Governance", "Cybersecurity", "Data Privacy",
    "Healthcare AI", "Financial Regulation",
    "POSH Policies", "ESG Policies", "IoT and Robotics"
]


# ── System Stats ───────────────────────────────────────────────────────────
@router.get("/stats")
def admin_stats(admin: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_admins = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
        total_policies = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]
        total_uploads = conn.execute("SELECT COUNT(*) FROM user_uploads").fetchone()[0]
        total_compares = conn.execute("SELECT COUNT(*) FROM user_compares").fetchone()[0]
        total_generates = conn.execute("SELECT COUNT(*) FROM user_generates").fetchone()[0]
        total_feedback = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]

        active_24h = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM activity_logs WHERE created_at > NOW() - INTERVAL '24 hours'"
        ).fetchone()[0]

        active_7d = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM activity_logs WHERE created_at > NOW() - INTERVAL '7 days'"
        ).fetchone()[0]

        # Recent registrations (last 7 days)
        new_users_7d = conn.execute(
            "SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '7 days'"
        ).fetchone()[0]

        # User growth per day (last 14 days)
        growth_rows = conn.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM users
            WHERE created_at > NOW() - INTERVAL '14 days'
            GROUP BY DATE(created_at)
            ORDER BY day
        """).fetchall()
        user_growth = [{"day": str(r[0]), "count": r[1]} for r in growth_rows]

        # Activity per day (last 14 days)
        activity_rows = conn.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM activity_logs
            WHERE created_at > NOW() - INTERVAL '14 days'
            GROUP BY DATE(created_at)
            ORDER BY day
        """).fetchall()
        activity_trend = [{"day": str(r[0]), "count": r[1]} for r in activity_rows]

        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_policies": total_policies,
            "total_uploads": total_uploads,
            "total_compares": total_compares,
            "total_generates": total_generates,
            "total_feedback": total_feedback,
            "active_24h": active_24h,
            "active_7d": active_7d,
            "new_users_7d": new_users_7d,
            "user_growth": user_growth,
            "activity_trend": activity_trend,
        }
    finally:
        conn.close()


# ── User Management ────────────────────────────────────────────────────────
@router.get("/users")
def admin_users(
    search: str = "",
    role: str = "",
    sort: str = "created_at",
    order: str = "desc",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: dict = Depends(require_admin)
):
    conn = get_connection()
    try:
        conditions = []
        params = []

        if search:
            conditions.append("(LOWER(email) LIKE %s OR LOWER(full_name) LIKE %s)")
            params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

        if role:
            conditions.append("role = %s")
            params.append(role)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Validate sort column
        valid_sorts = {"created_at", "email", "full_name", "role"}
        if sort not in valid_sorts:
            sort = "created_at"
        sort_dir = "DESC" if order.lower() == "desc" else "ASC"

        # Count total
        count_row = conn.execute(
            f"SELECT COUNT(*) FROM users {where_clause}", params
        ).fetchone()
        total = count_row[0]

        # Fetch paginated users
        offset = (page - 1) * limit
        rows = conn.execute(
            f"""SELECT id, email, full_name, role, created_at
                FROM users {where_clause}
                ORDER BY {sort} {sort_dir}
                LIMIT %s OFFSET %s""",
            params + [limit, offset]
        ).fetchall()

        users = []
        for r in rows:
            u = dict(r)
            # Get last activity timestamp
            last_active = conn.execute(
                "SELECT created_at FROM activity_logs WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                (u["id"],)
            ).fetchone()
            u["last_active"] = str(last_active[0]) if last_active else None
            users.append(u)

        return {
            "users": users,
            "total": total,
            "page": page,
            "pages": max(1, (total + limit - 1) // limit),
        }
    finally:
        conn.close()


@router.get("/users/{user_id}")
def admin_user_detail(user_id: int, admin: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT id, email, full_name, role, created_at FROM users WHERE id = %s",
            (user_id,)
        ).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_dict = dict(user)

        # Get activity history
        activities = conn.execute(
            "SELECT action, detail, ip_address, created_at FROM activity_logs WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
            (user_id,)
        ).fetchall()
        user_dict["activities"] = [dict(a) for a in activities]

        # Get counts
        user_dict["upload_count"] = conn.execute(
            "SELECT COUNT(*) FROM user_uploads WHERE user_id = %s", (user_id,)
        ).fetchone()[0]
        user_dict["compare_count"] = conn.execute(
            "SELECT COUNT(*) FROM user_compares WHERE user_id = %s", (user_id,)
        ).fetchone()[0]
        user_dict["generate_count"] = conn.execute(
            "SELECT COUNT(*) FROM user_generates WHERE user_id = %s", (user_id,)
        ).fetchone()[0]

        return user_dict
    finally:
        conn.close()


@router.put("/users/{user_id}/role")
def admin_update_role(
    user_id: int,
    body: RoleUpdate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    if body.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")

    # Prevent admin from demoting themselves
    if user_id == admin["id"] and body.role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own admin role")

    conn = get_connection()
    try:
        target = conn.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")

        conn.execute("UPDATE users SET role = %s WHERE id = %s", (body.role, user_id))
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "role_change",
            f"Changed user {target['email']} role from {target['role']} to {body.role}",
            request.client.host if request.client else ""
        )

        return {"message": f"User role updated to '{body.role}'"}
    finally:
        conn.close()


@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    # Prevent self-deletion
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")

    conn = get_connection()
    try:
        target = conn.execute("SELECT id, email FROM users WHERE id = %s", (user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")

        conn.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "user_delete",
            f"Deleted user {target['email']} (id={user_id})",
            request.client.host if request.client else ""
        )

        return {"message": f"User {target['email']} deleted"}
    finally:
        conn.close()


@router.put("/users/{user_id}/block")
def admin_block_user(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Block a user by setting their role to 'blocked'."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot block your own admin account")

    conn = get_connection()
    try:
        target = conn.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")

        new_role = "blocked" if target["role"] != "blocked" else "user"
        conn.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()

        action = "user_block" if new_role == "blocked" else "user_unblock"
        log_activity(
            admin["id"], admin["email"], action,
            f"{'Blocked' if new_role == 'blocked' else 'Unblocked'} user {target['email']}",
            request.client.host if request.client else ""
        )

        return {"message": f"User {'blocked' if new_role == 'blocked' else 'unblocked'}", "new_role": new_role}
    finally:
        conn.close()


@router.post("/create-admin")
def admin_create_admin(
    body: CreateAdminUser,
    request: Request,
    admin: dict = Depends(require_admin)
):
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    if not body.password or len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id, email, role FROM users WHERE email = %s", (email,)).fetchone()
        if existing:
            if existing["role"] == "admin":
                raise HTTPException(status_code=400, detail=f"User {email} is already an admin")
            
            pwd_hash = hash_password(body.password)
            conn.execute(
                "UPDATE users SET role = 'admin', password_hash = %s WHERE id = %s",
                (pwd_hash, existing["id"])
            )
            conn.commit()

            log_activity(
                admin["id"], admin["email"], "create_admin",
                f"Promoted existing user {email} to admin and updated password",
                request.client.host if request.client else ""
            )
            return {"message": f"User {email} successfully allocated as admin", "user_id": existing["id"]}
        else:
            pwd_hash = hash_password(body.password)
            full_name = body.full_name.strip() if body.full_name else "Admin User"
            
            res = conn.execute(
                "INSERT INTO users (email, password_hash, full_name, role) VALUES (%s, %s, %s, %s) RETURNING id",
                (email, pwd_hash, full_name, "admin")
            ).fetchone()
            conn.commit()

            new_id = res[0]
            log_activity(
                admin["id"], admin["email"], "create_admin",
                f"Created new admin account for {email}",
                request.client.host if request.client else ""
            )
            return {"message": f"New admin account for {email} created successfully", "user_id": new_id}
    finally:
        conn.close()


# ── Activity Logs ──────────────────────────────────────────────────────────
@router.get("/activity")
def admin_activity(
    action: str = "",
    user_email: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    admin: dict = Depends(require_admin)
):
    conn = get_connection()
    try:
        conditions = []
        params = []

        if action:
            conditions.append("action = %s")
            params.append(action)

        if user_email:
            conditions.append("LOWER(user_email) LIKE %s")
            params.append(f"%{user_email.lower()}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        total = conn.execute(
            f"SELECT COUNT(*) FROM activity_logs {where_clause}", params
        ).fetchone()[0]

        offset = (page - 1) * limit
        rows = conn.execute(
            f"""SELECT id, user_id, user_email, action, detail, ip_address, created_at
                FROM activity_logs {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s""",
            params + [limit, offset]
        ).fetchall()

        # Get distinct action types for filter dropdown
        action_types = conn.execute(
            "SELECT DISTINCT action FROM activity_logs ORDER BY action"
        ).fetchall()

        return {
            "logs": [dict(r) for r in rows],
            "total": total,
            "page": page,
            "pages": max(1, (total + limit - 1) // limit),
            "action_types": [r[0] for r in action_types],
        }
    finally:
        conn.close()


# ── System Health ──────────────────────────────────────────────────────────
@router.get("/system")
def admin_system(admin: dict = Depends(require_admin)):
    result = {
        "database": "unknown",
        "ml_status": None,
        "scheduler": "unknown",
        "policy_by_sector": [],
        "policy_by_region": [],
    }

    conn = get_connection()
    try:
        conn.execute("SELECT 1")
        result["database"] = "connected"

        # Policy breakdown by sector
        sector_rows = conn.execute(
            "SELECT sector, COUNT(*) as count FROM policies GROUP BY sector ORDER BY count DESC"
        ).fetchall()
        result["policy_by_sector"] = [{"sector": r[0], "count": r[1]} for r in sector_rows]

        # Policy breakdown by region
        region_rows = conn.execute(
            "SELECT region, COUNT(*) as count FROM policies GROUP BY region ORDER BY count DESC"
        ).fetchall()
        result["policy_by_region"] = [{"region": r[0], "count": r[1]} for r in region_rows]

    except Exception as e:
        result["database"] = f"error: {str(e)}"
    finally:
        conn.close()

    # ML status
    try:
        from app.ml.recommender_v2 import recommender
        result["ml_status"] = {
            "fitted": recommender.fitted,
            "countries": len(recommender.country_embeddings) if hasattr(recommender, 'country_embeddings') else 0,
        }
    except Exception:
        result["ml_status"] = {"fitted": False, "countries": 0}

    return result


# ── Admin Policy Delete ────────────────────────────────────────────────────
@router.delete("/policies/{policy_id}")
def admin_delete_policy(
    policy_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id, title FROM policies WHERE id = %s", (policy_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Policy not found")

        conn.execute("DELETE FROM policies WHERE id = %s", (policy_id,))
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "policy_delete",
            f"Deleted policy: {existing['title']} (id={policy_id})",
            request.client.host if request.client else ""
        )

        return {"message": f"Policy '{existing['title']}' deleted"}
    finally:
        conn.close()


# ── Trusted Domain Sources (Pipeline Expansion) ───────────────────────────
@router.get("/trusted-sources")
def get_trusted_sources(admin: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT id, name, url, source_type, description, country, sector, status, created_at, last_crawled_at, policies_fetched
            FROM trusted_sources
            ORDER BY id ASC
        """).fetchall()
        return {"sources": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.post("/trusted-sources")
def create_trusted_source(
    body: CreateTrustedSource,
    request: Request,
    admin: dict = Depends(require_admin)
):
    url = body.url.strip()
    name = body.name.strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=400, detail="Valid HTTP/HTTPS URL is required")
    if not name:
        raise HTTPException(status_code=400, detail="Source name is required")

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM trusted_sources WHERE url = %s", (url,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="A trusted source with this URL already exists")

        res = conn.execute("""
            INSERT INTO trusted_sources (name, url, source_type, description, country, sector)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, url, source_type, description, country, sector, status, created_at
        """, (
            name, url, body.source_type or "web_scraper",
            body.description or "", body.country or "Global", body.sector or "All"
        )).fetchone()
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "add_trusted_source",
            f"Added new policy source link: {name} ({url})",
            request.client.host if request.client else ""
        )
        return {"message": f"Trusted source '{name}' added successfully", "source": dict(res)}
    finally:
        conn.close()


@router.put("/trusted-sources/{source_id}/status")
def update_trusted_source_status(
    source_id: int,
    body: UpdateSourceStatus,
    request: Request,
    admin: dict = Depends(require_admin)
):
    new_status = body.status if body.status in ["Active", "Disabled"] else "Active"
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id, name FROM trusted_sources WHERE id = %s", (source_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Trusted source not found")

        conn.execute("UPDATE trusted_sources SET status = %s WHERE id = %s", (new_status, source_id))
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "update_source_status",
            f"Set status of source '{existing['name']}' to {new_status}",
            request.client.host if request.client else ""
        )
        return {"message": f"Source status updated to {new_status}"}
    finally:
        conn.close()


@router.delete("/trusted-sources/{source_id}")
def delete_trusted_source(
    source_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id, name, url FROM trusted_sources WHERE id = %s", (source_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Trusted source not found")

        conn.execute("DELETE FROM trusted_sources WHERE id = %s", (source_id,))
        conn.commit()

        log_activity(
            admin["id"], admin["email"], "delete_trusted_source",
            f"Removed trusted domain source: {existing['name']}",
            request.client.host if request.client else ""
        )
        return {"message": f"Trusted source '{existing['name']}' deleted successfully"}
    finally:
        conn.close()


@router.post("/trusted-sources/{source_id}/test")
def test_trusted_source_crawl(
    source_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    conn = get_connection()
    try:
        source = conn.execute(
            "SELECT id, name, url, source_type, description, country, sector FROM trusted_sources WHERE id = %s",
            (source_id,)
        ).fetchone()
        if not source:
            raise HTTPException(status_code=404, detail="Trusted source not found")
        source_dict = dict(source)
    finally:
        conn.close()

    try:
        from app.services.policy_fetcher import test_crawl_source
        extracted = test_crawl_source(source_dict)
        return {
            "message": f"Crawl test completed for '{source_dict['name']}'",
            "extracted_count": len(extracted),
            "sample_policies": extracted[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl test failed: {str(e)}")


# ── Custom Sectors Management ──────────────────────────────────────────────

@router.get("/sectors")
def get_all_sectors(admin: dict = Depends(require_admin)):
    """Return built-in sectors + custom sectors from DB."""
    builtin = [
        {"id": None, "name": s, "description": "System default sector", "color": "", "keywords": "", "status": "Active", "is_builtin": True}
        for s in BUILTIN_SECTORS
    ]
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, description, color, keywords, status, created_at FROM custom_sectors ORDER BY created_at DESC"
        ).fetchall()
        custom = [
            {**dict(r), "is_builtin": False, "created_at": str(r["created_at"]) if r["created_at"] else None}
            for r in rows
        ]
        return builtin + custom
    finally:
        conn.close()


@router.post("/sectors")
def create_custom_sector(
    data: CreateCustomSector,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Add a new custom sector."""
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Sector name is required")

    # Cannot duplicate a built-in sector
    if name in BUILTIN_SECTORS:
        raise HTTPException(status_code=409, detail=f"'{name}' is a built-in system sector and cannot be re-created")

    conn = get_connection()
    try:
        # Check for duplicate custom sector
        existing = conn.execute("SELECT id FROM custom_sectors WHERE LOWER(name) = LOWER(%s)", (name,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail=f"A custom sector named '{name}' already exists")

        conn.execute(
            "INSERT INTO custom_sectors (name, description, color, keywords) VALUES (%s, %s, %s, %s)",
            (name, data.description or "", data.color or "#64748b", data.keywords or "")
        )
        conn.commit()

        log_activity(
            conn, admin["id"], admin["email"], "sector_create",
            f"Created custom sector: {name}",
            request.client.host if request.client else ""
        )
        return {"message": f"Custom sector '{name}' created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sector: {str(e)}")
    finally:
        conn.close()


@router.put("/sectors/{sector_id}")
def update_custom_sector(
    sector_id: int,
    data: UpdateCustomSector,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update a custom sector's details."""
    conn = get_connection()
    try:
        existing = conn.execute("SELECT * FROM custom_sectors WHERE id = %s", (sector_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Custom sector not found")

        updates = []
        params = []
        if data.name is not None:
            new_name = data.name.strip()
            if new_name in BUILTIN_SECTORS:
                raise HTTPException(status_code=409, detail=f"Cannot rename to built-in sector name '{new_name}'")
            updates.append("name = %s")
            params.append(new_name)
        if data.description is not None:
            updates.append("description = %s")
            params.append(data.description)
        if data.color is not None:
            updates.append("color = %s")
            params.append(data.color)
        if data.keywords is not None:
            updates.append("keywords = %s")
            params.append(data.keywords)
        if data.status is not None:
            updates.append("status = %s")
            params.append(data.status)

        if not updates:
            return {"message": "No changes provided"}

        params.append(sector_id)
        conn.execute(f"UPDATE custom_sectors SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()

        log_activity(
            conn, admin["id"], admin["email"], "sector_update",
            f"Updated custom sector ID {sector_id}: {existing['name']}",
            request.client.host if request.client else ""
        )
        return {"message": f"Sector '{existing['name']}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update sector: {str(e)}")
    finally:
        conn.close()


@router.delete("/sectors/{sector_id}")
def delete_custom_sector(
    sector_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a custom sector (built-in sectors cannot be deleted)."""
    conn = get_connection()
    try:
        existing = conn.execute("SELECT * FROM custom_sectors WHERE id = %s", (sector_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Custom sector not found (built-in sectors cannot be deleted)")

        conn.execute("DELETE FROM custom_sectors WHERE id = %s", (sector_id,))
        conn.commit()

        log_activity(
            conn, admin["id"], admin["email"], "sector_delete",
            f"Deleted custom sector: {existing['name']}",
            request.client.host if request.client else ""
        )
        return {"message": f"Sector '{existing['name']}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete sector: {str(e)}")
    finally:
        conn.close()
