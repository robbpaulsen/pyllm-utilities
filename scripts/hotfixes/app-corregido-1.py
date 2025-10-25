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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
# No file size limits - extension validation provides protection

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for slideshow
current_images = []
current_image_index = 0
slideshow_lock = threading.Lock()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_qr_code():
    """Remove QR code file if it exists"""
    qr_path = "static/qr_code.png"
    try:
        if os.path.exists(qr_path):
            os.remove(qr_path)
            print("🧹 Cleaned up QR code file")
    except Exception as e:
        print(f"⚠️ Error cleaning QR code file: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down gracefully...")
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
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
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
                    print(f"📸 Renamed {filename} to {new_filename}")
                    update_image_list()
                except Exception as e:
                    print(f"❌ Error renaming file: {e}")

def update_image_list():
    """Update the global image list for slideshow"""
    global current_images
    with slideshow_lock:
        current_images = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                         if allowed_file(f)]
        current_images.sort(key=lambda x: os.path.getctime(
            os.path.join(app.config['UPLOAD_FOLDER'], x)
        ), reverse=True)

def generate_qr_code(url):
    """Generate QR code for the upload URL"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="navy", back_color="white")
    qr_path = "static/qr_code.png"
    os.makedirs("static", exist_ok=True)
    qr_img.save(qr_path)
    return qr_path

@app.route('/')
@app.route('/display')
def display():
    """Main display screen with QR code and slideshow"""
    # Get local IP and generate QR code for upload URL
    local_ip = get_local_ip()
    upload_url = f"http://{local_ip}:5000/upload"
    qr_path = generate_qr_code(upload_url)
    
    print(f"🌐 Server accessible at: http://{local_ip}:5000")
    print(f"📱 Upload URL for QR: {upload_url}")
    
    return render_template('display.html', qr_path=qr_path, upload_url=upload_url)

@app.route('/qr')
def qr():
    """QR code only page - cleaner for guests to read"""
    # Get local IP and generate QR code for upload URL
    local_ip = get_local_ip()
    upload_url = f"http://{local_ip}:5000/upload"
    qr_path = generate_qr_code(upload_url)
    
    return render_template('qr.html', qr_path=qr_path, upload_url=upload_url)

@app.route('/upload')
def upload_page():
    """Upload page for guests"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    uploaded_count = 0
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # Save with original filename first, handler will rename with UUID
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_count += 1
            print(f"✅ Uploaded: {filename}")
    
    if uploaded_count > 0:
        return jsonify({'success': f'{uploaded_count} fotos subidas exitosamente! 🎉'})
    else:
        return jsonify({'error': 'No se pudieron subir archivos válidos'}), 400

@app.route('/api/images')
def get_images():
    """API endpoint to get current images for slideshow"""
    with slideshow_lock:
        return jsonify({
            'images': current_images,
            'count': len(current_images)
        })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/next_image')
def next_image():
    """Get next image for slideshow"""
    global current_image_index
    
    with slideshow_lock:
        if not current_images:
            return jsonify({'image': None})
        
        image = current_images[current_image_index]
        current_image_index = (current_image_index + 1) % len(current_images)
        
        return jsonify({
            'image': url_for('uploaded_file', filename=image),
            'filename': image,
            'total': len(current_images)
        })

@app.route('/api/stats')
def get_stats():
    """API endpoint to get application statistics"""
    with slideshow_lock:
        total_size = sum(
            os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            for f in current_images
        )
        
        return jsonify({
            'total_photos': len(current_images),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'server_status': 'online',
            'last_upload': max([
                os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], f))
                for f in current_images
            ], default=0) if current_images else 0
        })

def setup_file_watcher():
    """Setup file system watcher for uploads directory"""
    event_handler = UploadHandler()
    observer = Observer()
    observer.schedule(event_handler, app.config['UPLOAD_FOLDER'], recursive=False)
    observer.start()
    return observer

def open_browser():
    """Open browser after 3 seconds delay"""
    time.sleep(3)
    local_ip = get_local_ip()
    try:
        webbrowser.open(f'http://{local_ip}:5000/display')
        print(f"🚀 Browser opened: http://{local_ip}:5000/display")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")

if __name__ == '__main__':
    # Register cleanup functions
    atexit.register(cleanup_qr_code)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Clean up any existing QR code at startup
    print("🚀 Starting Digital Memoirs app...")
    cleanup_qr_code()
    
    # Initialize image list
    update_image_list()
    
    # Start file watcher
    observer = setup_file_watcher()
    
    # Get and display local IP
    local_ip = get_local_ip()
    print(f"📱 Local access: http://localhost:5000")
    print(f"🌐 Network access: http://{local_ip}:5000")
    print(f"📸 Upload URL for QR: http://{local_ip}:5000/upload")
    print(f"🖥️ Display will open in browser in 3 seconds...")
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # 🔧 SOLUCIÓN AL BUG: Cambiar debug=True por debug=False
        # En modo debug, Flask usa un reloader que causa que se abran 2 pestañas
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
        cleanup_qr_code()
        observer.stop()
    finally:
        observer.stop()
        observer.join()
        print("👋 Digital Memoirs closed gracefully")