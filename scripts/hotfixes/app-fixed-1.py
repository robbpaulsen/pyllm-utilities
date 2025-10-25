from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import qrcode
from PIL import Image
import threading
import time
import webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json
import socket
import atexit
import signal
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max request size
app.config['BATCH_UPLOAD_LIMIT'] = 800  # Maximum files per batch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for slideshow
current_images = []
current_image_index = 0
slideshow_lock = threading.Lock()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'heic', 'heif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_qr_code():
    """Remove QR code file if it exists"""
    qr_path = "static/qr_code.png"
    try:
        if os.path.exists(qr_path):
            os.remove(qr_path)
            logger.info("🧹 Cleaned up QR code file")
    except Exception as e:
        logger.error(f"⚠️ Error cleaning QR code file: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n🛑 Shutting down gracefully...")
    cleanup_qr_code()
    sys.exit(0)

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to a remote address to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback method
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith("127."):
                # If hostname resolution gives localhost, try alternative method
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("1.1.1.1", 80))
                local_ip = s.getsockname()[0]
                s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

class UploadHandler(FileSystemEventHandler):
    """Handles new file uploads and renames them with UUID"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def on_created(self, event):
        if not event.is_directory:
            # Process file in background thread to avoid blocking
            self.executor.submit(self.process_file, event.src_path)
    
    def process_file(self, file_path):
        try:
            filename = os.path.basename(file_path)
            
            # Wait a moment to ensure file is fully written
            time.sleep(0.5)
            
            if allowed_file(filename):
                # Generate UUID filename while keeping extension
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{uuid.uuid4()}.{file_ext}"
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                try:
                    os.rename(file_path, new_path)
                    logger.info(f"Renamed {filename} to {new_filename}")
                    update_image_list()
                except Exception as e:
                    logger.error(f"Error renaming file: {e}")
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

def update_image_list():
    """Update the global image list for slideshow"""
    global current_images
    try:
        with slideshow_lock:
            current_images = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                             if allowed_file(f)]
            current_images.sort(key=lambda x: os.path.getctime(
                os.path.join(app.config['UPLOAD_FOLDER'], x)
            ), reverse=True)
            logger.info(f"Updated image list: {len(current_images)} images")
    except Exception as e:
        logger.error(f"Error updating image list: {e}")

def generate_qr_code(url):
    """Generate QR code for the upload URL"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="navy", back_color="white")
        qr_path = "static/qr_code.png"
        os.makedirs("static", exist_ok=True)
        qr_img.save(qr_path)
        return qr_path
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

@app.route('/')
@app.route('/display')
def display():
    """Main display screen with QR code and slideshow"""
    try:
        # Get local IP and generate QR code for upload URL
        local_ip = get_local_ip()
        upload_url = f"http://{local_ip}:5000/upload"
        qr_path = generate_qr_code(upload_url)
        
        logger.info(f"Server accessible at: http://{local_ip}:5000")
        logger.info(f"Upload URL for QR: {upload_url}")
        
        return render_template('display_fixed.html', qr_path=qr_path, upload_url=upload_url)
    except Exception as e:
        logger.error(f"Error in display route: {e}")
        return f"Error: {str(e)}", 500

@app.route('/qr')
def qr():
    """QR code only page - cleaner for guests to read"""
    try:
        # Get local IP and generate QR code for upload URL
        local_ip = get_local_ip()
        upload_url = f"http://{local_ip}:5000/upload"
        qr_path = generate_qr_code(upload_url)
        
        return render_template('qr.html', qr_path=qr_path, upload_url=upload_url)
    except Exception as e:
        logger.error(f"Error in qr route: {e}")
        return f"Error: {str(e)}", 500

@app.route('/upload')
def upload_page():
    """Upload page for guests"""
    try:
        return render_template('upload_fixed.html')
    except Exception as e:
        logger.error(f"Error in upload_page route: {e}")
        return f"Error: {str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads with enhanced error handling and batch limits"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files selected'}), 400
        
        files = request.files.getlist('files')
        
        # Check batch limit
        if len(files) > app.config['BATCH_UPLOAD_LIMIT']:
            return jsonify({
                'error': f'Demasiados archivos. Límite: {app.config["BATCH_UPLOAD_LIMIT"]} por lote. '
                        f'Recibidos: {len(files)}. Divide la carga en lotes más pequeños.'
            }), 400
        
        uploaded_count = 0
        failed_count = 0
        errors = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            for file in files:
                if file and file.filename:
                    future = executor.submit(process_single_file, file)
                    futures.append(future)
            
            # Collect results
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30 second timeout per file
                    if result['success']:
                        uploaded_count += 1
                    else:
                        failed_count += 1
                        errors.append(result['error'])
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Processing error: {str(e)}")
        
        if uploaded_count > 0:
            message = f'{uploaded_count} fotos subidas exitosamente!'
            if failed_count > 0:
                message += f' {failed_count} archivos fallaron.'
            
            logger.info(f"Upload completed: {uploaded_count} success, {failed_count} failed")
            return jsonify({'success': message})
        else:
            error_msg = 'No se pudieron subir archivos válidos'
            if errors:
                error_msg += f'. Errores: {", ".join(errors[:3])}'  # Show first 3 errors
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        logger.error(f"Error in upload_files: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Error del servidor: {str(e)}'}), 500

def process_single_file(file):
    """Process a single file upload"""
    try:
        if not allowed_file(file.filename):
            return {'success': False, 'error': f'Invalid file type: {file.filename}'}
        
        # Save with original filename first, handler will rename with UUID
        filename = secure_filename(file.filename)
        if not filename:
            return {'success': False, 'error': 'Invalid filename'}
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(file_path)
        
        # Verify file was saved and is valid
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return {'success': True, 'filename': filename}
        else:
            return {'success': False, 'error': f'Failed to save {filename}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Error processing {file.filename}: {str(e)}'}

@app.route('/api/images')
def get_images():
    """API endpoint to get current images for slideshow"""
    try:
        with slideshow_lock:
            return jsonify({
                'images': current_images,
                'count': len(current_images),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error in get_images: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

@app.route('/api/next_image')
def next_image():
    """Get next image for slideshow"""
    global current_image_index
    
    try:
        with slideshow_lock:
            if not current_images:
                return jsonify({'image': None, 'total': 0})
            
            image = current_images[current_image_index]
            current_image_index = (current_image_index + 1) % len(current_images)
            
            return jsonify({
                'image': url_for('uploaded_file', filename=image),
                'filename': image,
                'total': len(current_images),
                'index': current_image_index
            })
    except Exception as e:
        logger.error(f"Error in next_image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """Health check endpoint"""
    try:
        with slideshow_lock:
            image_count = len(current_images)
        
        return jsonify({
            'status': 'healthy',
            'image_count': image_count,
            'timestamp': datetime.now().isoformat(),
            'upload_limit': app.config['BATCH_UPLOAD_LIMIT']
        })
    except Exception as e:
        logger.error(f"Error in status: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def setup_file_watcher():
    """Setup file system watcher for uploads directory"""
    try:
        event_handler = UploadHandler()
        observer = Observer()
        observer.schedule(event_handler, app.config['UPLOAD_FOLDER'], recursive=False)
        observer.start()
        logger.info("File watcher started")
        return observer
    except Exception as e:
        logger.error(f"Error setting up file watcher: {e}")
        return None

def open_browser():
    """Open browser after 3 seconds delay"""
    try:
        time.sleep(3)
        local_ip = get_local_ip()
        webbrowser.open(f'http://{local_ip}:5000/display')
        logger.info("Browser opened")
    except Exception as e:
        logger.error(f"Error opening browser: {e}")

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Archivo demasiado grande. Máximo 500MB por lote.'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Register cleanup functions
    atexit.register(cleanup_qr_code)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Clean up any existing QR code at startup
    logger.info("🚀 Starting Flask app...")
    cleanup_qr_code()
    
    # Initialize image list
    update_image_list()
    
    # Start file watcher
    observer = setup_file_watcher()
    
    # Get and display local IP
    local_ip = get_local_ip()
    logger.info(f"📱 Local access: http://localhost:5000")
    logger.info(f"🌐 Network access: http://{local_ip}:5000")
    logger.info(f"📸 Upload URL for QR: http://{local_ip}:5000/upload")
    logger.info(f"🖥️ Display will open in browser in 3 seconds...")
    logger.info(f"📊 Batch upload limit: {app.config['BATCH_UPLOAD_LIMIT']} files")
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Run Flask app on all interfaces (0.0.0.0) so it's accessible from network
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Received interrupt signal")
        cleanup_qr_code()
        if observer:
            observer.stop()
    finally:
        if observer:
            observer.stop()
            observer.join()