import os
from server import Server

def verify_nginx(server):
    print('verifying nginx')
    stdout, stderr = server.sudo("nginx -v", hide=False)
    print((stdout, stderr))
    assert "1.1" in stderr, "unexpected Nginx version = " + stderr

def verify_certbot(server):
    print("verifying certbot")
    # remove any old packages
    stdout, stderr = server.sudo("/usr/bin/certbot --version")
    print((stdout, stderr))
    assert "certbot 1.1" in stdout or "certbot 1.2" in stdout
    return

def copy_and_configure_nginx_conf(server, www_url, seg_url, api_url):
    print("copy and configure the basic conf file")
    # put the basic bronchial configuration onto the server
    print('copying template configuration to server')
    tmp = '/home/ubuntu/tmp'
    server.run(f'rm -rf {tmp}/*.conf')
    server.put(f'assets/visionair3d.conf',f'{tmp}')
    print('verifying _fixer_')
    output, errors = server.run('fixer')
    print(output, errors)
    assert 'usage: fixer' in output
    server.run(f'fixer %WWW_URL% {www_url} {tmp}/visionair3d.conf')
    server.run(f'fixer %SEG_URL% {seg_url} {tmp}/visionair3d.conf')
    server.run(f'fixer %API_URL% {api_url} {tmp}/visionair3d.conf')

def install_nginx_conf(server):
    # move the configuration file into the nginx directories
    print('clearing old nginx conf files')
    server.sudo('rm -rf /etc/nginx/sites-available/*.conf')
    server.sudo('rm -rf /etc/nginx/sites-enabled/*.conf')
    print('copying the new visionair3d.conf to /etc/nginx/sites-available')
    server.sudo(f'cp /home/ubuntu/tmp/visionair3d.conf /etc/nginx/sites-available/visionair3d.conf')
    stdout, _ = server.run('ls /etc/nginx/sites-available')
    assert 'visionair3d.conf' in stdout
    print('linking visionair3d.conf to /etc/nginx/sites-enabled')
    server.sudo('ln -s /etc/nginx/sites-available/visionair3d.conf /etc/nginx/sites-enabled/visionair3d.conf')
    stdout, _ = server.run('ls -la /etc/nginx/sites-enabled')
    assert 'visionair3d.conf -> /etc/nginx/sites-available/visionair3d.conf' in stdout

def restart_nginx(server):
    print('restarting nginx')
    server.sudo('service nginx restart')
    output, errors = server.sudo('service --status-all')
    assert '[ + ]  nginx' in output

def run_certbot_nginx(server, www_url, seg_url, api_url):
    print('getting certbot certificates')
    command = 'sudo certbot --nginx --email gdelozier@visionair3d.app --agree-tos --no-eff-email --noninteractive'
    domains = f'--domains {www_url},{seg_url},{api_url}'
    output, errors = server.sudo(command + ' ' + domains)
    print(output, errors)

def setup_nginx(server, va3d_url, seg_url, api_url):
    va3d_url = va3d_url.replace("https://","")
    seg_url = seg_url.replace("https://","")
    api_url = api_url.replace("https://","")
    print(f'Setting up nginx configuration on {server.host}.')
    verify_nginx(server)
    verify_certbot(server)
    copy_and_configure_nginx_conf(server, va3d_url, seg_url, api_url)
    install_nginx_conf(server)
    restart_nginx(server)
    run_certbot_nginx(server, va3d_url, seg_url, api_url)
    restart_nginx(server)

