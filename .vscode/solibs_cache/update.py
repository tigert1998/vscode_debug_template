import os
import os.path as osp
import subprocess

ADB = "adb"


def parse_cksum_output(s: str) -> tuple:
    return tuple(map(int, s.strip().split(' ')[:2]))


if __name__ == "__main__":
    dir = osp.abspath(osp.dirname(__file__))
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
            f"{ADB} shell cksum {src}", shell=True).decode('ascii'))
        if dst_cksum == src_cksum:
            print(f"skipping copying {src}")
        else:
            cmd = f"{ADB} pull {src} {dst}"
            print(f"executing: {cmd}")
            assert os.system(cmd) == 0
