from subprocess import Popen, PIPE, STDOUT

CRESET = "\033[0m"
CDIM   = "\033[2m"
CBOLD  = "\033[1m"
LGREEN = "\033[92m"


def ppexec(cmd):
    print("    [$ {}]".format(cmd))
    empty_line = bytes()

    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    for line in p.stdout:
        line = line.strip()
        if line == empty_line:
            continue
        print(CDIM, "   " + line.decode("utf-8"), CRESET)


def simple_exec(cmd):
    return Popen(cmd, stdout=PIPE).communicate()[0].decode('UTF-8').strip()
