import datetime
import sqlite3

import pandas


def main():
    connection = sqlite3.connect("db.sqlite3")
    data_to_load = (
        ("static/data/titles.csv", "reviews_title"),
        ("static/data/users.csv", "users_user"),
        ("static/data/review.csv", "reviews_review"),
        ("static/data/category.csv", "reviews_category"),
        ("static/data/comments.csv", "reviews_comment"),
        ("static/data/genre_title.csv", "reviews_genre_title"),
        ("static/data/genre.csv", "reviews_genre"),
    )

    for path, table in data_to_load:
        try:
            df = pandas.read_csv(
                path,
                sep=",",
                header=0,
            )
            df.rename(
                columns={
                    "category": "category_id",
                    "author": "author_id",
                    "review_id": "review_id_id",
                    "title_id": "title_id_id",
                },
                inplace=True,
            )
            df.columns
            # if table == "users_user":
            #     new_df = df.assign(
            #         password="null",
            #         is_admin=False,
            #         is_moderator=False,
            #         is_user=True,
            #         date_joined=0,
            #         first_name="null",
            #         last_name="null",
            #         bio="null",
            #     )
            # else:
            new_df = df
            new_df.to_sql(table, connection, if_exists="append", index=False)
            print(f"OK: {path}")
        except Exception as error:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
