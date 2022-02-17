def install_nginx(server):
    print("installing nginx")
    # get the package installed
    server.install_apt_package("nginx")
    # make sure it's a managed service
    stdout, _  = server.sudo("service --status-all", hide=True)
    assert "nginx" in stdout, "nginx not found in stdout = " + stdout
    server.sudo("service nginx restart", hide=True)
    stdout, stderr = server.sudo("nginx -v", hide=False)
    assert "1.1" in stderr, "unexpected Nginx version = " + stderr

def install_certbot(server):
    print("Installing certbot")
    # remove any old packages
    stdout, stderr = server.sudo("apt-get remove -y certbot")
    stdout, stderr = server.sudo("apt-get install -y python3-venv")
    stdout, stderr = server.sudo("rm -rf /usr/local/bin/certbot")
    stdout, stderr = server.sudo("python3 -m venv /opt/certbot/")
    stdout, stderr = server.sudo("/opt/certbot/bin/pip install --upgrade pip")
    stdout, stderr = server.sudo("/opt/certbot/bin/pip install certbot certbot-nginx")
    stdout, stderr = server.sudo("ln -sf /opt/certbot/bin/certbot /usr/bin/certbot")
    stdout, stderr = server.sudo("/usr/bin/certbot --version")
    assert "certbot 1.1" in stdout or "certbot 1.2" in stdout
    stdout, stderr = server.sudo("/opt/certbot/bin/pip list")
    packages = []
    versions = []
    lines = [line for line in stdout.split("\n") if "certbot" in line]
    for line in lines:
        parts = [part for part in line.split(' ') if part != '']
        packages.append(parts[0])
        versions.append(parts[1])
    assert "certbot" in packages, "missing certbot package"
    assert "certbot-nginx" in packages, "missing certbot-nginx package"
    for version in versions:
        assert version == versions[0], "inconsistent certbot versions"
        assert "1.1" in version or "1.2" in version, "unexpected certbot versions"
    return


