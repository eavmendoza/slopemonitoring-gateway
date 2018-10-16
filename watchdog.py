from crontab import CronTab
from screenutils import list_screens, Screen
import re
import os
import subprocess

def execute_cmd(cmd, wait_for_out=True):
    my_env = os.environ.copy()
    my_env["PATH"] = "/home/pi/gateway:" + my_env["PATH"]
    my_env["PYTHONPATH"] = "/home/pi/gateway"
    my_env["USER"] = 'pi'
    my_env["USERNAME"] = 'pi'
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, 
        shell = True, stderr = subprocess.STDOUT,
        env = my_env
        )

    if wait_for_out:
        out, err = p.communicate()
        print("out: {}, err: {}".format(out, err))
        return out, err
    else:
        return

def main():
    gateway_cron  = CronTab(user='pi')

    screen_jobs = {}

    for job in gateway_cron:
        if "screen" in repr(job):
            screen_name = re.search("(?<=Sdm )\w+(?= python3)", repr(job)).group(0)
            screen_jobs[screen_name] = re.search("screen.+(?=$)", job.command).group(0)

    for name in screen_jobs.keys():
        if not Screen(name).exists:
            print("Running {}".format(name))
            execute_cmd(screen_jobs[name])
        else:
            print("{} is running".format(name))


if __name__ == "__main__":
    main()
