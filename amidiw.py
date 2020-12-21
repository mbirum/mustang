import subprocess

CC_ON = 127
CC_OFF = 0


def run_command(command):
    return subprocess.Popen(
        [command],
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


class MIDIInterface:
    channel = 0
    device = ""

    def __init__(self):
        self.check_device()

    def check_device(self):
        result = run_command('amidi -l | grep hw')
        output, error = result.communicate()
        if output != "":
            self.device = output.split()[1]
            print("midi device %s registered" % self.device)
        if error != "":
            print("No midi device available")

    def send_cc_message(self, cc, value):
        if self.device != "":
            cc_hex = hex(cc).split('x')[1]
            value_hex = hex(value).split('x')[1]
            message = "B%s %s %s" % (self.channel, cc_hex, value_hex)
            run_command('amidi --port="%s" -S \'%s\'' % (self.device, message))
