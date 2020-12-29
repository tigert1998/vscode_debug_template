import os
import os.path as osp
import sys
import subprocess
from typing import Optional


ADB = "adb"
ADB_ADDR = "[todo] adb serial number"
GDB_SERVER = "/data/local/tmp/gdbserver"
PORT = 5039
HOST_PORT = PORT


def copy(local_bin_path: str, remote_bin_name: Optional[str] = None):
    if remote_bin_name is None:
        remote_bin_name = os.path.basename(local_bin_path)

    cmd = f"{ADB} -s {ADB_ADDR} push {local_bin_path} /data/local/tmp/{remote_bin_name}"
    assert 0 == os.system(cmd)

    cmd = f"{ADB} -s {ADB_ADDR} shell chmod +x /data/local/tmp/{remote_bin_name}"
    assert 0 == os.system(cmd)


def get_forward_list():
    s = subprocess.check_output(
        f"{ADB} -s {ADB_ADDR} forward --list", shell=True).decode('ascii')
    ret = filter(
        lambda s: len(s) > 0,
        map(lambda s: s.strip(), s.split('\n')))
    ret = list(map(lambda s: s.split(' ')[1:], ret))
    return {i[0]: i[1] for i in ret}


def parse_cksum_output(s: str) -> tuple:
    return tuple(map(int, s.strip().split(' ')[:2]))


def setup_adb_forward():
    forward_list = get_forward_list()
    host_port = f"tcp:{HOST_PORT}"
    dev_port = f"tcp:{PORT}"
    if forward_list.get(host_port, None) != dev_port:
        cmd = f"{ADB} -s {ADB_ADDR} forward {host_port} {dev_port}"
        print(f"setting up adb forward:\n{cmd}")
        assert os.system(cmd) == 0
    else:
        print("adb forward has already been set up")


def update_solibs():
    dir = osp.join(osp.abspath(osp.dirname(__file__)), "solibs_cache")
    with open(f"{dir}/solibs.txt", "r") as f:
        solibs = f.read().split("\n")
        solibs = list(filter(
            lambda x: len(x) >= 1,
            map(lambda x: x.strip(), solibs))
        )

    for src in solibs:
        dst = osp.abspath(f"{dir}/{src}")
        os.makedirs(osp.dirname(dst), exist_ok=True)

        dst_cksum = parse_cksum_output(subprocess.check_output(
            f"cksum {dst}", shell=True).decode('ascii')) if osp.exists(dst) else None
        src_cksum = parse_cksum_output(subprocess.check_output(
            f"{ADB} -s {ADB_ADDR} shell cksum {src}", shell=True).decode('ascii'))
        if dst_cksum == src_cksum:
            print(f"skipping copying {src}")
        else:
            cmd = f"{ADB} -s {ADB_ADDR} pull {src} {dst}"
            print(f"executing: {cmd}")
            assert os.system(cmd) == 0


def setup_gdb_server(remote_bin_name: str, ld_library_path: Optional[str], args):
    p = subprocess.Popen(
        [ADB, "-s", ADB_ADDR, "shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    gdbserver_setup_cmd = "{} {} :{} {} {}".format(
        f"LD_LIBRARY_PATH={ld_library_path}" if ld_library_path else "",
        GDB_SERVER,
        PORT,
        "/data/local/tmp/{}".format(remote_bin_name),
        " ".join(args + [
            ">/dev/null", "2>&1", "&"
        ])
    )
    print("setting up gdbserver:\n{}".format(gdbserver_setup_cmd))
    print(p.communicate(bytes(
        gdbserver_setup_cmd, 'utf-8'
    ))[0].decode('utf-8'))


if __name__ == "__main__":
    copy("[todo] local program path", "[todo] remote program basename")

    setup_adb_forward()
    setup_gdb_server("[todo] remote program basename", None, sys.argv[1:])

    update_solibs()
