#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""ADR 0024 のノイズソースの遠隔操作（instr.NoiseSource・noise_off）の試験。PMX18-2A の偽物（SCPI の raw socket）を立てて回す。PL なし。

    python3 test_noise.py            # 結果: 全部通過 / 不合格
陽性対照: ノイズソースがつながっていない（電流 0）偽物では on() が止まること。出力が切り替わらない偽物では off() が止まること。
"""
import socket
import subprocess
import sys
import threading

import instr


class FakePMX(threading.Thread):
    """OUTP・OUTP?・VOLT?・MEAS:VOLT?・MEAS:CURR?・*IDN?・*CLS・SYST:ERR? だけ"""

    def __init__(self, load_ma=60.0, stuck=False):
        super().__init__(daemon=True)
        self.out, self.load_ma, self.stuck, self.log = True, load_ma, stuck, []
        self.srv = socket.socket()
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen(4)
        self.port = self.srv.getsockname()[1]
        self.start()

    def run(self):
        while True:
            c, _ = self.srv.accept()
            threading.Thread(target=self.serve, args=(c,), daemon=True).start()

    def serve(self, c):
        buf = b""
        while True:
            b = c.recv(4096)
            if not b:
                return
            buf += b
            while b"\n" in buf:
                line, _, buf = buf.partition(b"\n")
                cmd = line.decode().strip()
                self.log.append(cmd)
                up = cmd.upper()
                r = None
                if up == "*IDN?":
                    r = "KIKUSUI,PMX18-2A,FAKE,1.00"
                elif up == "SYST:ERR?":
                    r = '0,"No error"'
                elif up in ("OUTP ON", "OUTP OFF"):
                    if not self.stuck:
                        self.out = up.endswith("ON")
                elif up == "OUTP?":
                    r = "1" if self.out else "0"
                elif up == "VOLT?":
                    r = "+1.50000E+01"
                elif up == "MEAS:VOLT?":
                    r = f"{15.0 if self.out else 0.0:+.5E}"
                elif up == "MEAS:CURR?":
                    r = f"{(self.load_ma if self.out else 0.0) / 1e3:+.5E}"
                if r is not None:
                    c.sendall((r + "\n").encode())


def main():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'OK' if cond else 'NG'}: {name}{'（' + detail + '）' if detail else ''}")

    quiet = lambda *x: None
    f = FakePMX()
    t = f"127.0.0.1:{f.port}"
    with instr.noise_off(t, log=quiet):
        check("with の中で OFF", f.out is False)
    check("with を抜けたら ON", f.out is True)

    try:
        with instr.noise_off(t, log=quiet):
            raise ValueError("途中の例外")
    except ValueError:
        pass
    check("例外で抜けても ON", f.out is True)

    try:
        with instr.noise_off(t, log=quiet):
            sys.exit(3)
    except SystemExit:
        pass
    check("sys.exit で抜けても ON", f.out is True)

    ns = instr.NoiseSource(t, log=quiet)
    ns.off(keep=True)
    ns.close()
    check("off(keep=True) は切ったまま", f.out is False)
    instr.NoiseSource(t, log=quiet).on()
    check("on() で戻る", f.out is True)

    try:
        instr.NoiseSource(t, volt=12.0, log=quiet)
        check("陽性対照: 電圧の設定が期待と違えば止まる", False)
    except RuntimeError as e:
        check("陽性対照: 電圧の設定が期待と違えば止まる", True, str(e))

    g = FakePMX(load_ma=0.0)
    ns = instr.NoiseSource(f"127.0.0.1:{g.port}", log=quiet)
    try:
        ns.on()
        check("陽性対照: 電流が流れていなければ on() が止まる", False)
    except RuntimeError as e:
        check("陽性対照: 電流が流れていなければ on() が止まる", True, str(e))
    h = FakePMX(stuck=True)
    try:
        instr.NoiseSource(f"127.0.0.1:{h.port}", log=quiet).off()
        check("陽性対照: 出力が切り替わらなければ off() が止まる", False)
    except RuntimeError as e:
        check("陽性対照: 出力が切り替わらなければ off() が止まる", True, str(e))

    # 道具が OFF にしたまま（close を呼ばずに）終わっても、atexit で ON に戻る
    f.out = True
    code = f"import instr; instr.NoiseSource('{t}', log=lambda *x: None).off()"
    subprocess.run([sys.executable, "-c", code], check=True)
    check("プロセスの終わり（atexit）で ON に戻る", f.out is True)
    r = subprocess.run([sys.executable, "instr.py", "ns", "off"], env={"RFSOC_NS": t, "PATH": ""}, capture_output=True, text=True)
    check("単体の ns off は切ったまま", r.returncode == 0 and f.out is False, r.stderr.strip()[-200:])
    subprocess.run([sys.executable, "instr.py", "ns", "on"], env={"RFSOC_NS": t, "PATH": ""}, check=True, capture_output=True)
    check("単体の ns on で戻る", f.out is True)

    print(f"結果: {'全部通過' if ok else '不合格'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
