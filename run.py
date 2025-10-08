from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from datetime import datetime
import os
import sqlite3
from db import get_db_connection, execute_query

app = Flask(__name__)

# Render-specific configurations
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Load model with multiple path attempts for Render deployment
def load_model():
    """Load the ML model with multiple path attempts"""
    model_paths = [
        'models/logistic regression_model.pkl',  # Local development
        'logistic regression_model.pkl',          # Root directory
        './models/logistic regression_model.pkl', # Explicit relative path
        os.path.join(os.path.dirname(__file__), 'models', 'logistic regression_model.pkl'),
        os.path.join(os.path.dirname(__file__), 'logistic regression_model.pkl')
    ]
    
    for path in model_paths:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    model = pickle.load(f)
                print(f"✓ Model loaded successfully from: {path}")
                return model
        except Exception as e:
            print(f"Failed to load model from {path}: {e}")
            continue
    
    print("✗ Warning: Model file not found in any expected location.")
    print("Expected locations:", model_paths)
    return None

# Load model at startup
model = load_model()

def log_prediction(gene_values, prediction, prediction_label, true_label=None):
    """Log prediction and optional true label to database"""
    try:
        query = '''
            INSERT INTO predictions (timestamp, gene1, gene2, gene3, gene4, gene5, prediction_numeric, prediction_label, true_label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        params = (
            datetime.now().isoformat(),
            float(gene_values[0]), float(gene_values[1]), float(gene_values[2]),
            float(gene_values[3]), float(gene_values[4]),
            int(prediction), prediction_label,
            true_label
        )
        execute_query(query, params)
        print("✓ Prediction logged successfully!")
        return True
    except Exception as e:
        print(f"✗ Error logging prediction: {e}")
        return False

def get_predictions_from_db(limit=50):
    """Get predictions from database"""
    try:
        query = '''
            SELECT id, timestamp, gene1, gene2, gene3, gene4, gene5, prediction_numeric, prediction_label, true_label
            FROM predictions ORDER BY timestamp DESC LIMIT %s
        '''
        rows = execute_query(query, (limit,), fetch=True)
        
        # Convert to list of dictionaries for easier template rendering
        predictions = []
        for row in rows:
            try:
                # Handle both SQLite Row objects and PostgreSQL tuples
                if hasattr(row, 'keys'):  # SQLite Row object
                    row_dict = dict(row)
                    predictions.append({
                        'id': row_dict['id'],
                        'timestamp': row_dict['timestamp'],
                        'gene1': round(float(row_dict['gene1']), 4),
                        'gene2': round(float(row_dict['gene2']), 4),
                        'gene3': round(float(row_dict['gene3']), 4),
                        'gene4': round(float(row_dict['gene4']), 4),
                        'gene5': round(float(row_dict['gene5']), 4),
                        'prediction_numeric': row_dict['prediction_numeric'],
                        'prediction_label': row_dict['prediction_label'],
                        'true_label': row_dict['true_label']
                    })
                else:  # PostgreSQL tuple
                    predictions.append({
                        'id': row[0],
                        'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row[1], 'strftime') else str(row[1]),
                        'gene1': round(float(row[2]), 4),
                        'gene2': round(float(row[3]), 4),
                        'gene3': round(float(row[4]), 4),
                        'gene4': round(float(row[5]), 4),
                        'gene5': round(float(row[6]), 4),
                        'prediction_numeric': row[7],
                        'prediction_label': row[8],
                        'true_label': row[9]
                    })
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        return predictions
    except Exception as e:
        print(f"✗ Error fetching predictions: {e}")
        return []

def get_prediction_stats():
    """Get statistics for dashboard"""
    try:
        # Total predictions
        total_query = 'SELECT COUNT(*) FROM predictions'
        total_result = execute_query(total_query, fetch=True)
        total = total_result[0][0] if total_result else 0
        
        # Count by label
        label_query = '''
            SELECT prediction_label, COUNT(*) 
            FROM predictions 
            GROUP BY prediction_label
        '''
        label_result = execute_query(label_query, fetch=True)
        label_counts = dict(label_result) if label_result else {}
        
        # Recent predictions (last 24 hours) - works for both SQLite and PostgreSQL
        recent_query = '''
            SELECT COUNT(*) FROM predictions 
            WHERE timestamp >= datetime('now', '-1 day')
        '''
        try:
            recent_result = execute_query(recent_query, fetch=True)
            recent = recent_result[0][0] if recent_result else 0
        except:
            # Fallback for PostgreSQL
            recent_query_pg = '''
                SELECT COUNT(*) FROM predictions 
                WHERE timestamp >= NOW() - INTERVAL '1 day'
            '''
            try:
                recent_result = execute_query(recent_query_pg, fetch=True)
                recent = recent_result[0][0] if recent_result else 0
            except:
                recent = 0
        
        return {
            'total': total,
            'positive': label_counts.get('Positive', 0),
            'negative': label_counts.get('Negative', 0),
            'recent_24h': recent
        }
    except Exception as e:
        print(f"✗ Error getting stats: {e}")
        return {
            'total': 0,
            'positive': 0,
            'negative': 0,
            'recent_24h': 0
        }

@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction requests"""
    try:
        if model is None:
            error_msg = "ML Model not available. Please contact administrator."
            if request.content_type == 'application/json':
                return jsonify({"error": error_msg}), 500
            return render_template("error.html", error=error_msg), 500
            
        # Extract gene values
        gene_values = []
        for i in range(1, 6):
            try:
                value = float(request.form[f'gene{i}'])
                gene_values.append(value)
            except (KeyError, ValueError, TypeError) as e:
                error_msg = f"Invalid or missing value for Gene {i}"
                if request.content_type == 'application/json':
                    return jsonify({"error": error_msg}), 400
                return render_template("error.html", error=error_msg), 400

        true_label = request.form.get('true_label', None)
        # Treat empty string or 'Unknown' as None
        if true_label in ["", "Unknown", None]:
            true_label = None

        # Make prediction
        pred = model.predict([gene_values])[0]
        prediction_label = "Positive" if pred == 1 else "Negative"

        # Log the prediction
        log_success = log_prediction(gene_values, pred, prediction_label, true_label)

        # Return appropriate response
        if request.content_type == 'application/json':
            return jsonify({
                "prediction": prediction_label,
                "prediction_numeric": int(pred),
                "genes": gene_values,
                "true_label": true_label,
                "logged": log_success
            })
        
        return render_template("result.html", 
                             prediction=prediction_label, 
                             genes=gene_values, 
                             true_label=true_label,
                             logged=log_success)

    except Exception as e:
        print(f"✗ Prediction error: {e}")
        error_msg = "An error occurred during prediction"
        if request.content_type == 'application/json':
            return jsonify({"error": error_msg, "details": str(e)}), 500
        return render_template("error.html", error=error_msg), 500

@app.route("/dashboard")
def dashboard():
    """Render dashboard with database statistics"""
    try:
        stats = get_prediction_stats()
        recent_predictions = get_predictions_from_db(limit=10)
        
        return render_template("dashboard.html", 
                             stats=stats, 
                             recent_predictions=recent_predictions)
    except Exception as e:
        print(f"✗ Dashboard error: {e}")
        return render_template("error.html", 
                             error="Dashboard temporarily unavailable"), 500

@app.route("/history")
def history():
    """Render full prediction history"""
    try:
        predictions = get_predictions_from_db(limit=100)
        stats = get_prediction_stats()
        
        return render_template("history.html", 
                             predictions=predictions, 
                             stats=stats)
    except Exception as e:
        print(f"✗ History error: {e}")
        return render_template("error.html", 
                             error="History temporarily unavailable"), 500

@app.route("/api/logs")
def api_logs():
    """API endpoint for logs (JSON)"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 100)  # Cap at 100
        predictions = get_predictions_from_db(limit=limit)
        return jsonify({
            "status": "success",
            "count": len(predictions),
            "data": predictions
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/api/stats")
def api_stats():
    """API endpoint for statistics (JSON)"""
    try:
        stats = get_prediction_stats()
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/health")
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        conn, db_type = get_db_connection()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": db_type,
            "model_loaded": model is not None,
            "timestamp": datetime.now().isoformat(),
            "environment": app.config['ENV']
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "model_loaded": model is not None,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/test-db")
def test_db():
    """Test database connection"""
    try:
        conn, db_type = get_db_connection()
        
        # Test a simple query
        cur = conn.cursor()
        if db_type == 'postgresql':
            cur.execute("SELECT version();")
            version_info = cur.fetchone()[0]
        else:
            cur.execute("SELECT sqlite_version();")
            version_info = f"SQLite {cur.fetchone()[0]}"
        
        cur.close()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "database_type": db_type,
            "version": version_info,
            "message": f"Successfully connected to {db_type} database"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("error.html", error="Internal server error"), 500

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Bad request"}), 400
    return render_template("error.html", error="Bad request"), 400

# Startup function for Render
def create_app():
    """Application factory for Render"""
    return app

# Main entry point
if __name__ == "__main__":
    print("🧬 Starting GenePredict Flask Application...")
    
    # Environment info
    print(f"Environment: {app.config['ENV']}")
    print(f"Debug mode: {app.config['DEBUG']}")
    
    # Test database connection
    print("🔍 Testing database connection...")
    try:
        conn, db_type = get_db_connection()
        print(f"✓ Successfully connected to {db_type} database!")
        conn.close()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Application will continue with limited functionality.")
    
    # Check model status
    if model:
        print("✓ ML Model loaded successfully")
    else:
        print("✗ ML Model not loaded - predictions will not work")
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting server on {host}:{port}")
    
    # Run the application
    app.run(
        debug=app.config['DEBUG'], 
        host=host, 
        port=port,
        threaded=True  # Enable threading for better performance
    )

