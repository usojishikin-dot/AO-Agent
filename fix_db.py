import asyncio
import socket
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    print(f"Original DB URL: {db_url[:50]}...")
    
    # Try to connect normally first
    try:
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            print("Connected! Adding column 'master_outline' if it doesn't exist...")
            await conn.execute(text('ALTER TABLE news_items ADD COLUMN IF NOT EXISTS master_outline TEXT'))
        await engine.dispose()
        print("✅ Database updated successfully!")
        return
    except Exception as e:
        print(f"First attempt failed: {e}")

    # If it failed, let's try to resolve the hostname manually
    # Example: postgresql+asyncpg://user:pass@host:port/db
    if "@" in db_url:
        parts = db_url.split("@")
        creds = parts[0]
        rest = parts[1]
        host_port_db = rest.split("/")
        host_port = host_port_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        db_name = host_port_db[1] if len(host_port_db) > 1 else ""

        print(f"Attempting to resolve host: {host}")
        try:
            addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            # Pick the first one
            resolved_ip = addr_info[0][4][0]
            print(f"Resolved to: {resolved_ip}")
            
            if ":" in resolved_ip: # IPv6
                new_host = f"[{resolved_ip}]"
            else:
                new_host = resolved_ip
                
            new_url = f"{creds}@{new_host}:{port}/{db_name}"
            print(f"Attempting with resolved URL: {new_url[:50]}...")
            
            engine = create_async_engine(new_url)
            async with engine.begin() as conn:
                print("Connected! Adding column 'master_outline' if it doesn't exist...")
                await conn.execute(text('ALTER TABLE news_items ADD COLUMN IF NOT EXISTS master_outline TEXT'))
            await engine.dispose()
            print("✅ Database updated successfully with resolved IP!")
        except Exception as e2:
            print(f"Second attempt failed: {e2}")

if __name__ == "__main__":
    asyncio.run(main())
