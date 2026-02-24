"""
API Routes
Handles HTTP endpoints for the Contextual Agent application
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from services.orchestrator import ContextualOrchestrator
from utils.validators import validate_zipcode, validate_date

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize orchestrator
orchestrator = ContextualOrchestrator()


@api_bp.route('/search', methods=['POST'])
def search():
    """
    Main search endpoint
    Accepts date and zipcode, returns top 5 contextual items
    """
    try:
        # Parse request data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        zipcode = data.get('zipcode', '').strip()
        date_str = data.get('date', '').strip()

        # Validate inputs
        if not zipcode:
            return jsonify({'error': 'Zipcode is required'}), 400

        if not date_str:
            return jsonify({'error': 'Date is required'}), 400

        # Validate zipcode format
        if not validate_zipcode(zipcode):
            return jsonify({'error': 'Invalid zipcode. Must be 5 digits'}), 400

        # Validate date format
        if not validate_date(date_str):
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        logger.info(f"Search request: zipcode={zipcode}, date={date_str}")

        # Process request through orchestrator
        start_time = datetime.utcnow()
        result = orchestrator.get_contextual_items(zipcode, date_str)
        end_time = datetime.utcnow()

        # Calculate response time
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Add metadata
        result['metadata'] = {
            'response_time_ms': response_time_ms,
            'timestamp': end_time.isoformat()
        }

        logger.info(f"Search completed in {response_time_ms}ms, returned {len(result.get('results', []))} items")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return jsonify({
        'status': 'ok',
        'service': 'contextual-agent-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
