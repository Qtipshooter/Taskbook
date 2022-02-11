from server import Server
import os

def install_apt_packages(server):
    server.update_apt_packages()
    server.install_apt_package("python3-pip")
    packages = server.get_installed_apt_packages()
    assert "python3-pip" in packages
    assert server.apt_package_is_installed("python3-pip")
    version = server.get_python3_version()
    assert version.startswith("3.8")

def install_pip3_packages(server):
    version = server.get_pip3_version()
    assert version.startswith("20.")
    assert version.endswith("3.8")
    server.install_pip3_package("dataset")
    server.install_pip3_package("flask")
    packages = server.get_installed_pip3_packages()
    assert "dataset" in packages
    assert "flask" in packages

def get_source_code(server):

    # make sure we have git
    version = server.get_git_version()
    assert version.startswith("2.")

    # make sure we have a projects directory
    server.run("mkdir -p ~/projects")

    # delete old swift directory if there
    server.run("rm -rf ~/projects/taskbook-SWE")

    # get the code from Git
    server.run("cd ~/projects; git clone --depth 1 https://github.com/Qtipshooter/taskbook-SWE.git", hide=False)
    server.run("cd ~/projects/taskbook-SWE; rm -rf .git", hide=False)
    
    # transfer the code to the target machine
    server.local("rm -rf /home/runner/work/taskbook-SWE/taskbook-SWE/.git")
    server.local("rm -rf /home/runner/work/taskbook-SWE/taskbook-SWE/deploy/__pycache__")
    server.local("pushd /home/runner/work/taskbook-SWE/taskbook-SWE; tar cvf /home/runner/taskbook-SWE.tar . ; popd", hide=False)
    server.local("ls -la", hide=False)
    server.local("tar tvf /home/runner/taskbook-SWE.tar", hide=False)
    server.put("/home/runner/swift.tar","/home/ubuntu/taskbook-SWE.tar")
    server.run("tar tvf /home/ubuntu/taskbook-SWE.tar", hide=False)
    server.run("mkdir /home/ubuntu/projects/taskbook-SWE")
    server.run("pushd /home/ubuntu/projects/taskbook-SWE; tar xvf /home/ubuntu/taskbook-SWE.tar ; popd", hide=False)

    # verify the code was deployed
    stdout, _ = server.run("ls ~/projects/taskbook-SWE")
    assert "app.py" in stdout

def initialize_application(server):
    # set up the database, etc.
    server.run("cd ~/projects/taskbook-SWE; python3 setup.py")

def get_process_id(process):
    parts = process.strip().split(" ")
    id = int(parts[0])
    assert type(id) is int
    return id


def start_application(server):
    server.run("cd ~/projects/taskbook-SWE; screen -S webapp -dm python3 app.py")

def stop_application_processes(server):
    # find and kill the screen process
    processes = server.get_running_processes()
    processes = [p for p in processes if "SCREEN" in p and "app.py" in p ]
    if len(processes) > 0:
        screen_id = get_process_id(processes[0])
        server.sudo(f"kill -9 {screen_id}")

    # find and kill remaining swift.py python process, if any.
    processes = server.get_running_processes()
    processes = [p for p in processes if "SCREEN" not in p and "app.py" in p ]
    if len(processes) > 0:
        screen_id = get_process_id(processes[0])
        server.sudo(f"kill -9 {screen_id}")

    # verify that processes aren't running
    processes = server.get_running_processes()
    processes = [p for p in processes if "app.py" in p ]
    assert len(processes) == 0

def verify_application_processes(server):
    # verify the screen process
    processes = server.get_running_processes()
    processes = [p for p in processes if "SCREEN" in p and "app.py" in p ]
    assert len(processes) == 1, "Screen session process was not found."

    # verify the swift.py python process.
    processes = server.get_running_processes()
    processes = [p for p in processes if "SCREEN" not in p and "app.py" in p ]
    assert len(processes) == 1, "$ python3 app.py was not found"


if __name__ == "__main__":
    server = Server( host = "dev.taskbook.xyz", user="ubuntu", key_filename="/home/runner/.ssh/DevServer.pem")

    print("stopping application processes")
    stop_application_processes(server)

    print("installing apt packages")
    install_apt_packages(server)

    print("installing pip3 packages")
    install_pip3_packages(server)

    print("getting the source code")
    get_source_code(server)

    print("initialize the application")
    initialize_application(server)

    print("start the application")
    start_application(server)

    print("verify the application processes")
    verify_application_processes(server)
