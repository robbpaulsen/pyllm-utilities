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
    WIFI_INTERFACE=$(iw dev 2>/dev/null | awk '$1=="Interface"{print $2}' | head -1)
    
    # Si no encuentra con iw, intentar con ip link
    if [ -z "$WIFI_INTERFACE" ]; then
        WIFI_INTERFACE=$(ip link show | grep -E "wlan[0-9]|wlp[0-9]" | cut -d':' -f2 | tr -d ' ' | head -1)
    fi
    
    # Como último recurso, asumir wlan0
    if [ -z "$WIFI_INTERFACE" ]; then
        WIFI_INTERFACE="wlan0"
        echo "No se detectó interfaz WiFi automáticamente, usando wlan0 por defecto"
    fi
    
    # Verificar que la interfaz existe
    if ! ip link show "$WIFI_INTERFACE" >/dev/null 2>&1; then
        echo "ERROR: La interfaz $WIFI_INTERFACE no existe"
        echo "Interfaces disponibles:"
        ip link show | grep -E "^[0-9]+:" | cut -d':' -f2 | tr -d ' '
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
        echo "No se pudo detectar el código de país automáticamente." >&2
        read -p "Introduce tu código de país (por ejemplo: US, MX, ES, etc.) [US]: " input_country
        country_code="${input_country:-US}"
    fi
    
    # Validar que el código tenga 2 caracteres y solo contenga letras
    if [[ ! "$country_code" =~ ^[A-Z]{2}$ ]]; then
        # Intentar convertir a mayúsculas y tomar solo 2 caracteres
        country_code=$(echo "$country_code" | tr '[:lower:]' '[:upper:]' | head -c 2)
        
        # Verificar de nuevo
        if [[ ! "$country_code" =~ ^[A-Z]{2}$ ]]; then
            echo "Código de país inválido, usando US por defecto" >&2
            country_code="US"
        fi
    fi
    
    # Solo retornar el código, sin mensajes
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
    echo "Obteniendo código de país WiFi..."
    COUNTRY_CODE=$(get_country_code)
    echo "Usando country code: $COUNTRY_CODE"
    
    # Detener y deshabilitar servicios conflictivos
    echo "Deteniendo servicios conflictivos..."
    systemctl stop hostapd 2>/dev/null || true
    systemctl stop wpa_supplicant 2>/dev/null || true
    
    # Deshabilitar wpa_supplicant para la interfaz WiFi
    systemctl disable wpa_supplicant 2>/dev/null || true
    
    # Liberar la interfaz WiFi de wpa_supplicant
    if pgrep wpa_supplicant > /dev/null; then
        echo "Terminando procesos wpa_supplicant..."
        pkill wpa_supplicant 2>/dev/null || true
        sleep 2
    fi
    
    # Asegurar que la interfaz esté disponible
    ip link set ${WIFI_INTERFACE} down 2>/dev/null || true
    sleep 1
    ip link set ${WIFI_INTERFACE} up 2>/dev/null || true
    sleep 1
    
    # Verificar que la interfaz esté lista para modo AP
    echo "Verificando capacidades de la interfaz ${WIFI_INTERFACE}..."
    if ! iw ${WIFI_INTERFACE} info | grep -q "type managed"; then
        echo "Configurando interfaz en modo managed..."
        iw ${WIFI_INTERFACE} set type managed 2>/dev/null || true
    fi
    
    # Create hostapd config with configuración más básica
    cat > /etc/hostapd/hostapd.conf << EOF
# Hostapd config for Image Sharing Project - Basic Configuration
interface=${WIFI_INTERFACE}
driver=nl80211

# Network name (SSID) - Hidden network
ssid=${HOTSPOT_SSID}
ignore_broadcast_ssid=1

# WiFi channel (canal sin interferencia)
channel=6
country_code=${COUNTRY_CODE}

# WiFi security - configuración básica y compatible
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=${HOTSPOT_PASSWORD}
wpa_pairwise=CCMP
rsn_pairwise=CCMP

# Hardware mode - configuración más básica
hw_mode=g

# Connection limits
max_num_sta=10

# Logging para debugging
logger_syslog=-1
logger_syslog_level=2
EOF

    # Configurar el daemon de hostapd
    echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' > /etc/default/hostapd
    
    # Crear archivo de configuración adicional para systemd
    mkdir -p /etc/systemd/system/hostapd.service.d
    cat > /etc/systemd/system/hostapd.service.d/override.conf << EOF
[Unit]
After=dhcpcd.service
Wants=dhcpcd.service

[Service]
ExecStartPre=/bin/sleep 2
ExecStartPre=/usr/bin/pkill -f wpa_supplicant || /bin/true
ExecStartPre=/sbin/ip link set ${WIFI_INTERFACE} down || /bin/true
ExecStartPre=/bin/sleep 1
ExecStartPre=/sbin/ip link set ${WIFI_INTERFACE} up
Restart=on-failure
RestartSec=5
EOF

    # Enable hostapd service
    systemctl daemon-reload
    systemctl unmask hostapd
    systemctl enable hostapd
    
    echo "hostapd configurado correctamente"
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
    echo "Configuring network configuration..."
    
    # Detectar cuál servicio de configuración de red está disponible
    local network_service=""
    local config_method=""
    
    if systemctl list-unit-files | grep -q "dhcpcd.service"; then
        network_service="dhcpcd"
        config_method="dhcpcd_conf"
    elif command -v dhclient >/dev/null 2>&1; then
        network_service="dhclient"
        config_method="interfaces"
        echo "Sistema con dhclient detectado (configuración tradicional Debian)"
    elif systemctl list-unit-files | grep -q "systemd-networkd.service"; then
        network_service="systemd-networkd"
        config_method="systemd_network"
    elif systemctl list-unit-files | grep -q "networking.service"; then
        network_service="networking"
        config_method="interfaces"
    else
        echo "No se encontró servicio de red conocido, usando configuración manual..."
        config_method="manual"
    fi
    
    echo "Servicio de red detectado: ${network_service:-manual}"
    echo "Método de configuración: $config_method"
    
    case "$config_method" in
        "dhcpcd_conf")
            setup_dhcpcd_method
            ;;
        "interfaces")
            setup_interfaces_method
            ;;
        "systemd_network")
            setup_systemd_network_method
            ;;
        "manual")
            setup_manual_method
            ;;
    esac
}

# Configuración usando dhcpcd.conf
setup_dhcpcd_method() {
    echo "Configurando usando dhcpcd.conf..."
    
    if ! systemctl is-enabled dhcpcd >/dev/null 2>&1; then
        echo "dhcpcd no está habilitado, habilitándolo..."
        systemctl enable dhcpcd
    fi
    
    if [ -f "/etc/dhcpcd.conf" ]; then
        cp "/etc/dhcpcd.conf" "/etc/dhcpcd.conf.backup.$(date +%Y%m%d_%H%M%S)"
        sed -i '/# Static IP configuration for Image Sharing Hotspot/,$d' /etc/dhcpcd.conf
        
        cat >> /etc/dhcpcd.conf << EOF

# Static IP configuration for Image Sharing Hotspot
interface ${WIFI_INTERFACE}
static ip_address=${HOTSPOT_IP}/24
nohook wpa_supplicant
EOF
        echo "✓ dhcpcd.conf configurado"
    fi
}

# Configuración usando /etc/network/interfaces (dhclient)
setup_interfaces_method() {
    echo "Configurando usando /etc/network/interfaces (dhclient)..."
    
    # Backup del archivo interfaces
    if [ -f "/etc/network/interfaces" ]; then
        cp "/etc/network/interfaces" "/etc/network/interfaces.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Remover configuración previa del hotspot
    sed -i '/# Image Sharing Hotspot configuration/,/# End Image Sharing Hotspot configuration/d' /etc/network/interfaces
    
    # Agregar configuración estática
    cat >> /etc/network/interfaces << EOF

# Image Sharing Hotspot configuration
auto ${WIFI_INTERFACE}
iface ${WIFI_INTERFACE} inet static
    address ${HOTSPOT_IP}
    netmask 255.255.255.0
    network ${HOTSPOT_SUBNET%/*}
    broadcast 192.168.10.255
# End Image Sharing Hotspot configuration
EOF
    
    echo "✓ /etc/network/interfaces configurado"
    
    # Asegurar que networking esté habilitado
    systemctl enable networking 2>/dev/null || true
}

# Configuración usando systemd-networkd
setup_systemd_network_method() {
    echo "Configurando usando systemd-networkd..."
    
    mkdir -p /etc/systemd/network
    cat > /etc/systemd/network/10-hotspot.network << EOF
[Match]
Name=${WIFI_INTERFACE}

[Network]
IPForward=yes
Address=${HOTSPOT_IP}/24

[Route]
Destination=0.0.0.0/0
Gateway=${HOTSPOT_IP}
EOF
    
    systemctl enable systemd-networkd 2>/dev/null || true
    echo "✓ systemd-networkd configurado"
}

# Configuración manual como fallback
setup_manual_method() {
    echo "Usando configuración manual..."
    
    # Crear script para configurar IP manualmente
    cat > /usr/local/bin/hotspot-network-setup.sh << EOF
#!/bin/bash
# Manual network setup for hotspot

# Configure static IP
ip addr flush dev ${WIFI_INTERFACE}
ip addr add ${HOTSPOT_IP}/24 dev ${WIFI_INTERFACE}
ip link set ${WIFI_INTERFACE} up

# Add route
ip route add ${HOTSPOT_SUBNET} dev ${WIFI_INTERFACE} 2>/dev/null || true

echo "Network configured manually for ${WIFI_INTERFACE}"
EOF
    
    chmod +x /usr/local/bin/hotspot-network-setup.sh
    echo "✓ Script de configuración manual creado"
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

# Función para verificar y liberar la interfaz
prepare_interface() {
    local interface="$1"
    
    log_message "Preparing interface $interface for AP mode"
    
    # Matar cualquier proceso wpa_supplicant que esté usando la interfaz
    if pgrep wpa_supplicant > /dev/null; then
        log_message "Stopping wpa_supplicant processes"
        pkill -f "wpa_supplicant.*$interface" 2>/dev/null || true
        sleep 2
    fi
    
    # Detener dhclient si está corriendo en la interfaz
    if pgrep dhclient > /dev/null; then
        log_message "Stopping dhclient processes on $interface"
        pkill -f "dhclient.*$interface" 2>/dev/null || true
        sleep 1
    fi
    
    # Asegurar que la interfaz esté down y luego up
    ip link set "$interface" down 2>/dev/null || true
    sleep 1
    ip link set "$interface" up 2>/dev/null || true
    sleep 2
    
    # Configurar IP estática si existe el script manual
    if [ -f "/usr/local/bin/hotspot-network-setup.sh" ]; then
        log_message "Applying manual network configuration"
        /usr/local/bin/hotspot-network-setup.sh
    fi
    
    # Verificar que no hay configuración IP conflictiva (excepto la nuestra)
    current_ip=$(ip addr show "$interface" | grep 'inet ' | grep -v '192.168.10.' | awk '{print $2}' | cut -d'/' -f1)
    if [ -n "$current_ip" ]; then
        log_message "Removing conflicting IP: $current_ip"
        ip addr del "$current_ip" dev "$interface" 2>/dev/null || true
    fi
    
    log_message "Interface $interface prepared for AP mode"
}

# Función para verificar hostapd antes de iniciar
check_hostapd_config() {
    log_message "Verifying hostapd configuration"
    
    if ! hostapd -t /etc/hostapd/hostapd.conf; then
        log_message "ERROR: hostapd configuration test failed"
        return 1
    fi
    
    log_message "hostapd configuration is valid"
    return 0
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

# Preparar la interfaz
if ! prepare_interface "$WIFI_INTERFACE"; then
    log_message "ERROR: Failed to prepare interface"
    exit 1
fi

# Verificar configuración de hostapd
if ! check_hostapd_config; then
    exit 1
fi

# Detener servicios conflictivos
log_message "Stopping conflicting services"
systemctl stop wpa_supplicant 2>/dev/null || true
systemctl stop NetworkManager 2>/dev/null || true
sleep 2

# Iniciar servicios del hotspot
log_message "Starting hostapd..."
if systemctl start hostapd; then
    log_message "hostapd started successfully"
    sleep 3
    
    # Verificar que hostapd realmente está corriendo
    if systemctl is-active hostapd >/dev/null 2>&1; then
        log_message "hostapd is running and active"
    else
        log_message "ERROR: hostapd started but is not active"
        systemctl status hostapd >> "$LOGFILE" 2>&1
        exit 1
    fi
else
    log_message "ERROR: Failed to start hostapd"
    systemctl status hostapd >> "$LOGFILE" 2>&1
    journalctl -u hostapd --no-pager -n 20 >> "$LOGFILE" 2>&1
    exit 1
fi

log_message "Starting dnsmasq..."
if systemctl start dnsmasq; then
    log_message "dnsmasq started successfully"
    
    # Verificar que dnsmasq está activo
    if systemctl is-active dnsmasq >/dev/null 2>&1; then
        log_message "dnsmasq is running and active"
    else
        log_message "WARNING: dnsmasq started but may not be fully active"
    fi
else
    log_message "ERROR: Failed to start dnsmasq"
    systemctl status dnsmasq >> "$LOGFILE" 2>&1
    exit 1
fi

log_message "Hotspot startup completed successfully"
log_message "SSID: $(grep '^ssid=' /etc/hostapd/hostapd.conf | cut -d'=' -f2)"
log_message "IP Address: $(ip addr show $WIFI_INTERFACE | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)"
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
        arp -a | grep -E "192\.168\.4\.[0-9]+" | awk '{print $1 " " $2}'
        ;;
    "count")
        arp -a | grep -E "192\.168\.4\.[0-9]+" | wc -l
        ;;
    "status")
        echo "=== Hotspot Status ==="
        echo "hostapd status:"
        systemctl is-active hostapd
        echo "dnsmasq status:"
        systemctl is-active dnsmasq
        echo "Connected devices: $(arp -a | grep -E '192\.168\.4\.[0-9]+' | wc -l)"
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

    # Solo crear copia para el usuario actual si no es el mismo archivo
    if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "pi" ]; then
        cp /home/pi/hotspot_info.txt /home/$SUDO_USER/hotspot_info.txt 2>/dev/null && \
        chown $SUDO_USER:$SUDO_USER /home/$SUDO_USER/hotspot_info.txt 2>/dev/null || true
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
