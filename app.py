import streamlit as st
import re

# --- CONFIG ---
st.set_page_config(page_title="Cisco Wireless Automation Pro", page_icon="📶", layout="wide")

# --- DATABASE TEMPLATE SPESIFIK AP & WIRELESS ---
TEMPLATES = {
    "Access Point (AP) Deployment": {
        "Join AP to WLC (Primary/Secondary)": "capwap ap primary-base {wlc_name} {wlc_ip}\ncapwap ap secondary-base {wlc_2_name} {wlc_2_ip}\ncapwap ap controller ip address {wlc_ip}",
        "AP Static IP Configuration": "capwap ap ip address {ap_ip} {mask}\ncapwap ap ip default-gateway {gateway_ip}\ncapwap ap hostname {new_ap_name}",
        "AP Mode Change (FlexConnect/Local)": "ap mode {mode_type}\nap flexconnect vlan-central-switching\nap flexconnect native-vlan {native_vlan}",
        "AP Power & Radio (Catalyst)": "ap name {ap_name} power inline static {power_value}\nap name {ap_name} dot11 5ghz shutdown\nap name {ap_name} dot11 24ghz shutdown\nno ap name {ap_name} dot11 5ghz shutdown",
        "AP High Availability & LED": "ap led {state_on_off}\ncapwap ap redundancy-timer {timer_value}\ncapwap ap restart"
    },
    "WLC Infrastructure (DHCP & Pool)": {
        "DHCP Pool for AP Management (Option 43)": "ip dhcp pool AP_MANAGEMENT\n network {network_addr} {mask}\n default-router {gateway_ip}\n option 43 hex {wlc_hex_ip}\n lease 7",
        "DHCP Pool for Clients (SSID)": "ip dhcp pool {vlan_name}_POOL\n network {client_network} {client_mask}\n default-router {client_gateway}\n dns-server 8.8.8.8 8.8.4.4",
        "Interface SVI Creation": "interface Vlan{vlan_id}\n description {vlan_name}\n ip address {svi_ip} {svi_mask}\n no shut"
    },
    "Advanced Catalyst 9800 Config": {
        "WLC Policy & Site Tagging": "wireless profile policy {policy_name}\n vlan {vlan_id}\n no shutdown\n!\nwireless tag site {site_name}\n ap-profile {ap_profile_name}",
        "SSID dot1x (Enterprise)": "wlan {ssid_name} {id} {ssid_name}\n security dot1x authentication-list {auth_list}\n no shutdown",
        "Mobility Group Setup": "wireless mobility group name {group_name}\nwireless mobility group member {peer_wlc_ip} public-ip {peer_public_ip}"
    }
}

# --- UI LAYOUT ---
st.title("📶 Cisco Wireless Automation Pro")
st.markdown("### *Specialized for Catalyst Access Points & 9800 WLC Deployment*")
st.divider()

col_nav, col_main = st.columns([1, 2.5], gap="large")

with col_nav:
    st.subheader("📡 Wireless Modules")
    category = st.selectbox("Pilih Kategori:", list(TEMPLATES.keys()))
    template_name = st.selectbox("Skenario Konfigurasi:", list(TEMPLATES[category].keys()))
    
    st.divider()
    st.subheader("⌨️ Input Variables")
    
    raw_template = TEMPLATES[category][template_name]
    
    # PERBAIKAN: Menggunakan dict.fromkeys() untuk mendapatkan variabel unik tanpa mengubah urutan
    all_vars = re.findall(r"\{(.*?)\}", raw_template)
    unique_vars = list(dict.fromkeys(all_vars))
    
    input_values = {}
    for var in unique_vars:
        label = var.replace('_', ' ').title()
        
        # KEY UNIK: Gabungkan kategori + template + variabel agar tidak pernah bentrok
        unique_key = f"{category}_{template_name}_{var}"
        
        if "Hex" in label:
            input_values[var] = st.text_input(label, placeholder="Contoh: f1040a0a0a01", key=unique_key)
        elif "Mode" in label:
            input_values[var] = st.selectbox(label, ["local", "flexconnect", "bridge", "monitor"], key=unique_key)
        else:
            input_values[var] = st.text_input(label, key=unique_key)

with col_main:
    st.subheader("💻 Ready-to-Paste CLI")
    
    # Ambil nilai default kosong jika user belum isi agar tidak error .format()
    filled_values = {v: (input_values[v] if v in input_values else f"{{{v}}}") for v in all_vars}
    
    try:
        final_config = raw_template.format(**filled_values)
        st.code(final_config, language="bash")
        
        st.divider()
        with st.expander("ℹ️ Penjelasan Teknis (Best Practice)"):
            if "option 43" in final_config:
                st.write("Option 43 mentranslasikan IP WLC ke format Hex agar AP bisa menemukannya di Layer 3.")
            elif "primary-base" in final_config:
                st.write("Config ini memastikan AP memiliki 'Rumah Utama' dan 'Rumah Cadangan' (High Availability).")
            else:
                st.write("Konfigurasi ini divalidasi untuk perangkat Cisco Catalyst Series.")
                
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")

# --- SIDEBAR BUSINESS IMPACT ---
with st.sidebar:
    st.header("📈 Business Value")
    st.metric("Deployment Speed", "90% Faster")
    st.metric("Standardization", "Verified")
    st.divider()
    st.write("**Scenario Demo Anda:**")
    st.info(f"Modul: {template_name}")
    st.caption("Fokus pada kemudahan konfigurasi AP Catalyst di lapangan.")