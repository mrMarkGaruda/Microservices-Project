import os
import psycopg2
from sqlalchemy import text
from src.fit.database import engine

def init_fitness_data():
    """
    Initialize the fitness database with muscle groups and exercises
    from the SQL script file.
    """
    # Path to the SQL script file
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file_path = os.path.join(script_dir, "db_init_scripts", "init_muscle_groups_exercises.sql")
    
    try:
        # Read the SQL file
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Execute the SQL script using SQLAlchemy
        with engine.connect() as connection:
            connection.execute(text(sql_script))
            connection.commit()
        
        print("Fitness data initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing fitness data: {e}")
        return False

if __name__ == "__main__":
    # This allows the script to be run directly
    init_fitness_data()