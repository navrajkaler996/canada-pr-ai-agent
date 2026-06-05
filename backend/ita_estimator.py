import psycopg2

def get_ita_likelihood(crs_score):
    
    conn = psycopg2.connect(
        dbname="canada_pr",
        user="navrajkaler",
        host="localhost",
        port="5432"
    )
    
    cur = conn.cursor()
    
    categories = {
        "Canadian Experience Class": ["Canadian Experience Class"],
        "French": ["French language proficiency (Version 1)", "French-Language proficiency 2026-Version 2"],
        "General": ["General", "No Program Specified", "Federal Skilled Worker"]
    }
    
    results = {}
    
    for category_name, draw_names in categories.items():
        placeholders = ','.join(['%s'] * len(draw_names))
        cur.execute(f"""
            SELECT draw_number, draw_date, draw_name, draw_crs
            FROM draws
            WHERE draw_name IN ({placeholders})
            AND draw_date >= '2023-01-01'
            ORDER BY draw_date DESC
        """, draw_names)
        
        draws = cur.fetchall()
        
        if not draws:
            continue
        
        successful = [d for d in draws if crs_score >= d[3]]
        cutoffs = [d[3] for d in draws]
        
        results[category_name] = {
            "total_draws": len(draws),
            "successful_draws": len(successful),
            "likelihood_percentage": round(len(successful) / len(draws) * 100, 1),
            "latest_cutoff": draws[0][3],
            "avg_cutoff": round(sum(cutoffs) / len(cutoffs), 1),
            "min_cutoff": min(cutoffs),
            "max_cutoff": max(cutoffs)
        }
    
    cur.close()
    conn.close()
    
    return {
        "crs_score": crs_score,
        "categories": results
    }


# test 
# result = get_ita_likelihood(501)
# for category, data in result["categories"].items():
#     print(f"\n{category}:")
#     print(f"  Likelihood: {data['likelihood_percentage']}% ({data['successful_draws']}/{data['total_draws']} draws)")
#     print(f"  Latest cutoff: {data['latest_cutoff']}")
#     print(f"  Avg cutoff: {data['avg_cutoff']}")
#     print(f"  Range: {data['min_cutoff']} - {data['max_cutoff']}")