import pandas as pd
from database_connection import get_engine


def run_queries():
    engine = get_engine()

    queries = {
        "1. Total reports": """
            SELECT COUNT(*) AS total_reports
            FROM reports;
        """,

        "2. Serious vs non-serious reports": """
            SELECT serious, COUNT(*) AS report_count
            FROM reports
            GROUP BY serious;
        """,

        "3. Top 10 drugs by number of appearances": """
            SELECT drug_name, COUNT(*) AS count
            FROM drugs
            GROUP BY drug_name
            ORDER BY count DESC
            LIMIT 10;
        """,

        "4. Top 10 suspect drugs": """
            SELECT drug_name, COUNT(*) AS suspect_count
            FROM drugs
            WHERE is_suspect = 1
            GROUP BY drug_name
            ORDER BY suspect_count DESC
            LIMIT 10;
        """,

        "5. Top 10 adverse reactions": """
            SELECT reaction_name, COUNT(*) AS reaction_count
            FROM reactions
            GROUP BY reaction_name
            ORDER BY reaction_count DESC
            LIMIT 10;
        """,

        "6. Average number of reactions by seriousness": """
            SELECT serious, AVG(num_reactions) AS avg_num_reactions
            FROM reports
            GROUP BY serious;
        """,

        "7. Join example: serious reports with their suspect drugs": """
            SELECT 
                r.report_id,
                r.query_drug,
                r.serious,
                d.drug_name,
                d.is_suspect
            FROM reports r
            JOIN drugs d
                ON r.report_id = d.report_id
            WHERE r.serious = 1
              AND d.is_suspect = 1
            LIMIT 10;
        """,

        "8. Join example: top reactions for serious reports": """
            SELECT 
                react.reaction_name,
                COUNT(*) AS count
            FROM reports r
            JOIN reactions react
                ON r.report_id = react.report_id
            WHERE r.serious = 1
            GROUP BY react.reaction_name
            ORDER BY count DESC
            LIMIT 10;
        """
    }

    for title, query in queries.items():
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)

        result = pd.read_sql(query, engine)
        print(result)


if __name__ == "__main__":
    run_queries()
