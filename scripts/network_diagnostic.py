#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de red en la aplicación de fotos
Ejecuta: python network_diagnostic.py
"""

import socket
import subprocess
import platform
import requests
import time
from flask import Flask
import threading

def get_all_network_interfaces():
    """Obtiene todas las interfaces de red disponibles"""
    interfaces = {}
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            print("=== IPCONFIG OUTPUT ===")
            print(result.stdout)
        else:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode != 0:
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            print("=== NETWORK INTERFACES ===")
            print(result.stdout)
    except Exception as e:
        print(f"Error getting network interfaces: {e}")

    # Método alternativo usando socket
    hostname = socket.gethostname()
    try:
        interfaces['hostname_ip'] = socket.gethostbyname(hostname)
    except:
        interfaces['hostname_ip'] = 'N/A'
    
    # Método de conexión externa
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        interfaces['external_method'] = s.getsockname()[0]
        s.close()
    except:
        interfaces['external_method'] = 'N/A'

    return interfaces

def test_port_availability(port=5000):
    """Prueba si el puerto está disponible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except:
        return False

def test_flask_server():
    """Prueba un servidor Flask básico"""
    app = Flask(__name__)
    
    @app.route('/test')
    def test():
        return "Server is working!"
    
    def run_server():
        app.run(host='0.0.0.0', port=5001, debug=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    # Test local access
    try:
        response = requests.get('http://localhost:5001/test', timeout=5)
        local_access = response.status_code == 200
    except:
        local_access = False
    
    # Test network access
    interfaces = get_all_network_interfaces()
    network_ip = interfaces.get('external_method', 'N/A')
    
    network_access = False
    if network_ip != 'N/A':
        try:
            response = requests.get(f'http://{network_ip}:5001/test', timeout=5)
            network_access = response.status_code == 200
        except:
            network_access = False
    
    return local_access, network_access, network_ip

def check_firewall():
    """Verifica configuración del firewall"""
    system = platform.system()
    print(f"\n=== FIREWALL CHECK ({system}) ===")
    
    if system == "Windows":
        try:
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                  capture_output=True, text=True)
            print("Windows Firewall Status:")
            print(result.stdout)
        except:
            print("Could not check Windows Firewall")
    
    elif system == "Darwin":  # macOS
        try:
            result = subprocess.run(['sudo', 'pfctl', '-s', 'info'], 
                                  capture_output=True, text=True)
            print("macOS Firewall Status:")
            print(result.stdout)
        except:
            print("Could not check macOS Firewall (may need sudo)")
    
    elif system == "Linux":
        try:
            result = subprocess.run(['sudo', 'ufw', 'status'], 
                                  capture_output=True, text=True)
            print("UFW Status:")
            print(result.stdout)
        except:
            try:
                result = subprocess.run(['sudo', 'iptables', '-L'], 
                                      capture_output=True, text=True)
                print("Iptables rules:")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            except:
                print("Could not check Linux Firewall")

def main():
    print("🔍 DIAGNÓSTICO DE RED PARA APLICACIÓN DE FOTOS")
    print("=" * 50)
    
    # 1. Sistema operativo
    print(f"\n📱 Sistema Operativo: {platform.system()} {platform.release()}")
    
    # 2. Interfaces de red
    print(f"\n🌐 INTERFACES DE RED:")
    interfaces = get_all_network_interfaces()
    for name, ip in interfaces.items():
        print(f"  {name}: {ip}")
    
    # 3. Prueba de puerto
    print(f"\n🔌 DISPONIBILIDAD DE PUERTOS:")
    for port in [5000, 5001, 8000, 8080]:
        available = test_port_availability(port)
        status = "✅ Disponible" if available else "❌ Ocupado"
        print(f"  Puerto {port}: {status}")
    
    # 4. Prueba de servidor Flask
    print(f"\n🧪 PRUEBA DE SERVIDOR FLASK:")
    try:
        local_ok, network_ok, network_ip = test_flask_server()
        print(f"  Acceso local (localhost): {'✅' if local_ok else '❌'}")
        print(f"  Acceso red ({network_ip}): {'✅' if network_ok else '❌'}")
    except Exception as e:
        print(f"  Error en prueba: {e}")
    
    # 5. Verificación de firewall
    check_firewall()
    
    # 6. Sugerencias
    print(f"\n💡 SUGERENCIAS:")
    
    if not test_port_availability(5000):
        print("  🔴 Puerto 5000 ocupado - Prueba cerrar otras aplicaciones o usar otro puerto")
    
    network_ip = interfaces.get('external_method', 'N/A')
    if network_ip == 'N/A':
        print("  🔴 No se pudo detectar IP de red - Verifica conexión WiFi")
    else:
        print(f"  🟢 IP de red detectada: {network_ip}")
        print(f"  📱 URL para dispositivos móviles: http://{network_ip}:5000/upload")
        print(f"  🖥️ Genera QR con esta URL: http://{network_ip}:5000/upload")
    
    print(f"\n🔧 COMANDOS ÚTILES:")
    system = platform.system()
    if system == "Windows":
        print("  - Abrir puerto en firewall: netsh advfirewall firewall add rule name='Flask App' dir=in action=allow protocol=TCP localport=5000")
        print("  - Ver puertos ocupados: netstat -an | findstr :5000")
    elif system == "Darwin":
        print("  - Ver puertos ocupados: lsof -i :5000")
        print("  - Permitir en firewall: Preferencias del Sistema > Seguridad > Firewall")
    else:  # Linux
        print("  - Ver puertos ocupados: lsof -i :5000")
        print("  - Abrir puerto UFW: sudo ufw allow 5000")
    
    print(f"\n🌐 TESTING CONECTIVIDAD:")
    print(f"  Prueba esta URL desde tu móvil: http://{network_ip}:5001/test")

if __name__ == '__main__':
    main()