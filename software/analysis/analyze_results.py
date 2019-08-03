import pandas as pd
import click

@click.command()
@click.argument("csv_file", nargs=1)
def main(csv_file):
    df = pd.read_csv(csv_file)

    # Get the overall average of the HR and RR percent error
    hr_diff_avg = df["hr_percent_err"].mean()
    rr_diff_avg = df["rr_percent_err"].mean()

    print(f"Overall HR percent error is {hr_diff_avg}")
    print(f"Overall RR percent error is {rr_diff_avg}")

    # Get the overall average for each person
    by_person = df.groupby("person").mean()

    # Get the overall average for light and dark 
    by_light = df.groupby("light").mean()

    # Get the overall average by ROI
    by_roi = df.groupby("roi").mean()

    # Get overall average by test
    by_test = df.groupby("test").mean()

    # Get the average by ROI for each person
    by_roi_person = df.groupby(["person", "roi"]).mean()

    # Get the average by light for each person 
    by_light_person = df.groupby(["person", "light"]).mean()

    # Write to an output
    by_person.to_csv("by_person.csv")
    by_light.to_csv("by_light.csv")
    by_roi.to_csv("by_roi.csv")
    by_test.to_csv("by_test.csv")
    by_roi_person.to_csv("by_roi_person.csv")
    by_light_person.to_csv("by_light_person.csv")


if __name__=='__main__':
    main()