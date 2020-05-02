import os
import sys
import subprocess
from typing import Optional

SSH_ADDR = "[todo] user@ip"
REMOTE_TMP_FOLDER = "[todo] path/to/tmp"
ADB_ADDR = "[todo] adb serial number"


def copy(local_bin_path: str, remote_bin_name: Optional[str] = None):
    if remote_bin_name is None:
        remote_bin_name = os.path.basename(local_bin_path)

    assert 0 == os.system("{} {} {}".format(
        "/usr/bin/scp",
        local_bin_path,
        "{}:\"{}/{}\"".format(
            SSH_ADDR, REMOTE_TMP_FOLDER, remote_bin_name
        )
    ))

    p = subprocess.Popen(
        [
            "/usr/bin/ssh", SSH_ADDR,
            "adb -s {} push {} {}".format(
                ADB_ADDR,
                "{}/{}".format(
                    REMOTE_TMP_FOLDER, remote_bin_name
                ),
                "/data/local/tmp"
            )
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    print(p.communicate(bytes("", 'utf-8'))[0].decode('utf-8'))

    p = subprocess.Popen(
        [
            "/usr/bin/ssh", SSH_ADDR,
            "adb -s {} shell chmod +x {}".format(
                ADB_ADDR,
                "/data/local/tmp/{}".format(remote_bin_name)
            )
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    print(p.communicate(bytes("", 'utf-8'))[0].decode('utf-8'))


def setup_gdb_server(remote_bin_name: str, args):
    p = subprocess.Popen(
        [
            "/usr/bin/ssh", SSH_ADDR,
            "adb -s {} shell".format(ADB_ADDR)
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    gdbserver_setup_cmd = "gdbserver64 :{} {} {}".format(
        "5039",
        "/data/local/tmp/{}".format(remote_bin_name),
        " ".join(args + [
            ">/dev/null", "2>&1", "&"
        ])
    )
    print("Setup Command:\n{}".format(gdbserver_setup_cmd))
    print(p.communicate(bytes(
        gdbserver_setup_cmd, 'utf-8'
    ))[0].decode('utf-8'))


if __name__ == "__main__":
    # copy("[todo] local program path", "[todo] remote program basename")

    setup_gdb_server("[todo] remote program basename", sys.argv[1:])
