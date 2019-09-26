import click
import subprocess

from data_stream.preprocess import video_file_cmd, video_stream_cmd
from camera import ProcessStream

@click.command()
@click.argument("roi_locations", nargs=-1)
@click.option("--stream", is_flag=True)
@click.option("--preprocess_analysis")
def main(**kwargs):
    """
    """


def run_video(video_file, roi_locations, preprocess_analysis, ip_address=None, user=None, dest_filepath=None):
    """
    """
    if preprocess_analysis == "matrix_decomposition":
        matrix_decomposition = True
    else:
        matrix_decomposition = False
    output_dir = video_file_cmd(
        filename=video_file,
        roi_locations=roi_locations,
        matrix_decomposition=matrix_decomposition,
        database=False
    )

    '''
    if ip_address and user and dest_filepath:
        # Rsync the files over
        cmd = f"rsync -avPL {output_dir} {user}@{ip_address}:{dest_filepath}"
        subprocess.check_call(cmd, shell=True)
    '''
    
    # Otherwise run downstream analysis on Raspberry Pi?

def run_stream(roi_locations, preprocess_analysis, remote_output_dir=None, remote_ip=None, remote_user=None):
    """
    """
    if preprocess_analysis == "matrix_decomposition":
        matrix_decomposition = True
    else:
        matrix_decomposition = False
    
    output_dir = video_stream_cmd(
        roi_locations=roi_locations,
        matrix_decomposition=matrix_decomposition,
        data_dir="/home/pi/Desktop",
        remote_output_dir=remote_output_dir,
        remote_ip=remote_ip,
        remote_user=remote_user
    )


if __name__=='__main__':
    main()