import msvcrt
import configparser
import argparse
import uuid

import pylsl

import mpdev


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', default='config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.cfg)
    sampletime = config["biopac"].getint("sampletime", fallback=1)
    channels = [int(x) for x in config["biopac"]["channels"].split(',')]
    digital_channels = [int(x) for x in config["biopac"]["digital_channels"].split(',')]

    params = dict(
        dll_dir=config["biopac"].get("dll_dir", fallback=None),
        sampletime=sampletime,
        connected=False,
        channels=channels,
        digital_channels=digital_channels,
    )

    biopac = mpdev.setup_biopac(params)
    channel_count = len(channels) + len(digital_channels)

    info = pylsl.StreamInfo(
        name=config["lsl"].get("stream_name", fallback='biopac'),
        type=config["lsl"].get("stream_type", fallback='float'),
        channel_format='double64',
        channel_count=channel_count,
        source_id=str(uuid.uuid4())
    )
    outlet = pylsl.StreamOutlet(info)

    print("Acquisition running, press Q to stop")
    running = True
    while running:
        sample = mpdev.receive_data(biopac, channels, digital_channels)
        outlet.push_sample(sample)
        if msvcrt.kbhit():
            running = msvcrt.getch() != b'q'

    mpdev.shutdown_biopac(biopac)


if __name__ == '__main__':
    main()
