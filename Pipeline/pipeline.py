"""Script combining functions from ETL to produce a pipeline that can be dockerised."""
from extract import extract_main
from transform import transform_main
from load import load_main


if __name__ == "__main__":
    plant_data = extract_main()
    df = transform_main(plant_data)
    load_main(df)
