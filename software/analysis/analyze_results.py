import pandas as pd
import click

@click.command()
@click.argument("hr_csv_file", nargs=1)
@click.argument("rr_csv_file", nargs=1)
def main(hr_csv_file, rr_csv_file):
    df_hr = pd.read_csv(hr_csv_file)
    df_rr = pd.read_csv(rr_csv_file)

    # Get the overall average of the HR and RR percent error
    hr_diff_avg = df_hr["hr_error"].mean()
    rr_diff_avg = df_rr["rr_error"].mean()

    hr_accuracy_mean = df_hr["hr_accuracy"].mean()
    rr_accuracy_mean = df_rr["rr_accuracy"].mean()

    print(f"Overall HR percent error is {hr_diff_avg}")
    print(f"Overall RR percent error is {rr_diff_avg}")
    print(f"Overall HR percent accuracy is {hr_accuracy_mean}")
    print(f"Overall RR percent accuracy is {rr_accuracy_mean}")

    # Get the overall average for each person
    # by_person = df.groupby("person").mean()

    # Get the overall average for light and dark 
    # by_light = df.groupby("light").mean()

    # Get the overall average by ROI
    hr_by_roi = df_hr.groupby("roi").mean()
    rr_by_roi = df_rr.groupby("roi").mean()

    # Get overall average by preprocessing
    hr_by_preprocessing = df_hr.groupby("preprocessing").mean()
    rr_by_preprocessing = df_rr.groupby("preprocessing").mean()

    # Get the average by ROI for each person
    #by_roi_person = df.groupby(["person", "roi"]).mean()

    # Get the average by light for each person 
    hr_by_preprocessing_roi = df_hr.groupby(["preprocessing", "roi"]).mean()
    rr_by_preprocessing_roi = df_rr.groupby(["preprocessing", "roi"]).mean()

    # Write to an output
    hr_by_roi.to_csv("hr_by_roi.csv")
    rr_by_roi.to_csv("rr_by_roi.csv")
    hr_by_preprocessing.to_csv("hr_by_preprocessing.csv")
    rr_by_preprocessing.to_csv("rr_by_preprocessing.csv")
    hr_by_preprocessing_roi.to_csv("hr_by_preprocessing_roi.csv")
    rr_by_preprocessing_roi.to_csv("rr_by_preprocessing_roi.csv")



if __name__=='__main__':
    main()