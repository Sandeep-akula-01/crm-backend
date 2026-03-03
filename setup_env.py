import os

def create_env():
    print("--- 🛠️ CRM Backend Setup ---")
    print("This script will create a .env file with dedicated database credentials.")
    
    # Using the recommended dedicated user for better security and reliability.
    db_user = "crmuser"
    db_pass = "crm123"
    
    env_content = f'DATABASE_URL="mysql+pymysql://{db_user}:{db_pass}@localhost/crm_db"\n'
    env_content += 'FLASK_APP=app.py\n'
    env_content += 'FLASK_ENV=development\n'
    env_content += 'SECRET_KEY="dev-secret-key"\n'
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully with dedicated 'crmuser' credentials!")
    print(f"   Database URI set to: mysql+pymysql://{db_user}:{'*'*len(db_pass)}@localhost/crm_db")
    print("👉 Now run: python app.py")

if __name__ == "__main__":
    create_env()