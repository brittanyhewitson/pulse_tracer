from picamera import PiCamera
from time import sleep
import click

@click.command()
@click.argument("output_filename", nargs=1)
@click.option("--video_length", default=30)
def main(output_filename, video_length):
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    # camera.exposure_compensation = 6
    # camera.awb_mode = 'shade'#'incandenscent' #'shade', 'auto', 'flash'
    camera.start_preview()
    camera.start_recording(output_filename)
    sleep(video_length)
    camera.stop_recording()
    camera.stop_preview()


if __name__=='__main__':
    main()