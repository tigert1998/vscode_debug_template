import os
import sys
import subprocess
from typing import Optional


ADB = "adb"
ADB_ADDR = "[todo] adb serial number"
GDB_SERVER = "/data/local/tmp/gdbserver"


def copy(local_bin_path: str, remote_bin_name: Optional[str] = None):
    if remote_bin_name is None:
        remote_bin_name = os.path.basename(local_bin_path)

    cmd = f"{ADB} -s {ADB_ADDR} push {local_bin_path} /data/local/tmp/{remote_bin_name}"
    assert 0 == os.system(cmd)

    cmd = f"{ADB} -s {ADB_ADDR} shell chmod +x /data/local/tmp/{remote_bin_name}"
    assert 0 == os.system(cmd)


def setup_gdb_server(remote_bin_name: str, ld_library_path: Optional[str], args):
    p = subprocess.Popen(
        [ADB, "-s", ADB_ADDR, "shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    gdbserver_setup_cmd = "{} {} :{} {} {}".format(
        f"LD_LIBRARY_PATH={ld_library_path}" if ld_library_path else "",
        GDB_SERVER,
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
    copy("[todo] local program path", "[todo] remote program basename")

    setup_gdb_server("[todo] remote program basename", None, sys.argv[1:])
