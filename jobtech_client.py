import os
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class JobTechClient:
    def __init__(self):
        self.base_url = "https://jobsearch.api.jobtechdev.se"  # Removed /v2 to test base URL first
        self.headers = {
            "accept": "application/json"
        }
        logger.info(f"Initialized JobTechClient with base URL: {self.base_url}")
        
        # Test the API connection
        try:
            response = requests.get(f"{self.base_url}/search", headers=self.headers)
            logger.info(f"API Test Response Status: {response.status_code}")
            logger.info(f"API Test Response Headers: {response.headers}")
            logger.info(f"API Test Response Content: {response.text[:500]}")  # First 500 chars
        except Exception as e:
            logger.error(f"Error testing API connection: {str(e)}")

    def search_jobs(self, 
                   query: Optional[str] = None,
                   offset: int = 0,
                   limit: int = 10,
                   **kwargs) -> Dict[str, Any]:
        """
        Search for jobs using the JobTech API.
        
        Args:
            query: Free text search query
            offset: Pagination offset
            limit: Number of results per page
            **kwargs: Additional search parameters
        
        Returns:
            Dict containing search results
        """
        try:
            params = {
                "offset": offset,
                "limit": limit,
                **kwargs
            }
            
            if query:
                params["q"] = query
                
            url = f"{self.base_url}/search"
            logger.info(f"Making request to {url} with params: {json.dumps(params, indent=2)}")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            logger.debug(f"Response Content: {response.text[:500]}")  # First 500 chars
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in search_jobs: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Headers: {e.response.headers}")
                logger.error(f"Response Content: {e.response.text}")
            raise

    def get_job_ad(self, job_id: str) -> Dict[str, Any]:
        """
        Get a specific job ad by ID.
        
        Args:
            job_id: The ID of the job ad to retrieve
            
        Returns:
            Dict containing the job ad details
        """
        try:
            url = f"{self.base_url}/ad/{job_id}"
            logger.info(f"Making request to {url}")
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            logger.debug(f"Response Content: {response.text[:500]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in get_job_ad: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Headers: {e.response.headers}")
                logger.error(f"Response Content: {e.response.text}")
            raise

    def get_job_logo(self, job_id: str) -> bytes:
        """
        Get the logo for a specific job ad.
        
        Args:
            job_id: The ID of the job ad
            
        Returns:
            Bytes containing the logo image data
        """
        try:
            url = f"{self.base_url}/ad/{job_id}/logo"
            logger.info(f"Making request to {url}")
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in get_job_logo: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Headers: {e.response.headers}")
            raise

    def get_suggestions(self, 
                       query: str,
                       limit: int = 10,
                       contextual: bool = True) -> Dict[str, Any]:
        """
        Get search suggestions/typeahead results.
        
        Args:
            query: The search query to get suggestions for
            limit: Maximum number of suggestions to return
            contextual: Whether to use contextual suggestions
            
        Returns:
            Dict containing suggestion results
        """
        try:
            params = {
                "q": query,
                "limit": limit,
                "contextual": str(contextual).lower()
            }
            
            url = f"{self.base_url}/complete"
            logger.info(f"Making request to {url} with params: {json.dumps(params, indent=2)}")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            logger.debug(f"Response Content: {response.text[:500]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in get_suggestions: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Headers: {e.response.headers}")
                logger.error(f"Response Content: {e.response.text}")
            raise 