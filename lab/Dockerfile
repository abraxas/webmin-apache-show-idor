FROM debian:bookworm-slim

# Pin: webmin/webmin tag 2.670 commit 3a2b2b8671c0669c129f5275b3dd1853106ae02b
LABEL version="2.670" \
      git_commit="3a2b2b8671c0669c129f5275b3dd1853106ae02b"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C \
    WEBMIN_CONFIG=/etc/webmin \
    WEBMIN_VAR=/var/webmin \
    PERLLIB=/usr/share/webmin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        hostname \
        libio-pty-perl \
        libnet-ssleay-perl \
        openssl \
        perl \
        shared-mime-info \
    && ln -sf /usr/bin/perl /usr/local/bin/perl \
    && rm -rf /var/lib/apt/lists/*

COPY . /usr/share/webmin
WORKDIR /usr/share/webmin

RUN set -eux; \
    mkdir -p /etc/webmin /var/webmin; \
    export config_dir=/etc/webmin \
        var_dir=/var/webmin \
        perl=/usr/bin/perl \
        autoos=3 \
        port=10000 \
        login=root \
        password=labroot \
        ssl=0 \
        atboot=0 \
        nostart=1 \
        noportcheck=1 \
        noperlpath=1 \
        nochown=1; \
    /bin/sh ./setup.sh /usr/share/webmin; \
    test "$(cat /etc/webmin/version)" = "2.670"; \
    grep -q '^ssl=0' /etc/webmin/miniserv.conf; \
    sed -i \
        -e 's/^ssl_enforce=.*/ssl_enforce=0/' \
        -e 's/^ipv6=.*/ipv6=0/' \
        -e 's/^syslog=.*/syslog=0/' \
        /etc/webmin/miniserv.conf; \
    grep -q '^no_pam=' /etc/webmin/miniserv.conf || echo 'no_pam=1' >> /etc/webmin/miniserv.conf; \
    grep -q '^nofork=' /etc/webmin/miniserv.conf || echo 'nofork=1' >> /etc/webmin/miniserv.conf; \
    grep -q '^ssl_enforce=' /etc/webmin/miniserv.conf || echo 'ssl_enforce=0' >> /etc/webmin/miniserv.conf; \
    grep -q '^ipv6=' /etc/webmin/miniserv.conf || echo 'ipv6=0' >> /etc/webmin/miniserv.conf

EXPOSE 10000
CMD ["/usr/bin/perl", "/usr/share/webmin/miniserv.pl", "--nofork", "/etc/webmin/miniserv.conf"]
