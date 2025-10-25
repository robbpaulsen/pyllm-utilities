#!/bin/bash

##############################################################################
# Captive Portal Setup Script for Digital Memoirs
#
# Este script configura el Raspberry Pi para detectar y redirigir
# automáticamente a los usuarios cuando se conectan al WiFi.
#
# IMPORTANTE: Ejecutar como root o con sudo
#
# Uso: sudo bash setup-captive-portal.sh
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="10.0.17.1"
DNSMASQ_CONF="/etc/dnsmasq.conf"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "  Digital Memoirs - Captive Portal Setup"
    echo "=================================================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script debe ejecutarse como root"
        echo "Por favor ejecuta: sudo bash $0"
        exit 1
    fi
}

##############################################################################
# Backup Functions
##############################################################################

backup_config() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}${BACKUP_SUFFIX}"
        print_success "Backup creado: ${file}${BACKUP_SUFFIX}"
    else
        print_warning "Archivo no encontrado: $file"
    fi
}

##############################################################################
# Configuration Functions
##############################################################################

configure_dnsmasq() {
    print_info "Configurando dnsmasq para captive portal..."

    # Backup existing configuration
    backup_config "$DNSMASQ_CONF"

    # Check if captive portal configuration already exists
    if grep -q "# Captive Portal Detection - Digital Memoirs" "$DNSMASQ_CONF" 2>/dev/null; then
        print_warning "Configuración de captive portal ya existe en dnsmasq.conf"
        read -p "¿Deseas reconfigurar? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Saltando configuración de dnsmasq..."
            return
        fi
        # Remove old configuration
        sed -i '/# Captive Portal Detection - Digital Memoirs/,/# End Captive Portal Detection/d' "$DNSMASQ_CONF"
    fi

    # Add captive portal configuration
    cat >> "$DNSMASQ_CONF" << EOF

# Captive Portal Detection - Digital Memoirs
# Added: $(date)
# These entries redirect OS-level captive portal checks to our server

# iOS Captive Portal Detection
address=/captive.apple.com/$SERVER_IP
address=/www.apple.com/$SERVER_IP

# Android Captive Portal Detection
address=/connectivitycheck.gstatic.com/$SERVER_IP
address=/www.gstatic.com/$SERVER_IP
address=/clients3.google.com/$SERVER_IP

# Windows Captive Portal Detection
address=/www.msftconnecttest.com/$SERVER_IP
address=/msftconnecttest.com/$SERVER_IP

# Firefox Captive Portal Detection
address=/detectportal.firefox.com/$SERVER_IP

# End Captive Portal Detection
EOF

    print_success "Configuración de dnsmasq actualizada"
}

restart_services() {
    print_info "Reiniciando servicios..."

    # Restart dnsmasq
    if systemctl restart dnsmasq; then
        print_success "dnsmasq reiniciado exitosamente"
    else
        print_error "Error al reiniciar dnsmasq"
        print_info "Verifica el log: sudo journalctl -u dnsmasq -n 50"
        exit 1
    fi

    # Check dnsmasq status
    if systemctl is-active --quiet dnsmasq; then
        print_success "dnsmasq está corriendo correctamente"
    else
        print_error "dnsmasq no está corriendo"
        exit 1
    fi
}

verify_configuration() {
    print_info "Verificando configuración..."

    # Check if dnsmasq config is valid
    if dnsmasq --test 2>/dev/null; then
        print_success "Configuración de dnsmasq es válida"
    else
        print_error "Configuración de dnsmasq tiene errores"
        print_info "Restaurando backup..."
        cp "${DNSMASQ_CONF}${BACKUP_SUFFIX}" "$DNSMASQ_CONF"
        systemctl restart dnsmasq
        exit 1
    fi

    # Test DNS resolution
    print_info "Probando resolución DNS..."
    if nslookup captive.apple.com localhost 2>/dev/null | grep -q "$SERVER_IP"; then
        print_success "DNS está redirigiendo correctamente a $SERVER_IP"
    else
        print_warning "No se pudo verificar la redirección DNS"
    fi
}

display_summary() {
    echo ""
    print_header
    echo -e "${GREEN}✓ Captive Portal configurado exitosamente!${NC}"
    echo ""
    echo "Configuración aplicada:"
    echo "  • Servidor IP: $SERVER_IP"
    echo "  • DNS redirigiendo peticiones de captive portal"
    echo "  • Backup guardado: ${DNSMASQ_CONF}${BACKUP_SUFFIX}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Asegúrate de que Flask esté corriendo en $SERVER_IP:5000"
    echo "  2. Prueba con un dispositivo móvil:"
    echo "     - Escanea el QR WiFi"
    echo "     - Espera la notificación 'Iniciar sesión en red'"
    echo "     - Toca la notificación → debería abrir /upload"
    echo ""
    echo "Para revertir cambios:"
    echo "  sudo cp ${DNSMASQ_CONF}${BACKUP_SUFFIX} $DNSMASQ_CONF"
    echo "  sudo systemctl restart dnsmasq"
    echo ""
    echo -e "${BLUE}=================================================================="
    echo -e "Para más información, consulta: scripts/CAPTIVE_PORTAL_SETUP.md"
    echo -e "==================================================================${NC}"
    echo ""
}

rollback() {
    print_error "Ocurrió un error. Revirtiendo cambios..."
    if [ -f "${DNSMASQ_CONF}${BACKUP_SUFFIX}" ]; then
        cp "${DNSMASQ_CONF}${BACKUP_SUFFIX}" "$DNSMASQ_CONF"
        systemctl restart dnsmasq
        print_success "Configuración restaurada"
    fi
    exit 1
}

##############################################################################
# Main Execution
##############################################################################

main() {
    # Set error trap
    trap rollback ERR

    print_header

    # Prerequisite checks
    check_root

    print_info "Iniciando configuración del captive portal..."
    echo ""

    # Configuration steps
    configure_dnsmasq
    restart_services
    verify_configuration
    display_summary

    print_success "¡Setup completado!"
}

# Run main function
main
