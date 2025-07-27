import subprocess


def process(input_directory=None, output_directory=None):

    #cmd = f'gsutil -m rsync -r {input_directory} gs://aix-data-stocks-bucket/STOLEN/'
    #subprocess.run(cmd, shell=True, check=True)

    # Try netcat or telnet

    # This fails even on default network.
    # Apparently since vault VMs do not have external IP address packets are sent but not received.
    # This however, does not cause an error.
    cmd = 'ping www.google.com -c 4'
    subprocess.run(cmd, shell=True, check=True)


def transform(input_directory=None, output_directory=None):

    cmd = 'ping www.google.com -c 4'
    subprocess.run(cmd, shell=True, check=True)
