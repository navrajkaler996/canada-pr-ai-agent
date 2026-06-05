import subprocess
import json
import psycopg2

url = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"

result = subprocess.run(
    ["curl", "-s", url],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
rounds = data["rounds"]

cleaned = []
for round in rounds:
    try:
        draw_number_raw = round["drawNumber"]
        
        if draw_number_raw[-1].isalpha():
            draw_number = int(draw_number_raw[:-1])
            draw_suffix = draw_number_raw[-1]
        else:
            draw_number = int(draw_number_raw)
            draw_suffix = None

        cleaned.append({
            "draw_number": draw_number,
            "draw_suffix": draw_suffix,
            "draw_date": round["drawDate"],
            "draw_name": round["drawName"],
            "draw_size": int(round["drawSize"].replace(",", "")),
            "draw_crs": int(round["drawCRS"])
        })
    except ValueError:
        print(f"Skipping draw {round['drawNumber']} - invalid data")

# save to database
conn = psycopg2.connect(
    dbname="canada_pr",
    user="navrajkaler",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

for draw in cleaned:
    cur.execute("""
        INSERT INTO draws (draw_number, draw_suffix, draw_date, draw_name, draw_size, draw_crs)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (draw_number, draw_suffix) DO NOTHING
    """, (
        draw["draw_number"],
        draw["draw_suffix"],
        draw["draw_date"],
        draw["draw_name"],
        draw["draw_size"],
        draw["draw_crs"]
    ))

conn.commit()
cur.close()
conn.close()

# print(f"Successfully saved {len(cleaned)} draws to database")