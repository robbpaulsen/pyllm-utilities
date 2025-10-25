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
import netifaces  # pip install netifaces (opcional)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

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
            print("🧹 Cleaned up QR code file")
    except Exception as e:
        print(f"⚠️ Error cleaning QR code file: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down gracefully...")
    cleanup_qr_code()
    sys.exit(0)

def get_all_local_ips():
    """Get all possible local IP addresses"""
    ips = []
    
    # Method 1: Using netifaces (if available)
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.') and not ip.startswith('169.254.'):
                        ips.append(('netifaces_' + interface, ip))
    except ImportError:
        pass
    
    # Method 2: Socket connection method
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.append(('socket_method', s.getsockname()[0]))
        s.close()
    except:
        pass
    
    # Method 3: Hostname method
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if not ip.startswith('127.'):
            ips.append(('hostname_method', ip))
    except:
        pass
    
    # Method 4: Get all local addresses
    try:
        hostname = socket.gethostname()
        for ip in socket.getaddrinfo(hostname, None):
            addr = ip[4][0]
            if ':' not in addr and not addr.startswith('127.') and not addr.startswith('169.254.'):
                ips.append(('getaddrinfo_method', addr))
    except:
        pass
    
    return ips

def get_best_local_ip():
    """Get the most likely correct local IP"""
    all_ips = get_all_local_ips()
    
    if not all_ips:
        return "127.0.0.1"
    
    # Prefer socket method as it's most reliable
    for method, ip in all_ips:
        if method == 'socket_method':
            return ip
    
    # Otherwise, prefer 192.168.x.x or 10.x.x.x networks
    for method, ip in all_ips:
        if ip.startswith('192.168.') or ip.startswith('10.'):
            return ip
    
    # Return first available
    return all_ips[0][1]

class UploadHandler(FileSystemEventHandler):
    """Handles new file uploads and renames them with UUID"""
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            filename = os.path.basename(file_path)
            
            time.sleep(0.5)
            
            if allowed_file(filename):
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{uuid.uuid4()}.{file_ext}"
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                try:
                    os.rename(file_path, new_path)
                    print(f"✅ Renamed {filename} to {new_filename}")
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
    local_ip = get_best_local_ip()
    upload_url = f"http://{local_ip}:5000/upload"
    qr_path = generate_qr_code(upload_url)
    
    print(f"📱 Display accessed from: {request.remote_addr}")
    
    return render_template('display.html', qr_path=qr_path, upload_url=upload_url)

@app.route('/qr')
def qr():
    """QR code only page - cleaner for guests to read"""
    local_ip = get_best_local_ip()
    upload_url = f"http://{local_ip}:5000/upload"
    qr_path = generate_qr_code(upload_url)
    
    return render_template('qr.html', qr_path=qr_path, upload_url=upload_url)

@app.route('/debug')
def debug_info():
    """Debug information page"""
    all_ips = get_all_local_ips()
    best_ip = get_best_local_ip()
    
    debug_data = {
        'all_detected_ips': all_ips,
        'best_ip': best_ip,
        'request_info': {
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'host': request.headers.get('Host'),
            'url_root': request.url_root
        },
        'server_info': {
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'current_images_count': len(current_images)
        }
    }
    
    return jsonify(debug_data)

@app.route('/upload')
def upload_page():
    """Upload page for guests"""
    print(f"📱 Upload page accessed from: {request.remote_addr}")
    print(f"🌐 User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    print(f"🔗 Host header: {request.headers.get('Host', 'Unknown')}")
    
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    print(f"📤 Upload request from: {request.remote_addr}")
    
    if 'files' not in request.files:
        print("❌ No files in request")
        return jsonify({'error': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    uploaded_count = 0
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_count += 1
            print(f"✅ Saved file: {filename}")
    
    print(f"📊 Uploaded {uploaded_count} files successfully")
    
    if uploaded_count > 0:
        return jsonify({'success': f'{uploaded_count} fotos subidas exitosamente!'})
    else:
        return jsonify({'error': 'No se subieron archivos válidos'}), 400

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

@app.route('/test')
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'status': 'Server is working!',
        'timestamp': datetime.now().isoformat(),
        'client_ip': request.remote_addr
    })

def setup_file_watcher():
    """Setup file system watcher for uploads directory"""
    event_handler = UploadHandler()
    observer = Observer()
    observer.schedule(event_handler, app.config['UPLOAD_FOLDER'], recursive=False)
    observer.start()
    return observer

def open_browser():
    """Open browser after delay"""
    time.sleep(3)
    local_ip = get_best_local_ip()
    webbrowser.open(f'http://{local_ip}:5000/display')

def print_network_info():
    """Print comprehensive network information"""
    print("\n" + "="*60)
    print("🔍 INFORMACIÓN DE RED DETALLADA")
    print("="*60)
    
    all_ips = get_all_local_ips()
    best_ip = get_best_local_ip()
    
    print(f"\n📍 IPs DETECTADAS:")
    for method, ip in all_ips:
        marker = "⭐" if ip == best_ip else "  "
        print(f"{marker} {method:20} : {ip}")
    
    print(f"\n🎯 IP SELECCIONADA: {best_ip}")
    
    print(f"\n🌐 URLs DE ACCESO:")
    print(f"   Local (esta máquina): http://localhost:5000")
    print(f"   Red local (móviles) : http://{best_ip}:5000")
    print(f"   Upload directo      : http://{best_ip}:5000/upload")
    print(f"   Debug info          : http://{best_ip}:5000/debug")
    print(f"   Test conectividad   : http://{best_ip}:5000/test")
    
    print(f"\n📱 INSTRUCCIONES PARA MÓVIL:")
    print(f"   1. Conectar al mismo WiFi")
    print(f"   2. Abrir navegador móvil")
    print(f"   3. Ir a: http://{best_ip}:5000/upload")
    print(f"   4. O escanear código QR")
    
    print(f"\n🔧 TROUBLESHOOTING:")
    print(f"   • Si no funciona, probar: http://localhost:5000/debug")
    print(f"   • Verificar firewall del sistema")
    print(f"   • Asegurar que el móvil esté en la misma red WiFi")
    print(f"   • Probar desde navegador de escritorio: http://{best_ip}:5000/test")
    
    print("="*60)

if __name__ == '__main__':
    # Register cleanup functions
    atexit.register(cleanup_qr_code)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Clean up any existing QR code at startup
    print("🚀 Iniciando aplicación Flask con diagnóstico avanzado...")
    cleanup_qr_code()
    
    # Initialize image list
    update_image_list()
    
    # Start file watcher
    observer = setup_file_watcher()
    
    # Print detailed network information
    print_network_info()
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Run Flask app on all interfaces
        print(f"\n🖥️ Display se abrirá en el navegador en 3 segundos...")
        print(f"⏳ Iniciando servidor...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Interrupción recibida")
        cleanup_qr_code()
        observer.stop()
    except Exception as e:
        print(f"\n❌ Error del servidor: {e}")
        cleanup_qr_code()
        observer.stop()
    finally:
        observer.stop()
        observer.join()
        print("👋 Aplicación cerrada")