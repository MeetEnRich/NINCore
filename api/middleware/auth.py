"""
NINCore API — Authentication Middleware
=========================================
Validates the API key passed in the X-API-Key request header
against the API_Keys table in the database.

Every protected route depends on get_verified_agency(), which:
  1. Extracts the X-API-Key header
  2. Queries the API_Keys table for a matching Active key
  3. Stamps Last_Used on the key row
  4. Returns the APIKey ORM object so the route knows which
     agency and sector is making the request

Usage in a route:
    from api.middleware.auth import get_verified_agency
    from database.models import APIKey

    @router.post("/some-route")
    def route(agency: APIKey = Depends(get_verified_agency)):
        print(agency.Sector_Name)
"""

import logging
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from database.db import get_db
from database import crud
from database.models import APIKey

logger = logging.getLogger(__name__)

# FastAPI's built-in API key extractor — reads X-API-Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


import bcrypt

def get_verified_agency(
    api_key: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> APIKey:
    """
    FastAPI dependency. Validates X-API-Key header.

    Raises:
        401 — header missing or malformed
        403 — key not found, revoked, or incorrect secret

    Returns:
        APIKey ORM object for the authenticated agency
    """
    if not api_key:
        logger.warning("Request received with no API key header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header. "
                   "All NINCore API endpoints require authentication.",
        )

    # Expecting AgencyID:Secret format
    parts = api_key.split(":", 1)
    if len(parts) != 2:
        logger.warning("Malformed API key format attempted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Expected format is AgencyID:Secret",
        )
    
    agency_id, secret = parts
    
    # Fast O(1) lookup by Agency_ID
    key_record = crud.apikey.get_by_agency(db, agency_id=agency_id)

    if not key_record or key_record.Status != "Active":
        logger.warning("Agency ID not found or revoked: %s", agency_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or revoked API key. "
                   "Contact the NINCore administrator.",
        )

    # Secure verification
    try:
        is_valid = bcrypt.checkpw(secret.encode('utf-8'), key_record.API_Key.encode('utf-8'))
    except ValueError:
        is_valid = False

    if not is_valid:
        logger.warning("Invalid API key secret attempted for agency: %s", agency_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or revoked API key. "
                   "Contact the NINCore administrator.",
        )

    # Stamp last used timestamp
    crud.apikey.update_last_used(db, api_key=key_record.API_Key)
    db.commit()

    logger.info(
        "Authenticated: Agency=%s Sector=%s",
        key_record.Agency_ID,
        key_record.Sector_Name,
    )
    return key_record