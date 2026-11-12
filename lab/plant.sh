#!/bin/bash
# Plant two Apache vhosts and a virts-limited Webmin user, then start miniserv.
set -euo pipefail

WITNESS="WEBMIN-H01-APACHE-IDOR"
ALLOWED_HOST="allowed.example"
DENIED_HOST="denied.example"
HTTPD_CONF="/etc/apache2/webmin-h01-vhosts.conf"
LIMITED_USER="limited"
LIMITED_PASS="limited-pass"
APACHE_BIN="/usr/sbin/apache2"
WEBMIN_CONF="/etc/webmin"

mkdir -p /etc/apache2 /var/www/allowed /var/www/denied \
  "${WEBMIN_CONF}/apache" /var/webmin

if [[ ! -x "${APACHE_BIN}" ]]; then
  cat > "${APACHE_BIN}" << 'EOF'
#!/bin/sh
case "$1" in
  -v)
    echo "Server version: Apache/2.4.62 (Debian)"
    echo "Server built:   lab"
    exit 0
    ;;
  -l)
    printf '%s\n' "Compiled in modules:" "  core.c" "  http_core.c" "  mod_so.c"
    exit 0
    ;;
  -t)
    echo "Syntax OK"
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
EOF
  chmod 0755 "${APACHE_BIN}"
fi

cat > "${HTTPD_CONF}" << EOF
ServerRoot "/etc/apache2"
Listen 80
<VirtualHost *:80>
    ServerName ${ALLOWED_HOST}
    DocumentRoot /var/www/allowed
    ServerAdmin allowed-only@${ALLOWED_HOST}
</VirtualHost>
<VirtualHost *:80>
    ServerName ${DENIED_HOST}
    DocumentRoot /var/www/denied
    ServerAdmin ${WITNESS}
</VirtualHost>
EOF

# Overwrite module config so debian Includes/defines are not parsed.
cat > "${WEBMIN_CONF}/apache/config" << EOF
httpd_dir=/etc/apache2
httpd_path=${APACHE_BIN}
httpd_conf=${HTTPD_CONF}
show_order=0
max_servers=100
test_config=0
test_manual=0
test_always=0
test_apachectl=0
auto_mods=1
show_names=0
allow_virtualmin=0
format_config=1
show_list=1
EOF

hash="$(perl -e 'print crypt($ARGV[0], q($6$webminh01$))' "${LIMITED_PASS}")"
if [[ -z "${hash}" || "${hash}" == "${LIMITED_PASS}" || "${hash}" == *"*"* ]]; then
  echo "plant: crypt failed" >&2
  exit 1
fi

users_file="${WEBMIN_CONF}/miniserv.users"
acl_file="${WEBMIN_CONF}/webmin.acl"
if ! grep -q "^${LIMITED_USER}:" "${users_file}"; then
  echo "${LIMITED_USER}:${hash}:0" >> "${users_file}"
fi
if grep -q "^${LIMITED_USER}:" "${acl_file}"; then
  sed -i "s|^${LIMITED_USER}:.*|${LIMITED_USER}: apache|" "${acl_file}"
else
  echo "${LIMITED_USER}: apache" >> "${acl_file}"
fi

# types is not *: manual_save.cgi stays closed. virts is the allowed host only.
cat > "${WEBMIN_CONF}/apache/${LIMITED_USER}.acl" << EOF
virts=${ALLOWED_HOST}:80
global=0
create=0
vuser=0
noconfig=1
stop=0
apply=0
vaddr=0
dir=/
types=0 1 2 3 4 5
pipe=0
names=1
dirsmode=0
aliasdir=/
EOF

miniserv="${WEBMIN_CONF}/miniserv.conf"
sed -i \
  -e 's/^ssl=.*/ssl=0/' \
  -e 's/^ssl_enforce=.*/ssl_enforce=0/' \
  -e 's/^ipv6=.*/ipv6=0/' \
  -e 's/^syslog=.*/syslog=0/' \
  "${miniserv}"
grep -q '^no_pam=' "${miniserv}" || echo 'no_pam=1' >> "${miniserv}"
grep -q '^nofork=' "${miniserv}" || echo 'nofork=1' >> "${miniserv}"
grep -q '^ssl_enforce=' "${miniserv}" || echo 'ssl_enforce=0' >> "${miniserv}"
grep -q '^ipv6=' "${miniserv}" || echo 'ipv6=0' >> "${miniserv}"
grep -q '^syslog=' "${miniserv}" || echo 'syslog=0' >> "${miniserv}"

chmod 600 "${users_file}" "${acl_file}" \
  "${WEBMIN_CONF}/apache/${LIMITED_USER}.acl" "${WEBMIN_CONF}/apache/config"

echo "plant: vhosts=${HTTPD_CONF} user=${LIMITED_USER} virts=${ALLOWED_HOST}:80"

exec /usr/bin/perl /usr/share/webmin/miniserv.pl --nofork "${miniserv}"
