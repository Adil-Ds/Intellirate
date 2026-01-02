"""
Firebase Authentication Middleware
Validates Firebase ID tokens for all requests
"""
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from environment"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        # Parse Firebase private key (handle escaped newlines)
        private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
        
        # Create credentials
        cred_dict = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key": private_key,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        
        _firebase_initialized = True
        logger.info("✓ Firebase Admin SDK initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise


class FirebaseAuthMiddleware:
    """Middleware to validate Firebase authentication tokens"""
    
    security = HTTPBearer()
    
    @staticmethod
    async def verify_token(request: Request) -> dict:
        """
        Verify Firebase ID token from request headers
        
        Args:
            request: FastAPI request object
            
        Returns:
            dict: User information from decoded token
            
        Raises:
            HTTPException: If authentication fails
        """
        # Initialize Firebase if not already done
        if not _firebase_initialized:
            initialize_firebase()
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token from "Bearer <token>"
        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID from custom header
        user_id_header = request.headers.get("X-User-Id")
        if not user_id_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-User-Id header required"
            )
        
        # Verify Firebase token
        try:
            decoded_token = auth.verify_id_token(token)
            
            # Verify user ID matches token
            if decoded_token.get("uid") != user_id_header:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User ID mismatch - token UID does not match X-User-Id header"
                )
            
            # Extract user email
            user_email = request.headers.get("X-User-Email") or decoded_token.get("email")
            
            return {
                "uid": decoded_token["uid"],
                "email": user_email,
                "firebase_claims": decoded_token
            }
            
        except auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Firebase ID token"
            )
        except auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase ID token has expired"
            )
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}"
            )
    
    @staticmethod
    def get_user_tier(user_info: dict) -> str:
        """
        Determine user tier from Firebase custom claims
        
        Args:
            user_info: User information from decoded token
            
        Returns:
            str: User tier (free/pro/enterprise)
        """
        claims = user_info.get("firebase_claims", {})
        
        # Check custom claims for tier information
        tier = claims.get("tier", "free")
        
        # Validate tier
        valid_tiers = ["free", "pro", "enterprise"]
        if tier not in valid_tiers:
            tier = "free"
        
        return tier
