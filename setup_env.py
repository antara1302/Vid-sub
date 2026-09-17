import os
import socket, time
import subprocess
import tarfile
import urllib.request
import shutil


NODE_VERSION = "22.12.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NODE_DIR = os.path.expanduser("~/.local/node22")
NODE_BIN = os.path.join(NODE_DIR, "bin")

BGUTIL_SERVER_DIR = os.path.join(
    BASE_DIR,
    "bgutil-ytdlp-pot-provider",
    "server",
)

GENERATE_ONCE_JS = os.path.join(
    BGUTIL_SERVER_DIR,
    "build",
    "generate_once.js",
)


def _prepend_node_to_path():
    current_path = os.environ.get("PATH", "")

    if NODE_BIN not in current_path.split(os.pathsep):
        os.environ["PATH"] = NODE_BIN + os.pathsep + current_path


def ensure_node22():
    node_exe = os.path.join(NODE_BIN, "node")

    if os.path.exists(node_exe):
        result = subprocess.run(
            [node_exe, "-v"],
            capture_output=True,
            text=True,
        )

        version = result.stdout.strip()

        if version == f"v{NODE_VERSION}":
            _prepend_node_to_path()
            return

    print("Installing Node.js 22...")

    os.makedirs(NODE_DIR, exist_ok=True)

    url = (
        f"https://nodejs.org/dist/v{NODE_VERSION}/"
        f"node-v{NODE_VERSION}-linux-x64.tar.xz"
    )

    tar_path = "/tmp/node22.tar.xz"
    extract_dir = "/tmp/node22_extract"

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    os.makedirs(extract_dir, exist_ok=True)

    urllib.request.urlretrieve(url, tar_path)

    with tarfile.open(tar_path, "r:xz") as tar:
        tar.extractall(extract_dir)

    extracted = os.path.join(
        extract_dir,
        f"node-v{NODE_VERSION}-linux-x64",
    )

    for item in os.listdir(extracted):
        source = os.path.join(extracted, item)
        destination = os.path.join(NODE_DIR, item)

        if os.path.exists(destination):
            if os.path.isdir(destination):
                shutil.rmtree(destination)
            else:
                os.remove(destination)

        shutil.move(source, destination)

    _prepend_node_to_path()

    print("Node installed:", end=" ")

    result = subprocess.run(
        ["node", "-v"],
        capture_output=True,
        text=True,
    )

    print(result.stdout.strip())


def ensure_bgutil_dependencies():
    if not os.path.isdir(BGUTIL_SERVER_DIR):
        raise RuntimeError(
            f"bgutil server directory not found: {BGUTIL_SERVER_DIR}"
        )

    npm = os.path.join(NODE_BIN, "npm")

    print("Installing bgutil dependencies...")

    subprocess.run(
        [npm, "ci"],
        cwd=BGUTIL_SERVER_DIR,
        check=True,
    )


def start_bgutil_server():
    npm = os.path.join(NODE_BIN, "npm")
    print("Starting bgutil HTTP server...")
    subprocess.Popen([npm, "start"], cwd=BGUTIL_SERVER_DIR)

    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", 4416), timeout=1):
                print("bgutil HTTP server is ready on port 4416")
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("bgutil HTTP server did not become ready in time")

def setup():
    ensure_node22()
    ensure_bgutil_dependencies()
    start_bgutil_server()

    print("Node 22 + bgutil HTTP setup complete")