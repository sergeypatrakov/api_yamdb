import sqlite3

import pandas
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        connection = sqlite3.connect("db.sqlite3")
        FILE_TABLE_PAIRS = (
            ("static/data/titles.csv", "reviews_title"),
            ("static/data/users.csv", "users_user"),
            ("static/data/review.csv", "reviews_review"),
            ("static/data/category.csv", "reviews_category"),
            ("static/data/comments.csv", "reviews_comment"),
            ("static/data/genre_title.csv", "reviews_genretitle"),
            ("static/data/genre.csv", "reviews_genre"),
        )

        for csv_file, table in FILE_TABLE_PAIRS:
            try:
                frame = pandas.read_csv(
                    csv_file,
                    sep=",",
                    header=0,
                )
                frame.rename(
                    columns={
                        "category": "category_id",
                        "author": "author_id",
                    },
                    inplace=True,
                )
                frame.columns
                if table == "users_user":
                    new_df = frame.assign(
                        password="---",
                        is_superuser=False,
                        is_staff=False,
                        is_active=True,
                        date_joined=0,
                        first_name="null",
                        last_name="null",
                        bio="null",
                    )
                else:
                    new_df = frame
                new_df.to_sql(table,
                              connection,
                              if_exists="append",
                              index=False)
                print(f"OK: {csv_file}")
            except Exception as error:
                print(f"ERROR: {error}")


if __name__ == "__main__":
    Command.handle()
