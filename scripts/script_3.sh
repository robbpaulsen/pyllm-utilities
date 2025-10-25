#!/usr/bin/env bash
# Simplified Hotspot Setup for Image Sharing Project
# Versión corregida para resolver problemas de conexión

# Configuration variables
HOTSPOT_SSID="ImageShare_$(openssl rand -hex 3)"  # Random SSID for security
HOTSPOT_PASSWORD="ShareImg2024!"  # Change this to your preferred password
HOTSPOT_IP="192.168.10.1"  # Red alternativa para evitar conflictos
HOTSPOT_SUBNET="192.168.10.0/24"
HOTSPOT_DHCP_RANGE="192.168.10.2,192.168.10.20,255.255.255.0,12h"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Detectar la interfaz WiFi disponible
detect_wifi_interface() {
    # Buscar interfaces WiFi disponibles
    WIFI_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -1)
    
    if [ -z "$WIFI_INTERFACE" ]; then
        echo "No se encontró interfaz WiFi disponible"
        exit 1
    fi
    
    echo "Usando interfaz WiFi: $WIFI_INTERFACE"
}

# Check for required packages
check_packages() {
    echo "Checking required packages..."
    
    if ! dpkg -s "hostapd" | grep 'Status: install ok installed' >/dev/null 2>&1; then
        echo "Installing hostapd..."
        apt update && apt install -y hostapd
    fi
    
    if ! dpkg -s "dnsmasq" | grep 'Status: install ok installed' >/dev/null 2>&1; then
        echo "Installing dnsmasq..."
        apt update && apt install -y dnsmasq
    fi
    
    if ! dpkg -s "iptables-persistent" | grep 'Status: install ok installed' >/dev/null 2>&1; then
        echo "Installing iptables-persistent..."
        apt update && apt install -y iptables-persistent
    fi
}

# Obtener código de país de diferentes fuentes posibles
get_country_code() {
    local country_code=""
    
    # Intentar obtener de raspi-config
    if command -v raspi-config >/dev/null 2>&1; then
        # Intentar obtener del sistema actual
        country_code=$(raspi-config nonint get_wifi_country 2>/dev/null | tr -d '\r\n')
    fi
    
    # Intentar obtener de wpa_supplicant.conf si existe
    if [ -z "$country_code" ]; then
        for wpa_conf in "/etc/wpa_supplicant/wpa_supplicant.conf" "/boot/wpa_supplicant.conf" "/boot/firmware/wpa_supplicant.conf"; do
            if [ -f "$wpa_conf" ]; then
                country_code=$(grep "country=" "$wpa_conf" | cut -d'=' -f2 | tr -d '\r\n' | head -1)
                if [ -n "$country_code" ]; then
                    echo "Country code encontrado en $wpa_conf: $country_code"
                    break
                fi
            fi
        done
    fi
    
    # Intentar obtener de la configuración del kernel
    if [ -z "$country_code" ]; then
        country_code=$(iw reg get 2>/dev/null | grep "country" | cut -d' ' -f2 | tr -d ':' | head -1)
    fi
    
    # Si aún no se encuentra, preguntar al usuario o usar por defecto
    if [ -z "$country_code" ]; then
        echo "No se pudo detectar el código de país automáticamente."
        read -p "Introduce tu código de país (por ejemplo: US, MX, ES, etc.) [US]: " input_country
        country_code="${input_country:-US}"
        echo "Usando country code: $country_code"
    else
        echo "Country code detectado: $country_code"
    fi
    
    # Validar que el código tenga 2 caracteres
    if [ ${#country_code} -ne 2 ]; then
        echo "Código de país inválido, usando US por defecto"
        country_code="US"
    fi
    
    echo "$country_code"
}

# Configure hostapd
setup_hostapd() {
    echo "Configuring hostapd..."
    
    # Backup existing config
    if [ -f "/etc/hostapd/hostapd.conf" ]; then
        cp "/etc/hostapd/hostapd.conf" "/etc/hostapd/hostapd.conf.backup"
    fi
    
    # Get WiFi country code
    COUNTRY_CODE=$(get_country_code)
    
    # Detener hostapd si está corriendo
    systemctl stop hostapd 2>/dev/null || true
    
    # Create hostapd config with hidden SSID
    cat > /etc/hostapd/hostapd.conf << EOF
# Hostapd config for Image Sharing Project
interface=${WIFI_INTERFACE}
driver=nl80211

# Network name (SSID) - Hidden network
ssid=${HOTSPOT_SSID}
ignore_broadcast_ssid=1

# WiFi channel (canal sin interferencia)
channel=6
country_code=${COUNTRY_CODE}

# WiFi security - configuración más compatible
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=${HOTSPOT_PASSWORD}
wpa_pairwise=TKIP
rsn_pairwise=CCMP

# Hardware mode - configuración más compatible
hw_mode=g
ieee80211n=1
wmm_enabled=0

# Connection limits
max_num_sta=10
beacon_int=100
dtim_period=2
EOF

    # Configurar el daemon de hostapd
    echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' > /etc/default/hostapd
    
    # Deshabilitar servicios que pueden interferir
    systemctl disable wpa_supplicant 2>/dev/null || true
    
    # Enable hostapd service
    systemctl unmask hostapd
    systemctl enable hostapd
}

# Configure dnsmasq for DHCP
setup_dnsmasq() {
    echo "Configuring dnsmasq..."
    
    # Detener dnsmasq si está corriendo
    systemctl stop dnsmasq 2>/dev/null || true
    
    # Backup existing config
    if [ -f "/etc/dnsmasq.conf" ]; then
        cp "/etc/dnsmasq.conf" "/etc/dnsmasq.conf.backup"
    fi
    
    # Create dnsmasq config
    cat > /etc/dnsmasq.conf << EOF
# dnsmasq config for Image Sharing Project
interface=${WIFI_INTERFACE}
bind-interfaces
domain-needed
bogus-priv
expand-hosts

# DHCP range
dhcp-range=${HOTSPOT_DHCP_RANGE}

# DNS settings
no-resolv
server=8.8.8.8
server=8.8.4.4

# Captive portal redirect
address=/#/${HOTSPOT_IP}

# Configuraciones adicionales para estabilidad
dhcp-option=3,${HOTSPOT_IP}
dhcp-option=6,${HOTSPOT_IP}
dhcp-authoritative
EOF

    systemctl enable dnsmasq
}

# Configurar dhcpcd correctamente
setup_dhcpcd() {
    echo "Configuring dhcpcd..."
    
    # Hacer backup de dhcpcd.conf
    if [ -f "/etc/dhcpcd.conf" ]; then
        cp "/etc/dhcpcd.conf" "/etc/dhcpcd.conf.backup"
    fi
    
    # Remover configuraciones previas del hotspot
    sed -i '/# Static IP configuration for Image Sharing Hotspot/,$d' /etc/dhcpcd.conf
    
    # Agregar configuración estática para la interfaz WiFi
    cat >> /etc/dhcpcd.conf << EOF

# Static IP configuration for Image Sharing Hotspot
interface ${WIFI_INTERFACE}
static ip_address=${HOTSPOT_IP}/24
nohook wpa_supplicant
EOF

    # Reiniciar dhcpcd para aplicar cambios
    systemctl daemon-reload
    systemctl restart dhcpcd
}

# Configurar iptables para permitir tráfico local
setup_iptables() {
    echo "Configuring iptables..."
    
    # Limpiar reglas existentes
    iptables -F
    iptables -t nat -F
    
    # Permitir tráfico local en la interfaz del hotspot
    iptables -A INPUT -i ${WIFI_INTERFACE} -j ACCEPT
    iptables -A OUTPUT -o ${WIFI_INTERFACE} -j ACCEPT
    
    # Permitir tráfico de loopback
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT
    
    # Permitir conexiones establecidas
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    
    # Guardar reglas
    if command -v netfilter-persistent &> /dev/null; then
        netfilter-persistent save
    elif command -v iptables-save &> /dev/null; then
        iptables-save > /etc/iptables/rules.v4
    fi
}

# Create systemd service for startup
create_service() {
    echo "Creating startup service..."
    
    cat > /etc/systemd/system/image-hotspot.service << EOF
[Unit]
Description=Image Sharing Hotspot
After=dhcpcd.service
Wants=dhcpcd.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/start-image-hotspot.sh
RemainAfterExit=yes
TimeoutStartSec=30

[Install]
WantedBy=multi-user.target
EOF

    # Create startup script con mejor manejo de errores
    cat > /usr/local/bin/start-image-hotspot.sh << 'EOFSTART'
#!/bin/bash
# Startup script for Image Sharing Hotspot

LOGFILE="/var/log/image-hotspot/hotspot.log"
mkdir -p /var/log/image-hotspot

log_message() {
    echo "$(date): $1" | tee -a "$LOGFILE"
}

# Función para esperar a que la interfaz esté disponible
wait_for_interface() {
    local interface="$1"
    local timeout=30
    local count=0
    
    while [ $count -lt $timeout ]; do
        if ip link show "$interface" >/dev/null 2>&1; then
            log_message "Interface $interface is available"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    log_message "ERROR: Interface $interface not available after ${timeout}s"
    return 1
}

# Detectar interfaz WiFi
WIFI_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -1)

if [ -z "$WIFI_INTERFACE" ]; then
    log_message "ERROR: No WiFi interface found"
    exit 1
fi

log_message "Starting hotspot on interface $WIFI_INTERFACE"

# Esperar a que la interfaz esté disponible
if ! wait_for_interface "$WIFI_INTERFACE"; then
    exit 1
fi

# Asegurar que la interfaz esté up
ip link set "$WIFI_INTERFACE" up
sleep 2

# Detener servicios conflictivos
systemctl stop wpa_supplicant 2>/dev/null || true
sleep 1

# Iniciar servicios del hotspot
log_message "Starting hostapd..."
if systemctl start hostapd; then
    log_message "hostapd started successfully"
else
    log_message "ERROR: Failed to start hostapd"
    exit 1
fi

sleep 3

log_message "Starting dnsmasq..."
if systemctl start dnsmasq; then
    log_message "dnsmasq started successfully"
else
    log_message "ERROR: Failed to start dnsmasq"
    exit 1
fi

log_message "Hotspot startup completed successfully"
EOFSTART

    chmod +x /usr/local/bin/start-image-hotspot.sh
    systemctl daemon-reload
    systemctl enable image-hotspot
}

# Create user management script
create_user_manager() {
    cat > /usr/local/bin/manage-hotspot-users.sh << 'EOFMANAGE'
#!/bin/bash
# User management for Image Sharing Hotspot

LOGFILE="/var/log/image-hotspot/connections.log"

case "$1" in
    "list")
        echo "Connected devices:"
        arp -a | grep -E "192\.168\.10\.[0-9]+" | awk '{print $1 " " $2}'
        ;;
    "count")
        arp -a | grep -E "192\.168\.10\.[0-9]+" | wc -l
        ;;
    "status")
        echo "=== Hotspot Status ==="
        echo "hostapd status:"
        systemctl is-active hostapd
        echo "dnsmasq status:"
        systemctl is-active dnsmasq
        echo "Connected devices: $(arp -a | grep -E '192\.168\.10\.[0-9]+' | wc -l)"
        ;;
    "restart")
        echo "Restarting hotspot services..."
        systemctl restart hostapd
        sleep 2
        systemctl restart dnsmasq
        echo "Services restarted"
        ;;
    *)
        echo "Usage: $0 [list|count|status|restart]"
        echo "  list    - List connected devices"
        echo "  count   - Count connected devices"
        echo "  status  - Show service status"
        echo "  restart - Restart hotspot services"
        ;;
esac
EOFMANAGE
    chmod +x /usr/local/bin/manage-hotspot-users.sh
}

# Create QR code data
generate_qr_info() {
    echo "Generating connection information for QR code..."
    
    # WiFi QR format: WIFI:T:WPA;S:SSID;P:PASSWORD;H:true;;
    QR_DATA="WIFI:T:WPA;S:${HOTSPOT_SSID};P:${HOTSPOT_PASSWORD};H:true;;"
    
    cat > /home/pi/hotspot_info.txt << EOF
=== Image Sharing Hotspot Configuration ===

SSID: ${HOTSPOT_SSID}
Password: ${HOTSPOT_PASSWORD}
IP Address: ${HOTSPOT_IP}
WiFi Interface: ${WIFI_INTERFACE}
Hidden Network: YES

QR Code Data (for WiFi connection):
${QR_DATA}

Flask App URL: http://${HOTSPOT_IP}:5000

=== After Connection ===
Users should automatically redirect to: http://${HOTSPOT_IP}:5000/upload

=== Management Commands ===
- Check status: sudo /usr/local/bin/manage-hotspot-users.sh status
- List devices: sudo /usr/local/bin/manage-hotspot-users.sh list
- Count connections: sudo /usr/local/bin/manage-hotspot-users.sh count
- Restart services: sudo /usr/local/bin/manage-hotspot-users.sh restart
- View logs: tail -f /var/log/image-hotspot/hotspot.log

=== Troubleshooting ===
- Check hostapd: sudo systemctl status hostapd
- Check dnsmasq: sudo systemctl status dnsmasq
- Check interface: ip addr show ${WIFI_INTERFACE}
- Restart hotspot: sudo systemctl restart image-hotspot
EOF

    # También crear una copia para el usuario actual
    if [ "$SUDO_USER" ]; then
        cp /home/pi/hotspot_info.txt /home/$SUDO_USER/hotspot_info.txt
        chown $SUDO_USER:$SUDO_USER /home/$SUDO_USER/hotspot_info.txt
    fi

    echo "Configuration saved to /home/pi/hotspot_info.txt"
    echo ""
    echo "=== IMPORTANT ==="
    echo "SSID: ${HOTSPOT_SSID}"
    echo "Password: ${HOTSPOT_PASSWORD}"
    echo "WiFi Interface: ${WIFI_INTERFACE}"
    echo "QR Data: ${QR_DATA}"
}

# Main installation function
install_hotspot() {
    echo "Installing Image Sharing Hotspot..."
    
    # Detectar interfaz WiFi primero
    detect_wifi_interface
    
    check_packages
    setup_hostapd
    setup_dnsmasq
    setup_dhcpcd
    setup_iptables
    create_service
    create_user_manager
    generate_qr_info
    
    echo ""
    echo "Installation complete!"
    echo "Please reboot your Raspberry Pi to activate the hotspot."
    echo ""
    echo "After reboot, your Pi will automatically start as a hidden hotspot."
    echo "Users will need to manually connect using:"
    echo "SSID: ${HOTSPOT_SSID}"
    echo "Password: ${HOTSPOT_PASSWORD}"
    echo ""
    echo "Check status with: sudo /usr/local/bin/manage-hotspot-users.sh status"
}

# Uninstall function
uninstall_hotspot() {
    echo "Uninstalling Image Sharing Hotspot..."
    
    systemctl stop hostapd 2>/dev/null || true
    systemctl stop dnsmasq 2>/dev/null || true
    systemctl disable hostapd 2>/dev/null || true
    systemctl disable dnsmasq 2>/dev/null || true
    systemctl disable image-hotspot 2>/dev/null || true
    
    # Restore backups
    if [ -f "/etc/hostapd/hostapd.conf.backup" ]; then
        mv "/etc/hostapd/hostapd.conf.backup" "/etc/hostapd/hostapd.conf"
    else
        rm -f /etc/hostapd/hostapd.conf
    fi
    
    if [ -f "/etc/dnsmasq.conf.backup" ]; then
        mv "/etc/dnsmasq.conf.backup" "/etc/dnsmasq.conf"
    else
        rm -f /etc/dnsmasq.conf
    fi
    
    if [ -f "/etc/dhcpcd.conf.backup" ]; then
        mv "/etc/dhcpcd.conf.backup" "/etc/dhcpcd.conf"
    fi
    
    # Remove service files
    rm -f /etc/systemd/system/image-hotspot.service
    rm -f /usr/local/bin/start-image-hotspot.sh
    rm -f /usr/local/bin/manage-hotspot-users.sh
    
    # Restaurar reglas de iptables por defecto
    iptables -F
    iptables -t nat -F
    
    systemctl daemon-reload
    systemctl restart dhcpcd
    
    echo "Uninstallation complete. Please reboot."
}

# Menu
case "$1" in
    "install"|"")
        install_hotspot
        ;;
    "uninstall")
        uninstall_hotspot
        ;;
    "info")
        if [ -f "/home/pi/hotspot_info.txt" ]; then
            cat /home/pi/hotspot_info.txt
        else
            echo "Hotspot not installed yet."
        fi
        ;;
    *)
        echo "Usage: $0 [install|uninstall|info]"
        echo "  install   - Install and configure the hotspot (default)"
        echo "  uninstall - Remove the hotspot configuration"
        echo "  info      - Show hotspot connection information"
        ;;
esac