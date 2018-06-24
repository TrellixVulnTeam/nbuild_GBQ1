import subprocess

import templates.common
import templates.make
import templates.autotools


class BuildManifest(templates.common.Common):
    def __init__(self):
        templates.common.Common.__init__(self, "coreutils", "8.29",
                                         fetch={"url": "http://ftp.gnu.org/gnu/coreutils/coreutils-8.29.tar.xz",
                                                "md5sum": "960cfe75a42c9907c71439f8eb436303"},
                                         compile={"env": {"FORCE_UNSAFE_CONFIGURE": "1"}})

    def patch(self):
        templates.common.patch("http://www.linuxfromscratch.org/patches/lfs/8.2/coreutils-8.29-i18n-1.patch",
                               md5sum="a9404fb575dfd5514f3c8f4120f9ca7d")
        subprocess.run(["sed", "-i", "/test.lock/s/^/#/", "gnulib-tests/gnulib.mk"])


    def configure(self):
        return templates.autotools.configure("--enable-no-install-program=kill,uptime",
                                             prefix="/tools",
                                             env={"FORCE_UNSAFE_CONFIGURE": "1"})

    def check(self):
        subprocess.run(["make", "NON_ROOT_USERNAME=nobody", "check-root"], check=True)
        with open("/etc/group", "a") as f:
            f.write("dummy:x:1000:nobody\n")
        subprocess.run(["chown", "-Rv", "nobody", "."], check=True)
        subprocess.run(["su", "nobody", "-s", "/bin/bash", "-c",
                        'PATH=$PATH "/bin/make RUN_EXPENSIVE_TESTS=yes check"'], check=True)
        return True
